"""Results guard of scripts/runpod/pod.py (2026-11-18, audit P0). No RunPod call: a fake pod is a local HTTP server on a temp publish
folder, the pod record points at it, and `delete` always runs with --dry-run (it would only call the API after every check passed).
    .venv/bin/python tools/tests/test_pod_guard.py      -> N/N PASS"""
import json, os, shutil, subprocess, sys, tempfile, threading, functools, http.server

SKILL = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
POD, MAN = os.path.join(SKILL, "scripts/runpod/pod.py"), os.path.join(SKILL, "scripts/runpod/manifest.py")

def main():
    tmp = tempfile.mkdtemp(prefix="podguard_"); pub = os.path.join(tmp, "pub", "KEY"); os.makedirs(os.path.join(pub, "jobs", "007"))
    pods, dest = os.path.join(tmp, "pods"), os.path.join(tmp, "local")
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=os.path.join(tmp, "pub")))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    os.makedirs(pods); json.dump({"id": "fakepod", "status_url": "http://127.0.0.1:%d/KEY/status.json" % srv.server_address[1], "episode": "episodes/_x", "script": "lookdev_pod.sh", "expect": ["lock.tar", "lock.json"]}, open(os.path.join(pods, "fakepod.json"), "w"))
    env = dict(os.environ, RICKCLIPS_PODS_DIR=pods)
    run = lambda *a: subprocess.run([sys.executable, POD, *a, "--dest", dest], capture_output=True, text=True, env=env)
    man = lambda: subprocess.run([sys.executable, MAN, pub, "t"], capture_output=True, text=True, check=True)
    W = lambda p, b: open(os.path.join(pub, p), "wb").write(b)
    res = []
    def t(name, ok, info=""): res.append((name, ok)); print("%s  %s  %s" % ("PASS" if ok else "FAIL", name, info))
    try:
        r = run("delete", "fakepod", "--dry-run"); t("no manifest on the pod -> delete refused", r.returncode == 1 and "REFUSED" in r.stdout)
        W("jobs/007/look.png", b"x" * 5000); man()
        r = run("delete", "fakepod", "--dry-run"); t("expected lock.tar/lock.json missing -> refused", r.returncode == 1 and "expected results not produced" in r.stdout)
        W("lock.tar", os.urandom(300000)); W("lock.json", b'{"lock_version":2}'); man()
        r = run("delete", "fakepod", "--dry-run"); t("results not fetched -> refused", r.returncode == 1 and "FETCH_RECEIPT" in r.stdout)
        r = run("fetch", "fakepod"); t("fetch downloads and checks every file", r.returncode == 0 and os.path.exists(os.path.join(dest, "lock.tar")) and json.load(open(os.path.join(dest, "FETCH_RECEIPT.json")))["files"] == 3, r.stdout.strip()[-120:])
        r = run("delete", "fakepod", "--dry-run"); t("all fetched and verified -> delete allowed", r.returncode == 0 and "would terminate" in r.stdout)
        W("jobs/007/new.png", b"y" * 100); man()
        r = run("delete", "fakepod", "--dry-run"); t("new result on the pod after the fetch -> refused", r.returncode == 1 and "manifest changed" in r.stdout)
        run("fetch", "fakepod"); open(os.path.join(dest, "lock.tar"), "r+b").write(b"Z")
        r = run("delete", "fakepod", "--dry-run"); t("local file corrupted -> refused (sha256 re-checked)", r.returncode == 1 and "checksum mismatch locally: lock.tar" in r.stdout)
        os.remove(os.path.join(dest, "lock.tar"))
        r = run("delete", "fakepod", "--dry-run"); t("local file deleted -> refused", r.returncode == 1 and "missing locally: lock.tar" in r.stdout)
        r = run("fetch", "fakepod"); r = run("delete", "fakepod", "--dry-run"); t("re-fetch repairs -> allowed", r.returncode == 0)
        srv.shutdown(); srv.server_close()
        r = run("delete", "fakepod", "--dry-run"); t("pod unreachable -> refused without an explicit reason", r.returncode == 1 and "not reachable" in r.stdout)
        r = run("delete", "fakepod", "--dry-run", "--accept-unreachable", "test: pod gone"); t("explicit --accept-unreachable is logged", r.returncode == 0 and "accept-unreachable: test: pod gone" in r.stdout)
        r = subprocess.run([sys.executable, POD, "delete", "nosuchpod", "--dry-run"], capture_output=True, text=True, env=env); t("unknown pod (no record) -> refused", r.returncode == 1 and "no local record" in r.stdout)
        t("local results never deleted by the guard", os.path.exists(os.path.join(dest, "lock.json")) and os.path.exists(os.path.join(dest, "FETCH_RECEIPT.json")))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    n = sum(ok for _, ok in res); print("%d/%d PASS" % (n, len(res))); return 0 if n == len(res) else 1

if __name__ == "__main__":
    sys.exit(main())

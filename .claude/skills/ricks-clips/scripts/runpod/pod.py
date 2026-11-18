"""RunPod control for RicksClips GPU renders (GraphQL API https://api.runpod.io/graphql), 2026-11-17; results guard 2026-11-18.
    python scripts/runpod/pod.py create <episode path from the skill root> [--gpu "NVIDIA GeForce RTX 4090"] [--branch <git branch>] [--script X.sh]
                                        [--cloud ALL|COMMUNITY|SECURE] [--volume-gb 20] [--max-hours 3] [--scale 1] [--post v3] [--allow-cpu] [--diag]
    python scripts/runpod/pod.py status <podId>
    python scripts/runpod/pod.py fetch  <podId> [--dest <dir>]      download every file of the pod's manifest.json, check each sha256, write FETCH_RECEIPT.json
    python scripts/runpod/pod.py verify <podId> [--dest <dir>]      the delete checks without deleting (exit 0 = safe to delete)
    python scripts/runpod/pod.py delete <podId> [--dest <dir>] [--dry-run]
    python scripts/runpod/pod.py resume <podId>                      restart a pod its watchdog stopped (GPU billing starts again) to fetch its results
    python scripts/runpod/pod.py list                                local pod records and their fetch state
    python scripts/runpod/pod.py balance

RESULTS GUARD (audit 2026-11-18, P0: the stage-8 lock was lost when its pod was deleted before anything was downloaded):
  * every pod publishes <pub>/manifest.json (scripts/runpod/manifest.py): path, size, sha256 of each result;
  * `delete` REFUSES unless (1) the pod's live manifest.json was read, (2) it holds every expected result of that pod's script
    (lookdev: lock.tar + lock.json; render: final.mp4), (3) a local FETCH_RECEIPT.json was written for exactly that manifest
    (same sha256 of the manifest bytes), and (4) every listed file is present locally with the same size and sha256 NOW (re-hashed).
  * overrides are explicit and logged, never defaults: --accept-incomplete "<reason>" (an expected result was never produced),
    --accept-unreachable "<reason>" (the pod no longer answers: its results cannot be fetched), --forget-unknown "<reason>" (no local record).
  * nothing here ever deletes a local file. The pod watchdogs STOP the pod (volume kept) instead of removing it.
Records (status URL, publish key: a capability URL, so they stay OUT of git) live in $RICKCLIPS_PODS_DIR (default ~/.ricksclips/pods).
Auth: header "Authorization: Bearer $RUNPOD_API_KEY". In Claude Code Web the key is a Network Secret for api.runpod.io that the
proxy injects (RUNPOD_API_KEY may then be the placeholder 'proxy-injected')."""
import hashlib, json, os, sys, secrets, time, urllib.request

API = "https://api.runpod.io/graphql"
REPO = "https://github.com/shelohermituss-hub/Ricks-clips-.git"
SKILL = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PODS = os.path.expanduser(os.environ.get("RICKCLIPS_PODS_DIR", "~/.ricksclips/pods"))
EXPECT = {"lookdev_pod.sh": ["lock.tar", "lock.json"], "render_pod.sh": ["final.mp4"], "gpu_diag.sh": []}

def gql(q, v=None):
    req = urllib.request.Request(API, json.dumps({"query": q, "variables": v or {}}).encode(), {"content-type": "application/json", "Authorization": "Bearer " + os.environ.get("RUNPOD_API_KEY", "proxy-injected")})
    r = json.load(urllib.request.urlopen(req, timeout=120))
    if r.get("errors"): raise SystemExit("RunPod API error: %s" % json.dumps(r["errors"])[:800])
    return r["data"]

def sha256_file(p, bs=1 << 20):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(bs), b""): h.update(b)
    return h.hexdigest()

def rec_path(pid): return os.path.join(PODS, pid + ".json")
def load_rec(pid):
    p = rec_path(pid)
    return json.load(open(p)) if os.path.exists(p) else None
def save_rec(r): os.makedirs(PODS, exist_ok=True); json.dump(r, open(rec_path(r["id"]), "w"), indent=1)
def base_url(r): return r["status_url"].rsplit("/", 1)[0] + "/"
def default_dest(r): return os.path.join(SKILL, r.get("episode", "episodes/_pods"), "out", "pods", r["id"])

def get(url, timeout=60):
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "RicksClips-pod/1.0"}), timeout=timeout)

def live_manifest(r):
    """(manifest dict, sha256 of its bytes) or (None, reason)"""
    try: b = get(base_url(r) + "manifest.json", 30).read()
    except Exception as e: return None, "manifest.json not reachable: %s" % e
    try: return json.loads(b), hashlib.sha256(b).hexdigest()
    except Exception as e: return None, "manifest.json unreadable: %s" % e

def fetch(r, dest):
    m, msha = live_manifest(r)
    if m is None: raise SystemExit("FETCH FAILED: " + msha)
    os.makedirs(dest, exist_ok=True); got, bad = [], []
    for f in m["files"]:
        out = os.path.join(dest, *f["path"].split("/"))
        if os.path.exists(out) and os.path.getsize(out) == f["size"] and sha256_file(out) == f["sha256"]: got.append(f["path"]); continue
        os.makedirs(os.path.dirname(out), exist_ok=True); tmp = out + ".part"; h = hashlib.sha256(); n = 0
        with get(base_url(r) + urllib.request.quote(f["path"]), 600) as s, open(tmp, "wb") as o:
            for b in iter(lambda: s.read(1 << 20), b""): o.write(b); h.update(b); n += len(b)
        if n != f["size"] or h.hexdigest() != f["sha256"]: bad.append(f["path"]); os.remove(tmp); continue
        os.replace(tmp, out); got.append(f["path"])
    open(os.path.join(dest, "manifest.json"), "w").write(json.dumps(m, indent=1))
    rc = {"pod": r["id"], "manifest_sha256": msha, "manifest_stage": m.get("stage"), "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
          "files": len(got), "bytes": m.get("total_bytes"), "failed": bad}
    json.dump(rc, open(os.path.join(dest, "FETCH_RECEIPT.json"), "w"), indent=1)
    r.setdefault("fetches", []).append({**rc, "dest": dest}); save_rec(r)
    print(json.dumps({"fetched": len(got), "failed": bad, "dest": dest, "manifest_sha256": msha}))
    return not bad

def check(r, dest, args):
    """the delete conditions; returns (ok, problems, overrides used)"""
    probs, used = [], []
    m, msha = live_manifest(r)
    if m is None:
        if "--accept-unreachable" in args: used.append("accept-unreachable: " + opt(args, "--accept-unreachable", "")); return True, [msha], used
        return False, [msha + " (pod stopped? `pod.py resume` it, then fetch; or --accept-unreachable \"<reason>\")"], used
    names = {f["path"] for f in m["files"]}; miss_exp = [e for e in r.get("expect", []) if e not in names]
    if miss_exp:
        if "--accept-incomplete" in args: used.append("accept-incomplete %s: %s" % (miss_exp, opt(args, "--accept-incomplete", "")))
        else: probs.append("expected results not produced on the pod: %s (job unfinished? or --accept-incomplete \"<reason>\")" % miss_exp)
    rp = os.path.join(dest, "FETCH_RECEIPT.json")
    if not os.path.exists(rp): probs.append("no FETCH_RECEIPT.json in %s: run `pod.py fetch %s` first" % (dest, r["id"])); return not probs, probs, used
    rc = json.load(open(rp))
    if rc.get("manifest_sha256") != msha: probs.append("the pod's manifest changed since the last fetch (new results): fetch again")
    if rc.get("failed"): probs.append("last fetch had failed files: %s" % rc["failed"])
    for f in m["files"]:
        p = os.path.join(dest, *f["path"].split("/"))
        if not os.path.exists(p): probs.append("missing locally: " + f["path"])
        elif os.path.getsize(p) != f["size"] or sha256_file(p) != f["sha256"]: probs.append("checksum mismatch locally: " + f["path"])
    return not probs, probs, used

def opt(a, k, d): return a[a.index(k) + 1] if k in a and a.index(k) + 1 < len(a) else d

def main(a):
    if not a: print(__doc__); return 2
    if a[0] == "create":
        ep, gpu, br, key = a[1], opt(a, "--gpu", "NVIDIA GeForce RTX 4090"), opt(a, "--branch", "main"), secrets.token_hex(16)
        script = "gpu_diag.sh" if "--diag" in a else opt(a, "--script", "render_pod.sh")
        boot = ("apt-get update -qq && apt-get install -y -qq git ca-certificates >/dev/null 2>&1; git clone -q --depth 1 -b %s %s /root/repo "
                "&& bash /root/repo/.claude/skills/ricks-clips/scripts/runpod/%s; sleep infinity") % (br, REPO, script)
        inp = {"cloudType": opt(a, "--cloud", "ALL"), "gpuCount": 1, "volumeInGb": int(opt(a, "--volume-gb", "20")), "containerDiskInGb": 60, "minVcpuCount": 8, "minMemoryInGb": 30,   # volume: results survive a watchdog STOP
               "gpuTypeId": gpu, "name": "ricksclips-diag" if "--diag" in a else ("ricksclips-lookdev" if "lookdev" in script else "ricksclips-render"), "imageName": opt(a, "--image", "runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04"),
               "dockerArgs": "bash -c '%s'" % boot, "ports": "8000/http", "volumeMountPath": "/workspace",
               "env": [{"key": "RICKCLIPS_EPISODE", "value": ep}, {"key": "RICKCLIPS_PUB_KEY", "value": key}, {"key": "RICKCLIPS_MAX_HOURS", "value": opt(a, "--max-hours", "3")}, {"key": "RICKCLIPS_SCALE", "value": opt(a, "--scale", "1")}, {"key": "RICKCLIPS_BRANCH", "value": br}, {"key": "RICKCLIPS_POST", "value": opt(a, "--post", "")}, {"key": "RICKCLIPS_ALLOW_CPU", "value": "1" if "--allow-cpu" in a else "0"},
                       {"key": "NVIDIA_DRIVER_CAPABILITIES", "value": "all"}]}
        d = gql("mutation($i: PodFindAndDeployOnDemandInput) { podFindAndDeployOnDemand(input: $i) { id name desiredStatus costPerHr machine { gpuDisplayName } } }", {"i": inp})["podFindAndDeployOnDemand"]
        d["pub_key"] = key; d["status_url"] = "https://%s-8000.proxy.runpod.net/%s/status.json" % (d["id"], key)
        save_rec({"id": d["id"], "status_url": d["status_url"], "episode": ep, "script": script, "expect": EXPECT.get(script, []), "created": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "costPerHr": d.get("costPerHr")})
        print(json.dumps(d)); return 0
    if a[0] == "status":
        print(json.dumps(gql("query($i: PodFilter) { pod(input: $i) { id name desiredStatus lastStatusChange costPerHr uptimeSeconds: runtime { uptimeInSeconds } } }", {"i": {"podId": a[1]}})["pod"])); return 0
    if a[0] == "balance":
        print(json.dumps(gql("query { myself { clientBalance currentSpendPerHr pods { id desiredStatus costPerHr } } }")["myself"])); return 0
    if a[0] == "list":
        for n in sorted(os.listdir(PODS)) if os.path.isdir(PODS) else []:
            r = json.load(open(os.path.join(PODS, n))); f = (r.get("fetches") or [{}])[-1]
            print("%s  %s  %s  created %s  last fetch %s (%s files)%s" % (r["id"], r.get("script"), r.get("episode"), r.get("created"), f.get("fetched_at", "never"), f.get("files", 0), "  DELETED " + r["deleted"] if r.get("deleted") else ""))
        return 0
    if a[0] == "resume":
        print(json.dumps(gql("mutation($i: PodResumeInput!) { podResume(input: $i) { id desiredStatus costPerHr } }", {"i": {"podId": a[1], "gpuCount": 1}})["podResume"])); return 0
    if a[0] in ("fetch", "verify", "delete"):
        pid = a[1]; r = load_rec(pid)
        if r is None:
            if a[0] == "delete" and "--forget-unknown" in a: r = {"id": pid, "status_url": "http://unreachable.invalid/x/status.json", "expect": []}
            else: print("REFUSED: no local record for pod %s in %s (created elsewhere?). Add one with its status_url, or --forget-unknown \"<reason>\" to delete it unchecked." % (pid, PODS)); return 1
        dest = opt(a, "--dest", default_dest(r))
        if a[0] == "fetch": return 0 if fetch(r, dest) else 1
        if "--forget-unknown" in a and r.get("status_url", "").startswith("http://unreachable.invalid"): ok, probs, used = True, [], ["forget-unknown: " + opt(a, "--forget-unknown", "")]
        else: ok, probs, used = check(r, dest, a)
        print(json.dumps({"pod": pid, "safe_to_delete": ok, "problems": probs, "overrides": used, "dest": dest}, indent=1))
        if a[0] == "verify": return 0 if ok else 1
        if not ok: print("REFUSED: pod %s keeps running (and billing) until its results are safe locally." % pid); return 1
        if "--dry-run" in a: print("dry run: would terminate", pid); return 0
        gql("mutation($i: PodTerminateInput!) { podTerminate(input: $i) }", {"i": {"podId": pid}})
        r["deleted"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()); r["delete_overrides"] = used
        if r.get("status_url", "").startswith("http"): save_rec(r)
        print(json.dumps({"deleted": pid, "overrides": used}))
        left = [p["id"] for p in gql("query { myself { pods { id } } }")["myself"]["pods"]]; print(json.dumps({"pods_left": left})); return 0
    print(__doc__); return 2

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

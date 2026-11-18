"""Results manifest of a RunPod pod (2026-11-18, audit P0 "lock lost with the pod").
Runs ON the pod after every stage: lists every published file with its size and sha256 in <pub>/manifest.json, so the local side
(`pod.py fetch`) can download exactly what exists and prove it arrived intact, and `pod.py delete` can refuse while anything is missing.
    python3 manifest.py <pub dir> [<stage label>]
The manifest never lists itself, status.json, index.html or partial files (*.tmp)."""
import hashlib, json, os, sys, time

SKIP = {"manifest.json", "manifest.json.tmp", "status.json", "status.json.tmp", "index.html"}

def sha256(p, bs=1 << 20):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(bs), b""): h.update(b)
    return h.hexdigest()

def build(pub, stage=""):
    files = []
    for root, _, names in os.walk(pub):
        for n in sorted(names):
            rel = os.path.relpath(os.path.join(root, n), pub).replace(os.sep, "/")
            if rel in SKIP or n.endswith(".tmp"): continue
            p = os.path.join(root, n); files.append({"path": rel, "size": os.path.getsize(p), "sha256": sha256(p)})
    files.sort(key=lambda x: x["path"])
    return {"version": 1, "stage": stage, "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "files": files,
            "total_bytes": sum(x["size"] for x in files)}

if __name__ == "__main__":
    pub = sys.argv[1]; m = build(pub, sys.argv[2] if len(sys.argv) > 2 else "")
    tmp = os.path.join(pub, "manifest.json.tmp"); json.dump(m, open(tmp, "w"), indent=1); os.replace(tmp, os.path.join(pub, "manifest.json"))
    print("manifest: %d files, %.1f MB, stage %s" % (len(m["files"]), m["total_bytes"] / 1e6, m["stage"]))

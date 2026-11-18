"""rc.cache — content-addressed persistent cache (Mission 1, 2026-11-18). Pure Python: usable from system Python and from Blender.

A cache entry is a folder named by the sha256 of everything that decides its content:
    key = sha256( kind + canonical-JSON(inputs) + sha256 of every code file + sha256 of every input file + tool versions )
So the same inputs never rebuild, and any change in code, data or version gives a new key (old entries stay; nothing is overwritten).

    from rc import cache
    path = cache.get_or_build("asset", {"id": "crawler_dozer"}, build_fn, code_files=[builder.py, kit.py], versions={"blender": "5.2.2"})
    # build_fn(out_dir) writes into out_dir; the entry is published atomically (tmp folder + rename) with meta.json

Rules (CB 2026-11-18): the cache NEVER deletes anything by itself. `verify(entry)` re-hashes every file against meta.json.
Root: $RICKCLIPS_CACHE, default ~/.ricksclips/cache (on a pod: the volume, so a stopped pod keeps it)."""
import hashlib, json, os, shutil, tempfile, time

ROOT = os.path.expanduser(os.environ.get("RICKCLIPS_CACHE", "~/.ricksclips/cache"))

def sha256_file(p, bs=1 << 20):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(bs), b""): h.update(b)
    return h.hexdigest()

def _canon(x): return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)

def key(kind, inputs, code_files=(), input_files=(), versions=None):
    """the content key; returns (hex key, the key material as a dict for meta.json)"""
    mat = {"kind": kind, "inputs": inputs, "versions": versions or {},
           "code": {os.path.basename(p): sha256_file(p) for p in sorted(code_files)},
           "files": {os.path.basename(p): sha256_file(p) for p in sorted(input_files)}}
    return hashlib.sha256(_canon(mat).encode()).hexdigest(), mat

def entry_dir(kind, k): return os.path.join(ROOT, kind, k[:2], k)

def lookup(kind, k):
    d = entry_dir(kind, k); return d if os.path.exists(os.path.join(d, "meta.json")) else None

def get_or_build(kind, inputs, build_fn, code_files=(), input_files=(), versions=None, log=print):
    k, mat = key(kind, inputs, code_files, input_files, versions); hit = lookup(kind, k)
    if hit: log("[cache] HIT  %s %s" % (kind, k[:12])); return hit
    d = entry_dir(kind, k); os.makedirs(os.path.dirname(d), exist_ok=True)
    tmp = tempfile.mkdtemp(prefix=".build_", dir=os.path.dirname(d)); t0 = time.time()
    log("[cache] MISS %s %s -> building" % (kind, k[:12]))
    try:
        build_fn(tmp)
        files = {}
        for root, _, names in os.walk(tmp):
            for n in names:
                p = os.path.join(root, n); files[os.path.relpath(p, tmp).replace(os.sep, "/")] = {"size": os.path.getsize(p), "sha256": sha256_file(p)}
        if not files: raise RuntimeError("build produced no file")
        json.dump({"key": k, "material": mat, "built": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "seconds": round(time.time() - t0, 2), "files": files},
                  open(os.path.join(tmp, "meta.json"), "w"), indent=1)
        if os.path.exists(d): shutil.rmtree(tmp); return d          # a parallel builder published the same key first: same content by definition
        os.replace(tmp, d)
    except BaseException:
        shutil.rmtree(tmp, ignore_errors=True); raise                # a failed build leaves no entry behind
    log("[cache] BUILT %s %s in %.1f s" % (kind, k[:12], time.time() - t0)); return d

def verify(d):
    """(ok, problems): every file of meta.json present with the same size and sha256"""
    m = json.load(open(os.path.join(d, "meta.json"))); probs = []
    for rel, f in m["files"].items():
        p = os.path.join(d, rel)
        if not os.path.exists(p): probs.append("missing " + rel)
        elif os.path.getsize(p) != f["size"] or sha256_file(p) != f["sha256"]: probs.append("changed " + rel)
    return not probs, probs

def stats():
    out = {}
    if not os.path.isdir(ROOT): return out
    for kind in sorted(os.listdir(ROOT)):
        n = b = 0
        for root, _, names in os.walk(os.path.join(ROOT, kind)):
            if os.path.basename(root).startswith(".build_"): continue
            if "meta.json" in names: n += 1
            b += sum(os.path.getsize(os.path.join(root, x)) for x in names)
        out[kind] = {"entries": n, "bytes": b}
    return out

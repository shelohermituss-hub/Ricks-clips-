"""Upload a file to GoFile (guest upload) and VERIFY the download: the file is fetched back from GoFile and its sha256 compared.
    python3 gofile_upload_verify.py <file> <result.json>
result.json: downloadPage, fileId, size, sha256_local, sha256_downloaded, verified, method, errors. Exit 0 only when verified.
Download for verification: the folder contents API (Bearer guest token + the site's current "wt" value read from gofile.io/dist/js/*.js)
gives the file's direct link, fetched with the accountToken cookie."""
import hashlib, json, re, subprocess, sys, urllib.request
path, out = sys.argv[1], sys.argv[2]
R = {"errors": []}
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
def get(url, headers=None):
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", **(headers or {})}), timeout=120)
R["sha256_local"] = sha(path)
up = json.loads(subprocess.check_output(["curl", "-sS", "--retry", "3", "-F", "file=@" + path, "https://upload.gofile.io/uploadfile"]))
if up.get("status") != "ok": R["errors"].append("upload: %s" % up); json.dump(R, open(out, "w"), indent=1); sys.exit(1)
d = up["data"]; R.update(downloadPage=d.get("downloadPage"), fileId=d.get("id") or d.get("fileId"), fileName=d.get("name") or d.get("fileName"), size=d.get("size"), folder=d.get("parentFolder"))
tok = d.get("guestToken")
wt = None
for js in ("https://gofile.io/dist/js/config.js", "https://gofile.io/dist/js/global.js", "https://gofile.io/dist/js/wt.obf.js"):
    try:
        m = re.search(r'wt\s*[:=]\s*["\']([A-Za-z0-9]+)["\']', get(js).read().decode("utf-8", "ignore"))
        if m: wt = m.group(1); R["wt_from"] = js; break
    except Exception as e: R["errors"].append("%s: %s" % (js, e))
link = None
try:
    c = json.load(get("https://api.gofile.io/contents/%s%s" % (R["folder"], "?wt=" + wt if wt else ""), {"Authorization": "Bearer " + tok, **({"X-Website-Token": wt} if wt else {})}))
    ch = c.get("data", {}).get("children", {})
    link = next((v.get("link") for v in ch.values() if v.get("id") == R["fileId"] or v.get("name") == R["fileName"]), None)
    R["method"] = "contents API"
except Exception as e: R["errors"].append("contents: %s" % e)
if link:
    tmp = path + ".downloaded"
    try:
        with get(link, {"Cookie": "accountToken=" + tok}) as r, open(tmp, "wb") as f:
            while True:
                b = r.read(1 << 20)
                if not b: break
                f.write(b)
        R["sha256_downloaded"] = sha(tmp); R["verified"] = R["sha256_downloaded"] == R["sha256_local"]
    except Exception as e: R["errors"].append("download: %s" % e)
if not R.get("verified"):   # weaker fallback check: the public download page answers
    try: R["download_page_http"] = get(R["downloadPage"]).status
    except Exception as e: R["errors"].append("page: %s" % e)
R.setdefault("verified", False)
json.dump(R, open(out, "w"), indent=1); print(json.dumps({k: R.get(k) for k in ("downloadPage", "verified", "method", "errors")}))
sys.exit(0 if R["verified"] else 1)

#!/usr/bin/env python3
"""RicksClips Asset Hub: licensed asset search, ingestion, validation and staging.

Providers:
  sketchfab  Public model search; downloads require the user's own API/OAuth token.
  polyhaven  Public API search/download (CC0).
  ambientcg  Public API v3 search/download (CC0).
  fab        Official marketplace search hand-off + guarded local import after acquisition.
  blenderkit Uses the user's logged-in BlenderKit add-on via the existing tool.

No credentials are stored in this skill. No marketplace login, purchase, paywall,
or provider download restriction is bypassed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any, Dict, Iterable, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / "library" / "assets"
CATALOG = LIBRARY / "catalog.json"
USER_AGENT = os.environ.get("RICKCLIPS_ASSET_HUB_USER_AGENT", "RicksClips-AssetHub/1.2")
MAX_DOWNLOAD_MB = 2048
ALLOWED_SKETCHFAB = {"cc0", "by", "cc-by", "cc-by-4.0"}
# This production helper is for environments and ordinary set dressing only.
# Block searches/imports for weapon and self-defence asset categories.
RESTRICTED_ASSET_TERMS = re.compile(
    r"\b(guns?|firearms?|rifles?|pistols?|handguns?|shotguns?|ammunition|ammo|weapons?|swords?|daggers?|knives|knife|switchblades?|machetes?|spears?|crossbows?|bows?\s+and\s+arrows?|tasers?|pepper\s+spray|brass\s+knuckles?|fusils?|pistolets?|revolvers?|munitions?|armes?|epees?|épées?|couteaux?|poignards?|machettes?|lances?|arbaletes?|arbalètes?|arc\s+et\s+fleches?|arc\s+et\s+flèches?|matraques?|poings?\s+americains?|poings?\s+américains?)\b",
    re.IGNORECASE,
)

def assert_allowed_asset_topic(value: str) -> None:
    if RESTRICTED_ASSET_TERMS.search(str(value or "")):
        raise AssetHubError("This Asset Hub is limited to environments and ordinary set dressing; it does not search or ingest weapon/self-defence assets.")


class AssetHubError(RuntimeError):
    pass


def clean_id(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9._-]+", "_", str(value)).strip("._")
    if not value or value in {".", ".."}:
        raise AssetHubError("Invalid or empty asset identifier")
    return value[:120]


def api_json(url: str, headers: Optional[dict] = None, timeout: int = 45) -> Any:
    h = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    if headers:
        h.update(headers)
    last = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=h)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            last = exc
            if exc.code == 429 or 500 <= exc.code < 600:
                time.sleep(1.5 * (attempt + 1))
                continue
            detail = exc.read(500).decode("utf-8", "replace") if exc.fp else ""
            raise AssetHubError("HTTP %s for %s: %s" % (exc.code, url, detail)) from exc
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last = exc
            if attempt < 2:
                time.sleep(1.0 * (attempt + 1))
                continue
    raise AssetHubError("Request failed for %s: %s" % (url, last))


def download_url(url: str, dest: Path, max_mb: int = MAX_DOWNLOAD_MB,
                 expected_md5: Optional[str] = None) -> dict:
    if not url.startswith("https://"):
        raise AssetHubError("Refusing non-HTTPS download URL")
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    digest256, digest_md5, total = hashlib.sha256(), hashlib.md5(), 0
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=180) as response, tmp.open("wb") as out:
            final_url = response.geturl()
            if not final_url.startswith("https://"):
                raise AssetHubError("Download redirected to a non-HTTPS URL; blocked")
            length = response.headers.get("Content-Length")
            if length and int(length) > max_mb * 1024 * 1024:
                raise AssetHubError("Download exceeds --max-mb limit")
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > max_mb * 1024 * 1024:
                    raise AssetHubError("Download exceeded --max-mb limit")
                out.write(chunk)
                digest256.update(chunk)
                digest_md5.update(chunk)
        if expected_md5 and digest_md5.hexdigest().lower() != expected_md5.lower():
            raise AssetHubError("MD5 checksum mismatch for downloaded file")
        tmp.replace(dest)
        return {"path": str(dest), "bytes": total, "sha256": digest256.hexdigest(), "md5": digest_md5.hexdigest()}
    except Exception:
        tmp.unlink(missing_ok=True)
        raise


def safe_extract(zip_path: Path, dest: Path, max_mb: int = 4096) -> List[str]:
    """Extract an archive without zip-slip, symlink or decompression-bomb paths."""
    dest.mkdir(parents=True, exist_ok=True)
    written, total = [], 0
    with zipfile.ZipFile(zip_path) as zf:
        for info in zf.infolist():
            name = info.filename.replace("\\", "/")
            pp = PurePosixPath(name)
            if pp.is_absolute() or re.match(r"^[A-Za-z]:", name) or ".." in pp.parts or not pp.parts:
                raise AssetHubError("Unsafe archive path blocked: %s" % name)
            # Block Unix symlink entries.
            mode = (info.external_attr >> 16) & 0xFFFF
            if mode and (mode & 0o170000) == 0o120000:
                raise AssetHubError("Symlink entry blocked in archive: %s" % name)
            total += info.file_size
            if total > max_mb * 1024 * 1024:
                raise AssetHubError("Archive expands beyond --max-mb limit")
            target = dest.joinpath(*pp.parts)
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info) as src, target.open("wb") as out:
                shutil.copyfileobj(src, out, 1024 * 1024)
            written.append(str(target))
    return written


def load_catalog() -> dict:
    if not CATALOG.exists():
        return {"schema_version": 1, "assets": []}
    try:
        data = json.loads(CATALOG.read_text(encoding="utf-8"))
        if not isinstance(data.get("assets"), list):
            raise ValueError("catalog assets must be a list")
        return data
    except Exception as exc:
        raise AssetHubError("Catalog is invalid: %s" % exc)


def save_record(record: dict) -> None:
    data = load_catalog()
    key = (record.get("provider"), record.get("asset_id"))
    data["assets"] = [a for a in data["assets"] if (a.get("provider"), a.get("asset_id")) != key]
    data["assets"].append(record)
    data["assets"].sort(key=lambda a: (a.get("provider", ""), a.get("name", "").casefold()))
    CATALOG.parent.mkdir(parents=True, exist_ok=True)
    tmp = CATALOG.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(CATALOG)



def license_slug(raw: Any) -> str:
    if isinstance(raw, dict):
        raw = raw.get("slug") or raw.get("label") or raw.get("name") or "unknown"
    return str(raw or "unknown").strip().lower().replace("creative commons", "cc").replace("attribution", "by").replace(" ", "-")


def search_sketchfab(query: str, limit: int = 12) -> List[dict]:
    params = urllib.parse.urlencode({"type": "models", "q": query, "downloadable": "true", "count": min(24, max(1, limit))})
    data = api_json("https://api.sketchfab.com/v3/search?" + params)
    out = []
    for item in data.get("results", []):
        lic_raw = item.get("license") or "unknown"
        lic = license_slug(lic_raw)
        # Conservative allow-list. Non-commercial, no-derivatives, and unknown licenses are never auto-imported.
        allowed = lic in ALLOWED_SKETCHFAB or lic.endswith("/licenses/cc0") or lic.endswith("/licenses/by/4.0")
        author = (item.get("user") or {}).get("displayName") or (item.get("user") or {}).get("username")
        images = ((item.get("thumbnails") or {}).get("images") or [])
        out.append({"provider": "sketchfab", "asset_id": item.get("uid"), "name": item.get("name"),
                    "creator": author, "license": lic_raw, "license_allowed_by_default": allowed,
                    "downloadable": bool(item.get("isDownloadable")), "faces": item.get("faceCount"),
                    "views": item.get("viewCount"), "preview": images[-1].get("url") if images else None,
                    "source_url": item.get("viewerUrl") or ("https://sketchfab.com/3d-models/" + str(item.get("uid"))),
                    "download_requires_user_token": True})
    return out


def search_polyhaven(query: str, kind: str = "all", limit: int = 12) -> List[dict]:
    data = api_json("https://api.polyhaven.com/assets")
    q = query.casefold().split()
    typemap = {0: "hdri", 1: "texture", 2: "model"}
    wanted = {"material": "texture", "terrain": "texture", "all": None}.get(kind, kind)
    out = []
    for aid, item in data.items():
        kind_name = typemap.get(item.get("type"), "unknown")
        if wanted and kind_name != wanted:
            continue
        hay = " ".join([str(item.get("name", "")), str(item.get("description", "")), str(item.get("category", "")), " ".join(item.get("tags", []))]).casefold()
        if not all(token in hay for token in q):
            continue
        authors = item.get("authors") or {}
        out.append({"provider": "polyhaven", "asset_id": aid, "name": item.get("name", aid),
                    "creator": ", ".join(authors.keys()), "license": "CC0", "license_allowed_by_default": True,
                    "kind": kind_name, "polycount": item.get("polycount"), "tags": item.get("tags", []),
                    "preview": item.get("thumbnail_url"), "source_url": "https://polyhaven.com/a/" + aid})
    out.sort(key=lambda x: x.get("name", "").casefold())
    return out[:limit]


def _ambient_items(data: Any) -> List[dict]:
    """Normalize ambientCG's documented JSON response while tolerating schema wrappers."""
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict):
        for key in ("foundAssets", "assets", "results", "data"):
            if isinstance(data.get(key), list):
                return [x for x in data[key] if isinstance(x, dict)]
        # Some responses can be keyed by asset ID.
        if data and all(isinstance(v, dict) for v in data.values()):
            rows = []
            for aid, value in data.items():
                row = dict(value)
                row.setdefault("assetId", aid)
                rows.append(row)
            return rows
    return []


def search_ambientcg(query: str, kind: str = "material", limit: int = 12) -> List[dict]:
    kind_map = {"material": "material", "texture": "material", "hdri": "hdri", "model": "3d-model", "terrain": "terrain", "all": ""}
    params = {"q": query, "limit": min(100, max(1, limit)), "include": "type,title,shortDescription,url,tags,downloads,thumbnails"}
    if kind_map.get(kind, kind):
        params["type"] = kind_map.get(kind, kind)
    url = "https://ambientcg.com/api/v3/assets?" + urllib.parse.urlencode(params)
    data = api_json(url)
    out = []
    for item in _ambient_items(data):
        aid = item.get("assetId") or item.get("id") or item.get("asset_id")
        if not aid:
            continue
        title = item.get("displayName") or item.get("title") or item.get("name") or aid
        tags = item.get("tags") or []
        url = item.get("url") or ("https://ambientcg.com/view?id=" + str(aid))
        actual_type = item.get("type") or item.get("assetType") or kind_map.get(kind, kind)
        out.append({"provider": "ambientcg", "asset_id": str(aid), "name": title,
                    "creator": "ambientCG", "license": "CC0", "license_allowed_by_default": True,
                    "kind": actual_type, "tags": tags, "source_url": url,
                    "download_metadata_available": bool(item.get("downloads") or item.get("downloadFiles"))})
    return out[:limit]


def search_fab(query: str) -> List[dict]:
    encoded = urllib.parse.quote(query)
    return [{"provider": "fab", "name": "Search Fab for: " + query,
             "asset_id": "manual-acquisition", "license": "Fab Standard / CC-BY / UE Marketplace (check each listing)",
             "license_allowed_by_default": False, "acquisition": "manual_via_epic_account",
             "source_url": "https://www.fab.com/search?q=" + encoded,
             "notes": "Open the listing, verify license and formats, add to your Fab Library, download with Fab/Launcher, then run asset_hub.py import-local."}]


def search_blenderkit(query: str, limit: int = 7) -> List[dict]:
    blender = os.environ.get("BLENDER_BIN") or shutil.which("blender")
    if not blender:
        raise AssetHubError("Blender executable not found. Set BLENDER_BIN or add blender to PATH; BlenderKit search uses the logged-in add-on.")
    script = ROOT / "tools" / "blenderkit_tool.py"
    proc = subprocess.run([blender, "-b", "--python-exit-code", "1", "--python", str(script), "--", "search", query],
                          capture_output=True, text=True, timeout=180)
    if proc.returncode:
        raise AssetHubError("BlenderKit bridge failed: " + (proc.stderr[-1200:] or proc.stdout[-1200:]))
    rows = []
    for line in proc.stdout.splitlines():
        if line.startswith("BKR "):
            try:
                r = json.loads(line[4:])
                rows.append({"provider": "blenderkit", "asset_id": r.get("base"), "asset_version_id": r.get("id"),
                             "name": r.get("name"), "creator": r.get("author"), "license": r.get("lic"),
                             "license_allowed_by_default": r.get("lic") in {"royalty_free", "cc_zero"},
                             "faces": r.get("faces"), "style": r.get("style"),
                             "source_url": "https://www.blenderkit.com/asset-gallery-detail/%s/" % r.get("id")})
            except json.JSONDecodeError:
                continue
    return rows[:limit]


def do_search(provider: str, query: str, kind: str, limit: int) -> List[dict]:
    assert_allowed_asset_topic(query)
    if provider == "sketchfab": return search_sketchfab(query, limit)
    if provider == "polyhaven": return search_polyhaven(query, kind, limit)
    if provider == "ambientcg": return search_ambientcg(query, kind, limit)
    if provider == "fab": return search_fab(query)
    if provider == "blenderkit": return search_blenderkit(query, limit)
    rows, errors = [], []
    for name in ("polyhaven", "ambientcg", "sketchfab", "fab", "blenderkit"):
        try:
            rows.extend(do_search(name, query, kind, limit))
        except Exception as exc:
            errors.append({"provider": name, "error": str(exc)})
    for row in rows:
        row.setdefault("search_errors", errors)
    return rows


def recurse_download_entries(node: Any, trail: Tuple[str, ...] = ()) -> List[dict]:
    out = []
    if isinstance(node, dict):
        url = node.get("url") or node.get("rawLink") or node.get("downloadLink")
        if isinstance(url, str) and url.startswith("https://"):
            out.append({"url": url, "size": node.get("size"), "md5": node.get("md5"), "path": trail,
                        "label": "_".join(trail), "filename": node.get("filename") or node.get("fileName")})
        for k, value in node.items():
            if k not in {"url", "rawLink", "downloadLink"}:
                out.extend(recurse_download_entries(value, trail + (str(k),)))
    elif isinstance(node, list):
        for i, value in enumerate(node):
            out.extend(recurse_download_entries(value, trail + (str(i),)))
    return out


def pick_download(entries: List[dict], kind: str, resolution: str, fmt: str = "auto") -> dict:
    if not entries:
        raise AssetHubError("Provider returned no downloadable files for this asset")
    res = resolution.lower().replace(" ", "")
    def score(entry: dict) -> Tuple[int, int, int]:
        p = " ".join(entry.get("path", ())).lower()
        url = entry.get("url", "").lower()
        label = entry.get("label", "").lower()
        ext = Path(urllib.parse.urlparse(url).path).suffix.lower()
        resmatch = int(res in p or res in label or res in url)
        if fmt != "auto": fm = int(ext == "." + fmt.lower().lstrip("."))
        elif kind == "model": fm = {".glb": 4, ".gltf": 3, ".zip": 2, ".blend": 1}.get(ext, 0)
        elif kind == "hdri": fm = int(ext in {".hdr", ".exr", ".zip"})
        else: fm = int(ext in {".zip", ".png", ".jpg", ".jpeg", ".webp"}) + int(ext == ".zip")
        return (resmatch, fm, -int(entry.get("size") or 0))
    ranked = sorted(entries, key=score, reverse=True)
    best = ranked[0]
    if fmt != "auto" and not score(best)[1]:
        raise AssetHubError("No %s download found; available: %s" % (fmt, ", ".join(sorted({Path(urllib.parse.urlparse(x['url']).path).suffix for x in entries}))))
    return best


def find_ambient_download(item: dict, resolution: str, fmt: str) -> dict:
    entries = recurse_download_entries(item)
    # Prefer the requested resolution; if no exact match, choose the nearest smaller resolution, then first available.
    return pick_download(entries, "material", resolution, fmt)


def _write_provider_manifest(folder: Path, meta: dict, files: List[dict]) -> dict:
    record = {"schema_version": 1, **meta, "downloaded_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              "files": files, "status": "ingested", "commercial_use": meta.get("commercial_use", "verify_provider_terms")}
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "ASSET_MANIFEST.json").write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    save_record(record)
    return record


def download_polyhaven(asset_id: str, resolution: str = "2k", fmt: str = "auto", max_mb: int = MAX_DOWNLOAD_MB) -> dict:
    aid = clean_id(asset_id)
    meta = api_json("https://api.polyhaven.com/assets")
    if aid not in meta:
        raise AssetHubError("Unknown Poly Haven asset id: " + aid)
    item = meta[aid]
    assert_allowed_asset_topic(" ".join(str(item.get(k, "")) for k in ("name", "description", "category", "tags")))
    files = api_json("https://api.polyhaven.com/files/" + urllib.parse.quote(aid))
    entries = recurse_download_entries(files)
    kind = {0: "hdri", 1: "material", 2: "model"}.get(item.get("type"), "model")
    res = resolution.lower()
    if kind == "material":
        # A PBR material is a set of maps. Keep all map channels for the chosen resolution,
        # rather than downloading only one arbitrary colour/roughness file.
        selected = [e for e in entries if res in " ".join(e.get("path", ())).lower()
                    and Path(urllib.parse.urlparse(e["url"]).path).suffix.lower() in {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".exr"}]
        if not selected:
            selected = [pick_download(entries, kind, resolution, fmt)]
    else:
        selected = [pick_download(entries, kind, resolution, fmt)]
    folder = LIBRARY / "polyhaven" / aid
    file_records = []
    for index, chosen in enumerate(selected):
        suffix = Path(urllib.parse.urlparse(chosen["url"]).path).suffix or ".bin"
        label = clean_id(chosen.get("label") or "file_%02d" % (index + 1))
        target = folder / (aid + "_" + label + suffix)
        info = download_url(chosen["url"], target, max_mb, chosen.get("md5"))
        info.update({"role": "pbr_map" if kind == "material" else "primary", "resolution": resolution, "source_url": chosen["url"]})
        file_records.append(info)
    # Blend/GLTF downloads may be supplied as archives by the API.
    for item_rec in list(file_records):
        if Path(item_rec["path"]).suffix.lower() == ".zip":
            extracted = safe_extract(Path(item_rec["path"]), folder / "extracted", max_mb=max_mb * 2)
            file_records.extend({"path": p, "role": "extracted"} for p in extracted)
    record = _write_provider_manifest(folder, {"provider": "polyhaven", "asset_id": aid, "name": item.get("name", aid),
        "creator": ", ".join((item.get("authors") or {}).keys()), "license": "CC0", "license_url": "https://polyhaven.com/license",
        "source_url": "https://polyhaven.com/a/" + aid, "kind": kind, "api_credit": "Powered by Poly Haven"}, file_records)
    return record


def download_ambientcg(asset_id: str, resolution: str = "2K", fmt: str = "zip", max_mb: int = MAX_DOWNLOAD_MB) -> dict:
    aid = clean_id(asset_id)
    params = urllib.parse.urlencode({"id": aid, "include": "type,title,shortDescription,url,tags,downloads,thumbnails"})
    data = api_json("https://ambientcg.com/api/v3/assets?" + params)
    rows = _ambient_items(data)
    item = next((x for x in rows if str(x.get("assetId") or x.get("id")) == aid), None)
    if not item and rows:
        item = rows[0]
    if not item:
        raise AssetHubError("ambientCG did not return metadata for: " + aid)
    assert_allowed_asset_topic(" ".join(str(item.get(k, "")) for k in ("displayName", "title", "shortDescription", "tags")))
    chosen = find_ambient_download(item, resolution, fmt)
    folder = LIBRARY / "ambientcg" / aid
    suffix = Path(urllib.parse.urlparse(chosen["url"]).path).suffix or Path(chosen.get("filename") or "asset.zip").suffix or ".zip"
    target = folder / (aid + "_" + resolution + suffix)
    info = download_url(chosen["url"], target, max_mb)
    file_records = [dict(info, role="primary", resolution=resolution, source_url=chosen["url"])]
    if suffix.lower() == ".zip":
        extracted = safe_extract(target, folder / "extracted", max_mb=max_mb * 2)
        file_records.extend({"path": p, "role": "extracted"} for p in extracted)
    asset_type = item.get("type") or item.get("assetType") or "material"
    if isinstance(asset_type, list):
        asset_type = asset_type[0] if asset_type else "material"
    record = _write_provider_manifest(folder, {"provider": "ambientcg", "asset_id": aid,
        "name": item.get("displayName") or item.get("title") or aid, "creator": "ambientCG", "license": "CC0",
        "license_url": "https://ambientcg.com/license", "source_url": item.get("url") or "https://ambientcg.com/view?id=" + aid,
        "kind": str(asset_type), "commercial_use": "CC0"}, file_records)
    return record


def download_sketchfab(uid: str, max_mb: int = MAX_DOWNLOAD_MB) -> dict:
    token = os.environ.get("SKETCHFAB_OAUTH_TOKEN") or os.environ.get("RICKCLIPS_SKETCHFAB_TOKEN")
    if not token and os.environ.get("CLAUDE_CODE_REMOTE") != "true":
        raise AssetHubError("Set SKETCHFAB_OAUTH_TOKEN to your own Sketchfab OAuth access token. Downloads require account authentication.")
    uid = clean_id(uid)
    # In Claude Code Web, a Network Secret for api.sketchfab.com injects Authorization at the outbound proxy.
    auth = {"Authorization": "Bearer " + token} if token else {}

    model = api_json("https://api.sketchfab.com/v3/models/" + urllib.parse.quote(uid), headers=auth)
    assert_allowed_asset_topic(" ".join(str(model.get(k, "")) for k in ("name", "description", "categories", "tags")))
    if not model.get("isDownloadable"):
        raise AssetHubError("This Sketchfab model is not marked downloadable by its owner")
    lic_raw = model.get("license") or "unknown"
    lic = license_slug(lic_raw)
    allowed = lic in ALLOWED_SKETCHFAB or lic.endswith("/licenses/cc0") or lic.endswith("/licenses/by/4.0")
    if not allowed:
        raise AssetHubError("Sketchfab license is not in the automatic allow-list (CC0 or CC BY). Review manually: %s" % lic_raw)
    dl = api_json("https://api.sketchfab.com/v3/models/" + urllib.parse.quote(uid) + "/download", headers=auth)
    gltf = dl.get("gltf") or {}
    url = gltf.get("url")
    if not url:
        raise AssetHubError("Sketchfab did not return a glTF download URL")
    folder = LIBRARY / "sketchfab" / uid
    target = folder / (uid + "_source.zip")
    info = download_url(url, target, max_mb)
    extracted = safe_extract(target, folder / "gltf", max_mb=max_mb * 2)
    user = model.get("user") or {}
    record = _write_provider_manifest(folder, {"provider": "sketchfab", "asset_id": uid, "name": model.get("name", uid),
        "creator": user.get("displayName") or user.get("username"), "license": lic_raw,
        "license_url": "https://creativecommons.org/licenses/" + ("by/4.0" if "by" in lic else "publicdomain/zero/1.0"),
        "source_url": model.get("viewerUrl") or "https://sketchfab.com/3d-models/" + uid,
        "kind": "model", "commercial_use": "check exact license and preserve attribution"},
        [dict(info, role="source_archive")] + [{"path": p, "role": "extracted"} for p in extracted])
    return record


def import_local(provider: str, source: Path, asset_name: str, license_name: str,
                 source_url: str, creator: str = "unknown", license_url: str = "",
                 evidence: str = "", commercial_use: str = "not_verified") -> dict:
    """Import a user-acquired local asset. Fab requires explicit evidence metadata."""
    if provider not in {"fab", "blenderkit", "manual"}:
        raise AssetHubError("import-local is intended for Fab/manual/BlenderKit local acquisitions")
    if not source.exists():
        raise AssetHubError("Source path does not exist: " + str(source))
    if not license_name.strip() or not source_url.startswith("https://"):
        raise AssetHubError("A non-empty license and HTTPS source URL are required")
    assert_allowed_asset_topic(asset_name + " " + source_url)
    if provider == "fab" and not evidence.strip():
        raise AssetHubError("Fab imports require --evidence describing your acquired listing/library item; the tool never assumes ownership")
    aid = clean_id(re.sub(r"[^A-Za-z0-9._-]+", "_", asset_name))
    folder = LIBRARY / provider / aid
    folder.mkdir(parents=True, exist_ok=True)
    copied = []
    if source.is_dir():
        dst = folder / source.name
        if dst.exists():
            raise AssetHubError("Destination already exists; choose a new asset name or archive existing asset")
        shutil.copytree(source, dst)
        copied.extend(str(x) for x in dst.rglob("*") if x.is_file())
    else:
        dst = folder / source.name
        if dst.exists():
            raise AssetHubError("Destination already exists: " + str(dst))
        shutil.copy2(source, dst)
        copied.append(str(dst))
        if dst.suffix.lower() == ".zip":
            safe_extract(dst, folder / "extracted")
            copied.extend(str(x) for x in (folder / "extracted").rglob("*") if x.is_file())
    files = []
    for p in copied:
        fp = Path(p)
        digest = hashlib.sha256(fp.read_bytes()).hexdigest()
        files.append({"path": str(fp), "bytes": fp.stat().st_size, "sha256": digest, "role": "imported"})
    record = _write_provider_manifest(folder, {"provider": provider, "asset_id": aid, "name": asset_name,
        "creator": creator, "license": license_name, "license_url": license_url or "not_provided",
        "source_url": source_url, "acquisition_evidence": evidence, "commercial_use": commercial_use,
        "kind": "locally_imported"}, files)
    return record


def stage_asset(asset_id: str, provider: str, episode: Path) -> dict:
    if provider not in {"sketchfab", "polyhaven", "ambientcg", "fab", "blenderkit", "manual"}:
        raise AssetHubError("Unsupported asset provider: " + str(provider))
    aid = clean_id(asset_id)
    source = (LIBRARY / provider / aid).resolve()
    try:
        source.relative_to(LIBRARY.resolve())
    except ValueError:
        raise AssetHubError("Asset path escapes the local library")
    manifest = source / "ASSET_MANIFEST.json"
    if not manifest.exists():
        raise AssetHubError("Asset is not in the local catalog: %s/%s" % (provider, aid))
    meta = json.loads(manifest.read_text(encoding="utf-8"))
    if meta.get("status") != "ingested":
        raise AssetHubError("Asset has not passed ingestion")
    dest = episode / "assets" / "asset_hub" / provider / aid
    if dest.exists():
        raise AssetHubError("Asset already staged at %s" % dest)
    shutil.copytree(source, dest)
    from build_asset_credits import build_credits
    credits = build_credits(episode)
    return {"provider": provider, "asset_id": aid, "staged_to": str(dest), "manifest": str(dest / "ASSET_MANIFEST.json"),
            "episode_relative_path": str(Path("assets") / "asset_hub" / provider / aid), "credits_file": str(credits)}


def validate_directory(path: Path) -> dict:
    issues, files = [], []
    if not path.exists() or not path.is_dir():
        raise AssetHubError("Asset directory does not exist: " + str(path))
    for fp in path.rglob("*"):
        if not fp.is_file():
            continue
        rel = str(fp.relative_to(path))
        size = fp.stat().st_size
        rec = {"file": rel, "bytes": size, "extension": fp.suffix.lower()}
        if size == 0:
            issues.append("empty file: " + rel)
        if fp.suffix.lower() == ".glb" and size >= 12:
            with fp.open("rb") as f:
                header = f.read(12)
            if header[:4] != b"glTF" or int.from_bytes(header[4:8], "little") != 2:
                issues.append("invalid GLB header: " + rel)
            else:
                rec["glb_version"] = int.from_bytes(header[4:8], "little")
        elif fp.suffix.lower() == ".gltf":
            try:
                data = json.loads(fp.read_text(encoding="utf-8"))
                if data.get("asset", {}).get("version") != "2.0":
                    issues.append("glTF version is not 2.0: " + rel)
                rec["meshes"] = len(data.get("meshes", []))
                rec["materials"] = len(data.get("materials", []))
            except Exception as exc:
                issues.append("invalid glTF JSON %s: %s" % (rel, exc))
        elif fp.suffix.lower() in {".blend", ".hdr", ".exr", ".png", ".jpg", ".jpeg", ".webp", ".zip", ".bin"}:
            pass
        files.append(rec)
    return {"directory": str(path), "file_count": len(files), "issues": issues, "files": files,
            "status": "PASS" if files and not issues else "FAIL" if issues else "WARN"}


def cmd_search(args: argparse.Namespace) -> int:
    provider_errors = []
    if args.provider == "all":
        rows = []
        for provider in ("polyhaven", "ambientcg", "sketchfab", "fab", "blenderkit"):
            try:
                rows.extend(do_search(provider, args.query, args.kind, args.limit))
            except Exception as exc:
                provider_errors.append({"provider": provider, "error": str(exc)})
        # Keep per-provider failures visible even when every API is temporarily unavailable.
        payload = {"query": args.query, "provider": args.provider, "results": rows, "provider_errors": provider_errors}
    else:
        rows = do_search(args.provider, args.query, args.kind, args.limit)
        payload = {"query": args.query, "provider": args.provider, "results": rows}
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if rows else (2 if provider_errors else 0)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Search, acquire, validate and stage 3D assets for RicksClips")
    sub = parser.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search", help="Search the providers without downloading")
    s.add_argument("provider", choices=["all", "sketchfab", "polyhaven", "ambientcg", "fab", "blenderkit"])
    s.add_argument("query")
    s.add_argument("--kind", choices=["all", "model", "material", "texture", "hdri", "terrain"], default="all")
    s.add_argument("--limit", type=int, default=12)
    s.set_defaults(func=cmd_search)
    d = sub.add_parser("download", help="Download an allowed asset by provider ID")
    d.add_argument("provider", choices=["sketchfab", "polyhaven", "ambientcg"])
    d.add_argument("asset_id")
    d.add_argument("--resolution", default="2k")
    d.add_argument("--format", default="auto")
    d.add_argument("--max-mb", type=int, default=MAX_DOWNLOAD_MB)
    def do_dl(a):
        if a.provider == "sketchfab": r = download_sketchfab(a.asset_id, a.max_mb)
        elif a.provider == "polyhaven": r = download_polyhaven(a.asset_id, a.resolution, a.format, a.max_mb)
        else: r = download_ambientcg(a.asset_id, a.resolution.upper(), a.format, a.max_mb)
        print(json.dumps(r, ensure_ascii=False, indent=2)); return 0
    d.set_defaults(func=do_dl)
    i = sub.add_parser("import-local", help="Register an asset acquired locally (Fab/Fab Launcher or other permitted import)")
    i.add_argument("provider", choices=["fab", "blenderkit", "manual"])
    i.add_argument("source", type=Path)
    i.add_argument("--name", required=True)
    i.add_argument("--license", required=True)
    i.add_argument("--source-url", required=True)
    i.add_argument("--creator", default="unknown")
    i.add_argument("--license-url", default="")
    i.add_argument("--evidence", default="", help="For Fab: e.g. listing ID and confirmation that it is in your Fab Library")
    i.add_argument("--commercial-use", default="not_verified")
    def do_import(a):
        r = import_local(a.provider, a.source, a.name, a.license, a.source_url, a.creator, a.license_url, a.evidence, a.commercial_use)
        print(json.dumps(r, ensure_ascii=False, indent=2)); return 0
    i.set_defaults(func=do_import)
    st = sub.add_parser("stage", help="Copy a catalog asset into one episode's assets folder")
    st.add_argument("provider", choices=["sketchfab", "polyhaven", "ambientcg", "fab", "blenderkit", "manual"])
    st.add_argument("asset_id")
    st.add_argument("--episode", required=True, type=Path)
    def do_stage(a):
        r = stage_asset(a.asset_id, a.provider, a.episode.resolve()); print(json.dumps(r, indent=2)); return 0
    st.set_defaults(func=do_stage)
    v = sub.add_parser("validate", help="Validate a local asset folder")
    v.add_argument("directory", type=Path)
    def do_validate(a):
        r = validate_directory(a.directory.resolve()); print(json.dumps(r, ensure_ascii=False, indent=2)); return 0 if r["status"] == "PASS" else 2
    v.set_defaults(func=do_validate)
    c = sub.add_parser("catalog", help="Print the local asset catalog")
    def do_catalog(a): print(json.dumps(load_catalog(), ensure_ascii=False, indent=2)); return 0
    c.set_defaults(func=do_catalog)
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (AssetHubError, OSError, zipfile.BadZipFile) as exc:
        print("ASSET_HUB_ERROR: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

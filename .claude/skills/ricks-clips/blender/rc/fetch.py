"""rc.fetch — provider downloads INTO THE CACHE (Mission 2, 2026-11-18). Pure Python.
Provider files never go into git (they are big and re-downloadable); asset.json says what to fetch, this module fetches it once into
rc.cache ("download" entries, sha256 of every file in meta.json) and every later use is a cache hit, on this machine or on a pod volume.
  polyhaven_model(id, res="1k")  -> folder with <id>_<res>.gltf + its .bin + textures/ (the gltf "include" files: the step Asset Hub missed)
  polyhaven_maps(id, res="1k")   -> {"color","roughness","normal","ao","displacement"} -> file paths (jpg)
  ambientcg_maps(id, res="1K")   -> same keys, from the ambientCG JPG zip
Licences: Poly Haven and ambientCG are CC0 (recorded in asset.json). A client User-Agent is sent (PI-013)."""
import io, json, os, urllib.request, zipfile
from . import cache

UA = {"User-Agent": "RicksClips-rc/1.0 (asset fetch)"}
def _get(url, timeout=300): return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read()
def _api(path): return json.loads(_get("https://api.polyhaven.com/" + path, 60))

def polyhaven_model(aid, res="1k", log=print):
    def build(out):
        g = _api("files/" + aid)["gltf"][res]["gltf"]
        open(os.path.join(out, os.path.basename(g["url"])), "wb").write(_get(g["url"]))
        for rel, f in g.get("include", {}).items():
            p = os.path.join(out, rel); os.makedirs(os.path.dirname(p), exist_ok=True); open(p, "wb").write(_get(f["url"]))
    d = cache.get_or_build("download", {"provider": "polyhaven", "id": aid, "res": res, "fmt": "gltf"}, build, log=log)
    return os.path.join(d, [f for f in os.listdir(d) if f.endswith(".gltf")][0])

PH_MAPS = {"color": "Diffuse", "roughness": "Rough", "normal": "nor_gl", "ao": "AO", "displacement": "Displacement"}
def polyhaven_maps(aid, res="1k", log=print):
    def build(out):
        F = _api("files/" + aid)
        for k, key in PH_MAPS.items():
            if key in F and res in F[key] and "jpg" in F[key][res]: open(os.path.join(out, k + ".jpg"), "wb").write(_get(F[key][res]["jpg"]["url"]))
    d = cache.get_or_build("download", {"provider": "polyhaven", "id": aid, "res": res, "fmt": "maps-jpg"}, build, log=log)
    return {k: os.path.join(d, k + ".jpg") for k in PH_MAPS if os.path.exists(os.path.join(d, k + ".jpg"))}

AC_MAPS = {"color": "_Color.jpg", "roughness": "_Roughness.jpg", "normal": "_NormalGL.jpg", "ao": "_AmbientOcclusion.jpg", "displacement": "_Displacement.jpg"}
def ambientcg_maps(aid, res="1K", log=print):
    def build(out):
        z = zipfile.ZipFile(io.BytesIO(_get("https://ambientcg.com/get?file=%s_%s-JPG.zip" % (aid, res))))
        for n in z.namelist():
            for k, suf in AC_MAPS.items():
                if n.endswith(suf): open(os.path.join(out, k + ".jpg"), "wb").write(z.read(n))
    d = cache.get_or_build("download", {"provider": "ambientcg", "id": aid, "res": res, "fmt": "maps-jpg"}, build, log=log)
    return {k: os.path.join(d, k + ".jpg") for k in AC_MAPS if os.path.exists(os.path.join(d, k + ".jpg"))}

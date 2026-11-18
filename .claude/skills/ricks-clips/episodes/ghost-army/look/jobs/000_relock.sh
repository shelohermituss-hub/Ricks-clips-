# Stage 8 again on the pod after the lock fix (zero-scale instances wrote NaN rotations into the set GLBs): bake + export-lock, then a glTF parse check of every set
cd "$SKILL"
python3 tools/film_plan.py bake "$EP/film.json" | tail -1
ANG=""; for a in vulkan gl-egl; do if RICKCLIPS_GPU_ANGLE=$a timeout 180 node templates/threejs_film/render_gpu.mjs "$EP/film.json" --gpu-info > "$OUT/gpuinfo_$a.txt" 2>&1 && grep -qi nvidia "$OUT/gpuinfo_$a.txt"; then ANG=$a; break; fi; done
echo "angle: ${ANG:-software}"
RICKCLIPS_GPU_ANGLE=$ANG node templates/threejs_film/render_gpu.mjs "$EP/film.json" --export-lock $([ -z "$ANG" ] && echo --software) --cache /tmp/pc_relock > "$OUT/lock.log" 2>&1; echo "export-lock rc=$?"
grep -E "^set |^cards |highlights" "$OUT/lock.log"
cp "$EP/out/lock/lock.json" "$OUT/lock.json"
python3 - <<PY
import json, struct, glob
for f in sorted(glob.glob("$EP/out/lock/sets/*.glb")):
    b = open(f, 'rb').read(); L = struct.unpack('<I', b[12:16])[0]; J = json.loads(b[20:20 + L])
    bad = [i for i, a in enumerate(J['accessors']) if any(v is None for v in a.get('max', []) + a.get('min', []))]
    print("NANCHECK", f.split('/')[-1], "bad accessors:", len(bad))
PY

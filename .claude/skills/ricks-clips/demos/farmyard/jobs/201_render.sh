#!/usr/bin/env bash
# Farmyard demo, GPU render on the pod (deliverables 10 + 14). Run by scripts/runpod/blender_pod.sh with SKILL, EP, BLENDER, OUT set.
# 1 drawings (card service)  2 scene assembly (phases 1-9, same code and commit as local)  3 benchmark Cycles vs EEVEE on 3 frames
# 4 full sequence 540x960 Cycles GPU (slices, resume, manifest, gpu_usage.csv)  5 encode. Every output lands in OUT (published, fetched by pod.py).
set -eu
export RICKCLIPS_BLENDER="$BLENDER"; cd "$SKILL"; D="$EP"; B="$D/build"; mkdir -p "$B"
echo "== 1 cards"; python3 tools/card_service.py "$D/tracks.json" "$B" | tee "$OUT/cards.log"
echo "== 2 assemble"; t=$(date +%s)
"$BLENDER" -b --factory-startup --python-exit-code 3 --python blender/rc/cli.py -- assemble "$D/places/farmyard/place.json" "$B/scene.blend" --upto 9 > "$OUT/assemble.log" 2>&1
grep "^RC_RESULT" "$OUT/assemble.log" | cut -c11- > "$OUT/scene_report.json"; echo "assemble $(( $(date +%s) - t )) s"
echo "== 3 bench"; python3 tools/render_manager.py bench "$B/scene.blend" "$OUT/bench" --frames 60,200,380 --res 540x960 --samples 64 --gpu | tee "$OUT/bench.log"
echo "== 4 render"; python3 tools/render_manager.py render "$B/scene.blend" "$OUT/frames" --frames 0-449 --slice 30 --res 540x960 --samples 64 --gpu | tee "$OUT/render.log"
python3 tools/render_manager.py verify "$OUT/frames"
echo "== 5 encode"; python3 tools/render_manager.py encode "$OUT/frames" "$OUT/farmyard_gpu_540x960_silent.mp4" --fps 30
echo "JOB DONE"

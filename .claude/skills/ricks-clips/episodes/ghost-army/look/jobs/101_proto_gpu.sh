# Mission 2 prototype on GPU (runs on a blender_pod.sh pod; NEEDS CB APPROVAL before any pod is created).
# 1. rebuild the two prototype scenes from place.json (asset cache on the pod volume; card drawings via the card cache)
# 2. benchmark: the same 3 frames in EEVEE and in Cycles OPTIX at 540x960, timed, GPU utilisation sampled (gpu_usage.csv)
# 3. render both sequences on the faster engine whose quality passes, at 540x960, encode MP4s; manifest for pod.py fetch
set -u; cd "$SKILL"; B="$BLENDER -b --factory-startup --python-exit-code 3 --python blender/rc/cli.py --"; mkdir -p "$OUT/blend"
node templates/threejs_film/render_gpu.mjs "$EP/film.json" --export-lock --cards-only --who lou,carrier_tall,carrier_stocky,carrier_short,farmer,boy --card-frames 0-150 --lock-dir "$EP/out/proto_field/lock" --cache /tmp/pc_cards | grep "^cards"
for P in field field_crash_test; do $B assemble "$EP/places/$P/place.json" "$OUT/blend/$P.blend" | grep -E "RC_RESULT|Error" | cut -c1-300; done
for E in EEVEE CYCLES; do $B render "$OUT/blend/field.blend" "$OUT/bench_$E" 30,103,150 --engine $E --res 540x960 --samples 64 --gpu | grep RC_RESULT; done
$B render "$OUT/blend/field.blend" "$OUT/seq_field" 0-150 --engine ${RC_ENGINE:-CYCLES} --res 540x960 --samples 64 --gpu | grep RC_RESULT
$B render "$OUT/blend/field_crash_test.blend" "$OUT/seq_crash" 0-120 --engine ${RC_ENGINE:-CYCLES} --res 540x960 --samples 64 --gpu | grep RC_RESULT
for S in field crash; do ffmpeg -y -loglevel error -framerate 30 -start_number 0 -i "$OUT/seq_$S/f%05d.png" -c:v libx264 -crf 16 -pix_fmt yuv420p "$OUT/proto_$S.mp4"; done

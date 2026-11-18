# LookDev prototype job 001: baseline (from_lock, library materials only) + measured render times, 3 places x 2 engines
cd "$EP/look"
for spec in "field morning 285" "cafe interior 1245" "road night 945"; do set -- $spec
  for eng in CYCLES EEVEE; do "$BLENDER" -b --python smoke.py -- $1 $2 $3 $eng "$OUT/base_${1}_${eng}.png" 64 2>&1 | grep -E "SMOKE|Error|rror:" ; done
done

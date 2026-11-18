# LookDev prototype job 002: field, cafe, night road; look + clay + depth proofs, credits, step logs, timings
cd "$EP/look"; export PH_CACHE=/root/ph
for pl in field cafe road; do "$BLENDER" -b --python place_ld.py -- $pl "$OUT" 128 2>&1 | grep -E "STEP|PLACE DONE|Error|rror:|Traceback" ; done
ls "$OUT"

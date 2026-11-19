#!/usr/bin/env bash
# Restore, in a FRESH session, the files that are not in git but that the tests and the shots need (lesson PI-017).
# Idempotent: what is already there is skipped. Needs Blender 5.2 (scripts/cloud_environment_setup.sh) and the Sketchfab
# network secret on api.sketchfab.com. Does NOT restore CB's source video (ask CB) nor rendered frames (rebuilt by the shots).
#   bash scripts/restore_untracked.sh
set -e; SK=$(cd "$(dirname "$0")/.." && pwd); cd "$SK"
PY=python3; [ -x .venv/bin/python ] && PY=.venv/bin/python
say(){ printf '[restore] %s\n' "$*"; }
# 1. Sketchfab models (CC-BY): F1, sedan (crashed_car), vintage bicycle (library + test_rc), small SUV (crash_instinct)
#    The network secret for api.sketchfab.com must use the prefix "Token" when it is a Sketchfab API token (Bearer only for OAuth tokens).
for id in ca91852b29bb435d8d0278d9131aa775 58c33766470d46e7b2aed542650494e5 1795f6e907634afda88fdaf45f67b279 5db696c6ed5d4bdc87905c1040fa072a; do   # last one: white SUV of crash_instinct
  if [ -f library/assets/sketchfab/$id/gltf/scene.gltf ]; then say "sketchfab $id present"
  else say "sketchfab $id: downloading"; $PY tools/asset_hub.py download sketchfab $id >/dev/null; fi
done
# 2. library assets whose asset.json points at a converted glb/ file
for a in library/assets/sketchfab/*/asset.json; do
  f=$($PY -c "import json,sys;b=json.load(open(sys.argv[1])).get('build',{});print(b.get('file','') if b.get('type')=='file' else '')" "$a")
  d=$(dirname "$a")
  if [ -n "$f" ] && [ ! -f "$d/$f" ]; then say "converting $d -> $f"; blender -b --factory-startup --python tools/gltf_to_glb.py -- --asset "$d" 2>&1 | grep '^GLB'; fi
done
# 3. baked plan of the episode used by the card-cache test (episodes/*/out is not in git)
[ -f episodes/ghost-army/out/plan/camera_baked.json ] || (cd episodes/ghost-army && python3 ../../tools/film_plan.py bake film.json | tail -1)
say "done. Card drawings: python3 tools/card_service.py demos/crashed_car/tracks_sNN.json demos/crashed_car/build/cards_sNN (about 1.5 min per track)"

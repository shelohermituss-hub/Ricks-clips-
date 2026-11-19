#!/usr/bin/env bash
# Render one shot part in layers (CB rules 2026-11-19): build -> CONTINUITY CHECK (no render if it fails) -> split -> render each layer -> composite
#   bash demos/crashed_car/shots/render_layers.sh <part> <frames a-b> [production dir]   e.g.  s02_pit 122-205
#   another production (same layout: shots/<part>.py, build/):  ... s01_plant 0-95 demos/crash_instinct
set -e; SK=$(cd "$(dirname "$0")/../../.." && pwd); D=$(cd "${3:-$(dirname "$0")/..}" && pwd); part=$1; frames=$2; SHOTS=$SK/demos/crashed_car/shots
blender -b --factory-startup --python $D/shots/$part.py -- $D/build/$part.blend --res 270x480 --samples 12 >/dev/null 2>&1
mkdir -p $D/build/continuity
if ! blender -b $D/build/$part.blend --python $SHOTS/continuity.py -- $D/build/continuity/$part.json 2>&1 | grep -A20 "^CONTINUITY" ; then echo "no output"; exit 1; fi
python3 -c "import json,sys; sys.exit(0 if json.load(open('$D/build/continuity/$part.json'))['ok'] else 1)" || { echo "CONTINUITY FAIL: render refused, fix the shot first"; exit 1; }
blender -b --factory-startup --python $SHOTS/layers.py -- $D/build/$part.blend $D/build/${part}_layers 2>&1 | grep LAYERS
for L in SKY SET OBJECTS FX; do
  python3 $SK/tools/render_manager.py render $D/build/${part}_layers/$L.blend $D/build/${part}_layers/$L --frames $frames --slice 100 --res 270x480 --samples 12 2>&1 | tail -1 | cut -c1-120
done
python3 $SHOTS/layers.py comp $D/build/${part}_layers $frames $D/build/${part}_comp

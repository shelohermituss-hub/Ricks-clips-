#!/usr/bin/env bash
# QUICK PREVIEW of a whole shot on the cloud CPU (CB rule 2026-11-19, CB_RULES 11h "where each render runs"): build -> CONTINUITY CHECK
# (no preview if it fails) -> ONE layer (no split), 135x240, 4 samples, no motion blur -> <build>/<part>_preview.mp4. Real renders = GPU.
#   bash demos/crashed_car/shots/preview.sh <part> <frames a-b> [production dir]     e.g.  s02_crash 96-164 demos/crash_instinct
set -e; SK=$(cd "$(dirname "$0")/../../.." && pwd); D=$(cd "${3:-$(dirname "$0")/..}" && pwd); part=$1; frames=$2; SHOTS=$SK/demos/crashed_car/shots
a=${frames%-*}; b=${frames#*-}; T0=$(date +%s)
blender -b --factory-startup --python $D/shots/$part.py -- $D/build/$part.blend --res 135x240 --samples 4 >/dev/null 2>&1
mkdir -p $D/build/continuity
blender -b $D/build/$part.blend --python $SHOTS/continuity.py -- $D/build/continuity/$part.json 2>&1 | grep "^CONTINUITY" || { echo "no continuity output"; exit 1; }
python3 -c "import json,sys; sys.exit(0 if json.load(open('$D/build/continuity/$part.json'))['ok'] else 1)" || { echo "CONTINUITY FAIL: preview refused, fix the shot first"; exit 1; }
rm -rf $D/build/${part}_preview; mkdir -p $D/build/${part}_preview
blender -b $D/build/$part.blend --python-expr "import bpy; s=bpy.context.scene; s.render.use_motion_blur=False; s.cycles.samples=4; s.render.resolution_x=135; s.render.resolution_y=240; s.render.resolution_percentage=100; s.render.filepath='$D/build/${part}_preview/f'; s.render.image_settings.file_format='PNG'" -s $a -e $b -a >/dev/null 2>&1
ffmpeg -v error -y -framerate 30 -start_number $a -i $D/build/${part}_preview/f%04d.png -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" -c:v libx264 -pix_fmt yuv420p -crf 20 $D/build/${part}_preview.mp4 || { echo "ENCODE FAIL"; exit 1; }
echo "PREVIEW $D/build/${part}_preview.mp4  ($(ls $D/build/${part}_preview | wc -l) frames, $(( $(date +%s) - T0 )) s)"

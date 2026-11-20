#!/bin/bash
# render the preview frames of the given shots one after the other: shots/render_queue.sh 02 03 ...   (needs build/sNN.blend)
cd "$(dirname "$0")/.."
for s in "$@"; do
  if [ "$s" = "01" ]; then B=build/s01_button_v4.blend; else B=build/s$s.blend; fi
  blender -b $B --python shots/anim.py -- build/frames/s$s 3 8 > build/frames_s$s.log 2>&1; echo "s$s $(ls build/frames/s$s | wc -l) frames" >> build/frames_done.log
done

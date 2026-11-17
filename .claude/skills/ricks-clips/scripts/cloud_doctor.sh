#!/usr/bin/env bash
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; VENV="$ROOT/.venv"
PASS=0; WARN=0; FAIL=0
ok(){ echo "[PASS] $*"; PASS=$((PASS+1)); }
warn(){ echo "[WARN] $*"; WARN=$((WARN+1)); }
bad(){ echo "[FAIL] $*"; FAIL=$((FAIL+1)); }
checkbin(){ if command -v "$1" >/dev/null 2>&1; then ok "$1: $("$1" --version 2>&1 | head -n 1)"; else bad "$1 not found"; fi; }
for b in python3 node npm blender ffmpeg ffprobe; do checkbin "$b"; done
if [ -x /usr/bin/google-chrome ]; then ok "Chrome: $(/usr/bin/google-chrome --version 2>&1 | head -n1)"; else warn 'System Chrome missing; browser rendering may need a separate Playwright browser install.'; fi
if [ -x "$VENV/bin/python" ]; then
  "$VENV/bin/python" -c "import importlib; mods=['PIL','numpy','scipy','soundfile','faster_whisper','cv2']; [print('[PASS] Python module:',m,getattr(importlib.import_module(m),'__version__','')) for m in mods]"     && ok 'Python dependency imports' || bad 'One or more Python dependencies do not import'
else bad 'Python virtual environment missing; run scripts/cloud_session_start.sh'; fi
[ -d "$ROOT/templates/threejs_film/node_modules/playwright" ] && ok 'Playwright npm package present' || bad 'Playwright npm package missing'
[ -d "$ROOT/templates/threejs_film/node_modules/three" ] && ok 'Three.js npm package present' || bad 'Three.js npm package missing'
if [ -d "$ROOT/templates/threejs_film/node_modules/playwright" ] && command -v node >/dev/null 2>&1; then
  if node "$ROOT/scripts/cloud_browser_smoke.mjs"; then ok 'Headless Chrome/Playwright/WebGL smoke test'; else bad 'Headless Chrome/Playwright/WebGL smoke test failed'; fi
fi
if command -v blender >/dev/null 2>&1; then
  blender -b --factory-startup --python-expr "import bpy; print('RICKCLIPS_BLENDER_OK', bpy.app.version_string)" >/tmp/ricksclips-blender-check.log 2>&1
  if grep -q 'RICKCLIPS_BLENDER_OK' /tmp/ricksclips-blender-check.log; then ok "Blender background Python works: $(grep 'RICKCLIPS_BLENDER_OK' /tmp/ricksclips-blender-check.log | tail -n1)"; else bad 'Blender background Python smoke test failed'; tail -n 18 /tmp/ricksclips-blender-check.log; fi
  case "$(blender --version 2>/dev/null | head -n1)" in "Blender 5.2"*) ;; *) warn 'Blender is not the 5.2 LTS the pipeline is audited on; rerun scripts/cloud_environment_setup.sh (needs download.blender.org allowed).';; esac
fi
if command -v nvidia-smi >/dev/null 2>&1 && nvidia-smi -L >/dev/null 2>&1; then ok 'NVIDIA GPU detected'; else warn 'No NVIDIA GPU detected; use --software for previews. This is not a GPU render host.'; fi
printf '\nRicksClips Cloud Doctor: PASS=%s WARN=%s FAIL=%s\n' "$PASS" "$WARN" "$FAIL"
[ "$FAIL" -eq 0 ]

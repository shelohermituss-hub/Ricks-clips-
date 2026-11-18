#!/usr/bin/env bash
# Runs INSIDE a RunPod GPU pod started by scripts/runpod/pod.py --script lookdev_pod.sh (2026-11-18, Ghost Army LookDev prototype).
# A small job runner for the Blender look pass (pipeline stage 9):
#   1. setup: GPU user-space libs, node + playwright, Blender 5.2.2 LTS (download.blender.org, sha256 checked), the repo branch
#   2. stage 8 on the pod: film_plan bake + render_gpu.mjs --export-lock (same commit = same lock as the local one)
#   3. loop: every 30 s `git pull` the branch; every job file episodes/<ep>/look/jobs/NNN_*.sh not run yet is run once, in order,
#      with SKILL, EP, BLENDER, OUT (= the published folder of that job) in its environment; its log and outputs are published.
# Published read-only at http://<pod>:8000/<RICKCLIPS_PUB_KEY>/ (status.json, setup.log, jobs/<NNN>/...).
# Watchdog: RICKCLIPS_MAX_HOURS (the pod removes itself after that, budget cap).
set -u
SKILL=/root/repo/.claude/skills/ricks-clips; EP="$SKILL/${RICKCLIPS_EPISODE:?}"; PUB=/root/pub/${RICKCLIPS_PUB_KEY:?}; BR=${RICKCLIPS_BRANCH:-main}
mkdir -p "$PUB/jobs"; : > /root/pub/index.html; LOG="$PUB/setup.log"; exec > >(tee -a "$LOG") 2>&1
T0=$(date +%s)
st(){ printf '{"stage":"%s","msg":"%s","elapsed_s":%d,"time":"%s"}\n' "$1" "${2:-}" $(( $(date +%s) - T0 )) "$(date -u +%FT%TZ)" > "$PUB/status.json.tmp" && mv "$PUB/status.json.tmp" "$PUB/status.json"; echo "[status] $1 ${2:-}"; }
fail(){ st failed "$1"; echo "FAILED: $1"; sleep infinity; }
(cd /root/pub && nohup python3 -m http.server 8000 --bind 0.0.0.0 >/dev/null 2>&1 &)
( sleep $(( ${RICKCLIPS_MAX_HOURS:-3} * 3600 )); st watchdog "max time reached, removing pod"; command -v runpodctl >/dev/null && runpodctl remove pod "${RUNPOD_POD_ID:-}" ) &
export DEBIAN_FRONTEND=noninteractive XDG_RUNTIME_DIR=/tmp/xdg; mkdir -p -m 700 $XDG_RUNTIME_DIR
st setup "apt (GPU libs, X11 for Blender)"
apt-get update -qq && apt-get install -y -qq ffmpeg curl xz-utils bc git libvulkan1 vulkan-tools libegl1 libgl1 libgles2 libglvnd0 libglx0 libx11-6 libxext6 libxcb1 libx11-xcb1 \
  libxrandr2 libxkbcommon0 libxi6 libxrender1 libxfixes3 libxxf86vm1 libsm6 libice6 libxkbcommon-x11-0 mesa-utils >/dev/null || fail "apt"
nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader > "$PUB/gpu.txt" || true
st setup "node + playwright"
curl -fsSL https://nodejs.org/dist/v22.11.0/node-v22.11.0-linux-x64.tar.xz | tar -xJ -C /opt && export PATH=/opt/node-v22.11.0-linux-x64/bin:$PATH || fail "node"
(cd "$SKILL/templates/threejs_film" && npm install --no-audit --no-fund >/dev/null && npx playwright install --with-deps chromium >/dev/null) || fail "npm/playwright"
st setup "Blender 5.2.2"
BV=5.2.2; BT=blender-$BV-linux-x64.tar.xz; cd /tmp && curl -fsSL -O https://download.blender.org/release/Blender5.2/$BT && curl -fsSL https://download.blender.org/release/Blender5.2/blender-$BV.sha256 | grep " $BT\$" > bl.sha \
  && sha256sum -c bl.sha && tar -xJf $BT -C /opt || fail "blender download"
BLENDER=/opt/blender-$BV-linux-x64/blender; $BLENDER --version | head -1 | tee "$PUB/blender.txt"
$BLENDER -b --python-expr "import bpy; p=bpy.context.preferences.addons['cycles'].preferences; p.compute_device_type='OPTIX'; p.get_devices(); print('CYCLES_DEVICES', [(d.name,d.type) for d in p.devices])" 2>&1 | grep CYCLES_DEVICES | tee -a "$PUB/blender.txt"
python3 -m pip install -q numpy pillow >/dev/null 2>&1 || true
st lock "film_plan bake + export-lock (stage 8)"
python3 "$SKILL/tools/film_plan.py" bake "$EP/film.json" | tail -2
ANG=""; for a in vulkan gl-egl; do if RICKCLIPS_GPU_ANGLE=$a timeout 180 node "$SKILL/templates/threejs_film/render_gpu.mjs" "$EP/film.json" --gpu-info > "$PUB/gpuinfo_$a.txt" 2>&1 && grep -qi nvidia "$PUB/gpuinfo_$a.txt"; then ANG=$a; break; fi; done
echo "webgl angle: ${ANG:-software}" | tee -a "$PUB/blender.txt"
RICKCLIPS_GPU_ANGLE=$ANG node "$SKILL/templates/threejs_film/render_gpu.mjs" "$EP/film.json" --export-lock ${ANG:+} $([ -z "$ANG" ] && echo --software) --cache /tmp/pc_lock > "$PUB/lock.log" 2>&1 || fail "export-lock"
grep -E "^set |^cards |highlights" "$PUB/lock.log" | tail -30; cp "$EP/out/lock/lock.json" "$PUB/lock.json" 2>/dev/null
export SKILL EP BLENDER
st ready "waiting for jobs in look/jobs"
while :; do
  (cd /root/repo && git fetch -q origin "$BR" && git reset -q --hard FETCH_HEAD) || true
  for j in $(ls "$EP"/look/jobs/[0-9][0-9][0-9]_*.sh 2>/dev/null | sort); do
    id=$(basename "$j" .sh); [ -e "$PUB/jobs/$id/done" ] && continue
    mkdir -p "$PUB/jobs/$id"; st job "$id running"; t=$(date +%s)
    OUT="$PUB/jobs/$id" bash "$j" > "$PUB/jobs/$id/log.txt" 2>&1; rc=$?
    printf '{"rc":%d,"seconds":%d}\n' $rc $(( $(date +%s) - t )) > "$PUB/jobs/$id/done"; ls "$PUB/jobs/$id" > "$PUB/jobs/$id/files.txt"
    st ready "$id finished rc=$rc"
  done
  sleep 30
done

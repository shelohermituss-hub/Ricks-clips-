#!/usr/bin/env bash
# Runs INSIDE a RunPod GPU pod started by scripts/runpod/pod.py (2026-11-17).
# Renders one episode at 1080x1920 / 30 fps, muxes the episode's sound mix, uploads the MP4 to GoFile and verifies the
# download (sha256), and publishes its progress, log and result read-only at  http://<pod>:8000/<RICKCLIPS_PUB_KEY>/
# (RunPod proxy: https://<podId>-8000.proxy.runpod.net/<key>/status.json). Env: RICKCLIPS_EPISODE (path from the skill root),
# RICKCLIPS_PUB_KEY (random), RICKCLIPS_MAX_HOURS (watchdog, default 3: the pod deletes itself after that, if runpodctl is present).
set -u
SKILL=/root/repo/.claude/skills/ricks-clips; EP="$SKILL/${RICKCLIPS_EPISODE:?}"; PUB=/root/pub/${RICKCLIPS_PUB_KEY:?}
mkdir -p "$PUB"; : > /root/pub/index.html; LOG="$PUB/render.log"; exec > >(tee -a "$LOG") 2>&1
T0=$(date +%s)
st(){ printf '{"stage":"%s","msg":"%s","elapsed_s":%d,"time":"%s"}\n' "$1" "${2:-}" $(( $(date +%s) - T0 )) "$(date -u +%FT%TZ)" > "$PUB/status.json.tmp" && mv "$PUB/status.json.tmp" "$PUB/status.json"; echo "[status] $1 ${2:-}"; }
fail(){ st failed "$1"; echo "FAILED: $1"; sleep infinity; }
(cd /root/pub && nohup python3 -m http.server 8000 --bind 0.0.0.0 >/dev/null 2>&1 &)
( sleep $(( ${RICKCLIPS_MAX_HOURS:-3} * 3600 )); st watchdog "max time reached, removing pod"; command -v runpodctl >/dev/null && runpodctl remove pod "${RUNPOD_POD_ID:-}" ) &
st setup "apt + node + playwright"
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq && apt-get install -y -qq ffmpeg curl xz-utils libvulkan1 vulkan-tools >/dev/null || fail "apt"
nvidia-smi -L; nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader > "$PUB/gpu.txt" || true
curl -fsSL https://nodejs.org/dist/v22.11.0/node-v22.11.0-linux-x64.tar.xz | tar -xJ -C /opt && export PATH=/opt/node-v22.11.0-linux-x64/bin:$PATH || fail "node"
node --version; ffmpeg -version | head -1
cd "$SKILL/templates/threejs_film" && npm install --no-audit --no-fund >/dev/null && npx playwright install --with-deps chromium >/dev/null || fail "npm/playwright"
st plan "film_plan check"
python3 "$SKILL/tools/film_plan.py" check "$EP/film.json" | tail -3 || fail "film_plan"
N=$(python3 -c "import json;print(json.load(open('$EP/film.json'))['end'])")
# GPU: ANGLE Vulkan, then EGL; keep the first that is really the NVIDIA card (render_gpu.mjs refuses a CPU renderer with exit 2)
MODE=software; ANG=""
for a in vulkan gl; do
  if RICKCLIPS_GPU_ANGLE=$a timeout 180 node render_gpu.mjs "$EP/film.json" --gpu-info > "$PUB/gpuinfo_$a.txt" 2>&1 && grep -qi nvidia "$PUB/gpuinfo_$a.txt"; then MODE=gpu; ANG=$a; break; fi
done
grep -h "WebGL renderer" "$PUB"/gpuinfo_*.txt; echo "render mode: $MODE $ANG"
if [ "$MODE" = gpu ]; then K=${RICKCLIPS_PROCS:-3}; EXTRA=""; else K=${RICKCLIPS_PROCS:-$(( $(nproc) / 4 > 2 ? $(nproc) / 4 : 2 ))}; EXTRA="--software"; fi
FR=/root/frames; rm -rf "$FR"; mkdir -p "$FR"; st render "mode=$MODE angle=$ANG procs=$K frames=$N"
TR0=$(date +%s); pids=()
for i in $(seq 0 $((K-1))); do a=$(( N * i / K )); b=$(( N * (i+1) / K - 1 ))
  RICKCLIPS_GPU_ANGLE=$ANG node render_gpu.mjs "$EP/film.json" --frames $a-$b --scale 1 --seed 7 --stills-dir "$FR" --cache /tmp/pc_$i $EXTRA > "$PUB/render_part$i.log" 2>&1 & pids+=($!); done
while :; do n=$(ls "$FR" | wc -l); st render "mode=$MODE angle=$ANG procs=$K frames $n/$N"; alive=0; for p in "${pids[@]}"; do kill -0 $p 2>/dev/null && alive=1; done; [ $alive = 0 ] && break; sleep 20; done
TR=$(( $(date +%s) - TR0 )); n=$(ls "$FR" | wc -l); [ "$n" -eq "$N" ] || fail "only $n of $N frames rendered (see render_part*.log)"
st encode "render ${TR}s for $N frames"
ffmpeg -nostdin -loglevel error -y -framerate 30 -i "$FR/f_%05d.png" -i "$EP/sound/mix.flac" -map 0:v -map 1:a -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -r 30 \
  -c:a aac -b:a 192k -ar 48000 -shortest -movflags +faststart "$PUB/final.mp4" || fail "ffmpeg"
ffprobe -v error -show_entries stream=codec_name,width,height,avg_frame_rate,nb_frames:format=duration,size -of json "$PUB/final.mp4" > "$PUB/probe.json"
printf '{"mode":"%s","angle":"%s","procs":%d,"frames":%d,"render_s":%d,"s_per_frame":%.3f}\n' "$MODE" "$ANG" "$K" "$N" "$TR" "$(echo "$TR / $N" | bc -l 2>/dev/null || echo 0)" > "$PUB/render.json"
sha256sum "$PUB/final.mp4" | cut -d' ' -f1 > "$PUB/final.sha256"
st upload "GoFile"
python3 "$SKILL/scripts/runpod/gofile_upload_verify.py" "$PUB/final.mp4" "$PUB/gofile.json" || st upload_failed "see gofile.json"
st done "$(python3 -c "import json;d=json.load(open('$PUB/gofile.json'));print(d.get('downloadPage',''), 'verified' if d.get('verified') else 'NOT verified')" 2>/dev/null)"
sleep infinity

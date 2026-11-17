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
# RunPod containers expose CUDA but not the NVIDIA graphics libraries (Vulkan ICD / EGL): Chrome then falls back to SwiftShader.
# Install the user-space part of the SAME driver version as the host (no kernel module), so ANGLE can reach the card.
DRV=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -1 | tr -d ' ')
if [ -n "$DRV" ] && [ ! -e /usr/share/vulkan/icd.d/nvidia_icd.json ] && [ ! -e /etc/vulkan/icd.d/nvidia_icd.json ]; then
  st setup "installing NVIDIA user-space graphics driver $DRV"
  apt-get install -y -qq kmod pkg-config libglvnd-dev >/dev/null 2>&1 || true
  if curl -fsSL -o /tmp/nv.run "https://us.download.nvidia.com/XFree86/Linux-x86_64/$DRV/NVIDIA-Linux-x86_64-$DRV.run" || curl -fsSL -o /tmp/nv.run "https://us.download.nvidia.com/tesla/$DRV/NVIDIA-Linux-x86_64-$DRV.run"; then
    sh /tmp/nv.run --silent --no-kernel-module --no-kernel-modules --no-x-check --no-nouveau-check --no-systemd --no-questions --ui=none --install-libglvnd > "$PUB/nvidia_install.log" 2>&1 \
      || sh /tmp/nv.run --silent --no-kernel-module --no-x-check --no-nouveau-check --no-systemd --no-questions --ui=none >> "$PUB/nvidia_install.log" 2>&1 || true
  else echo "NVIDIA driver $DRV download failed" | tee "$PUB/nvidia_install.log"; fi
  ls /usr/share/vulkan/icd.d/ /etc/vulkan/icd.d/ 2>/dev/null; vulkaninfo --summary 2>&1 | grep -iE "deviceName|driverName" | head -4
fi
# Mounted NVIDIA libs without their loader files: write the EGL vendor file and the Vulkan ICD so ANGLE can find the card.
LEGL=$(ldconfig -p | grep -oE '/[^ ]*libEGL_nvidia\.so\.0' | head -1); LGLX=$(ldconfig -p | grep -oE '/[^ ]*libGLX_nvidia\.so\.0' | head -1)
mkdir -p /usr/share/glvnd/egl_vendor.d /usr/share/vulkan/icd.d
[ -n "$LEGL" ] && ! ls /usr/share/glvnd/egl_vendor.d/*nvidia* /etc/glvnd/egl_vendor.d/*nvidia* 2>/dev/null | grep -q . && printf '{"file_format_version":"1.0.0","ICD":{"library_path":"libEGL_nvidia.so.0"}}\n' > /usr/share/glvnd/egl_vendor.d/10_nvidia.json
[ -n "$LGLX" ] && ! ls /usr/share/vulkan/icd.d/*nvidia* /etc/vulkan/icd.d/*nvidia* 2>/dev/null | grep -q . && printf '{"file_format_version":"1.0.0","ICD":{"library_path":"libGLX_nvidia.so.0","api_version":"1.3.0"}}\n' > /usr/share/vulkan/icd.d/nvidia_icd.json
{ echo "libEGL_nvidia=$LEGL libGLX_nvidia=$LGLX"; ls -la /usr/share/glvnd/egl_vendor.d /usr/share/vulkan/icd.d /etc/vulkan/icd.d 2>&1; ldconfig -p | grep -iE "nvidia" | sort; vulkaninfo --summary 2>&1 | grep -iE "deviceName|driverName|ERROR" | head -6; } > "$PUB/gpu_diag.txt" 2>&1
# GPU (proved on an RTX 4090 pod 2026-11-17, scripts/runpod/gpu_diag.sh): ANGLE Vulkan + --disable-vulkan-surface and ANGLE gl-egl both reach the card;
# Vulkan WITHOUT --disable-vulkan-surface gives no WebGL2 in headless Chromium. Try them in that order; keep the first that is
# really the NVIDIA card (render_gpu.mjs refuses a CPU renderer with exit 2)
MODE=software; ANG=""
for a in vulkan gl-egl; do
  if RICKCLIPS_GPU_ANGLE=$a timeout 180 node render_gpu.mjs "$EP/film.json" --gpu-info > "$PUB/gpuinfo_$a.txt" 2>&1 && grep -qi nvidia "$PUB/gpuinfo_$a.txt"; then MODE=gpu; ANG=$a; break; fi
done
grep -h "WebGL renderer" "$PUB"/gpuinfo_*.txt; echo "render mode: $MODE $ANG"
if [ "$MODE" = gpu ]; then K=${RICKCLIPS_PROCS:-3}; EXTRA=""; else K=${RICKCLIPS_PROCS:-$(( $(nproc) / 8 > 2 ? $(nproc) / 8 : 2 ))}; EXTRA="--software"; fi
FR=/root/frames; rm -rf "$FR"; mkdir -p "$FR"; echo "cpus: $(nproc)"; st render "mode=$MODE angle=$ANG procs=$K frames=$N"
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

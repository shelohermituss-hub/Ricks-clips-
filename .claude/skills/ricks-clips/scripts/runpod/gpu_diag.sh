#!/usr/bin/env bash
# GPU diagnostic for RunPod (2026-11-17): why Chrome/ANGLE sees SwiftShader instead of the NVIDIA card, and which fix works.
# Started by pod.py with --diag; publishes diag.txt under the same read-only status page as render_pod.sh.
set -u
SKILL=/root/repo/.claude/skills/ricks-clips; PUB=/root/pub/${RICKCLIPS_PUB_KEY:?}; mkdir -p "$PUB"; : > /root/pub/index.html
exec > >(tee -a "$PUB/diag.txt") 2>&1
(cd /root/pub && nohup python3 -m http.server 8000 --bind 0.0.0.0 >/dev/null 2>&1 &)
( sleep 3600; command -v runpodctl >/dev/null && runpodctl remove pod "${RUNPOD_POD_ID:-}" ) &
echo '{"stage":"diag","msg":"running"}' > "$PUB/status.json"
sec(){ echo; echo "===== $*"; }
sec env; env | grep -iE "nvidia|cuda" | sort
sec nvidia-smi; nvidia-smi --query-gpu=name,driver_version --format=csv
sec icd/egl files; ls -la /usr/share/vulkan/icd.d /etc/vulkan/icd.d /usr/share/glvnd/egl_vendor.d /etc/glvnd/egl_vendor.d 2>&1; cat /usr/share/vulkan/icd.d/*.json /etc/vulkan/icd.d/*.json 2>/dev/null
sec nvidia libs; ldconfig -p | grep -iE "nvidia|libEGL|libGLX|libvulkan" | sort
export DEBIAN_FRONTEND=noninteractive; apt-get update -qq >/dev/null; apt-get install -y -qq curl xz-utils libvulkan1 vulkan-tools libegl1 libgl1 libgles2 libglvnd0 libglx0 libx11-6 libxext6 libxcb1 libx11-xcb1 libxrandr2 libxkbcommon0 mesa-utils >/dev/null 2>&1; export XDG_RUNTIME_DIR=/tmp/xdg; mkdir -p -m 700 $XDG_RUNTIME_DIR   # same GPU packages as render_pod.sh
sec vulkaninfo before; vulkaninfo --summary 2>&1 | grep -iE "deviceName|driverName|apiVersion|ERROR" | head -8
curl -fsSL https://nodejs.org/dist/v22.11.0/node-v22.11.0-linux-x64.tar.xz | tar -xJ -C /opt; export PATH=/opt/node-v22.11.0-linux-x64/bin:$PATH
cd "$SKILL/templates/threejs_film" && npm install --no-audit --no-fund >/dev/null 2>&1 && npx playwright install --with-deps chromium >/dev/null 2>&1
cat > /tmp/probe.mjs <<'JS'
import { createRequire } from 'module'; const require = createRequire(process.cwd() + '/'); const { chromium } = require('playwright');
const V = ['--use-angle=vulkan','--use-gl=angle','--enable-features=Vulkan,VulkanFromANGLE,DefaultANGLEVulkan'];
const sets = { vulkan: V, vulkan_nosurface: [...V, '--disable-vulkan-surface'], vulkan_nosurface_ozone: [...V, '--disable-vulkan-surface', '--ozone-platform=headless'], gl_egl: ['--use-angle=gl-egl','--use-gl=angle'], egl: ['--use-gl=egl'] };
for (const [k, a] of Object.entries(sets)) for (const hl of [true, 'new-shell']) { try {
  const b = await chromium.launch({ channel: hl === true ? 'chromium' : undefined, headless: true, args: [...a, '--no-sandbox', '--enable-gpu', '--ignore-gpu-blocklist', '--disable-dev-shm-usage', '--enable-logging=stderr', '--v=0'] });
  const p = await b.newPage(); const r = await p.evaluate(() => { const c = document.createElement('canvas'), g = c.getContext('webgl2'); if (!g) return 'NO WEBGL2'; const e = g.getExtension('WEBGL_debug_renderer_info'); return e ? g.getParameter(e.UNMASKED_RENDERER_WEBGL) : 'masked'; });
  console.log(`${k} [${hl === true ? 'chromium-channel' : 'headless-shell'}]: ${r}`); await b.close(); } catch (e) { console.log(`${k} [${hl}]: ERROR ${String(e.message).split('\n')[0]}`); } }
JS
sec chrome probes before driver install; node /tmp/probe.mjs 2>&1 | grep -vE "^\[|GL Driver" | head -20
sec "fix A: write missing EGL vendor / Vulkan ICD files for the NVIDIA libs already mounted"
L=$(ldconfig -p | grep -oE '/[^ ]*libEGL_nvidia\.so\.0' | head -1); G=$(ldconfig -p | grep -oE '/[^ ]*libGLX_nvidia\.so\.0' | head -1); echo "libEGL_nvidia=$L libGLX_nvidia=$G"
mkdir -p /usr/share/glvnd/egl_vendor.d /usr/share/vulkan/icd.d
[ -n "$L" ] && ! ls /usr/share/glvnd/egl_vendor.d/*nvidia* >/dev/null 2>&1 && printf '{"file_format_version":"1.0.0","ICD":{"library_path":"libEGL_nvidia.so.0"}}\n' > /usr/share/glvnd/egl_vendor.d/10_nvidia.json && echo "wrote 10_nvidia.json"
[ -n "$G" ] && ! ls /usr/share/vulkan/icd.d/*nvidia* /etc/vulkan/icd.d/*nvidia* >/dev/null 2>&1 && printf '{"file_format_version":"1.0.0","ICD":{"library_path":"libGLX_nvidia.so.0","api_version":"1.3.0"}}\n' > /usr/share/vulkan/icd.d/nvidia_icd.json && echo "wrote nvidia_icd.json"
sec vulkaninfo after fix A; vulkaninfo --summary 2>&1 | grep -iE "deviceName|driverName|ERROR" | head -8
sec chrome probes after fix A; node /tmp/probe.mjs 2>&1 | grep -vE "^\[|GL Driver" | head -20
DRV=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -1 | tr -d ' ')
sec "fix B: install NVIDIA user-space $DRV"
for u in "https://us.download.nvidia.com/XFree86/Linux-x86_64/$DRV/NVIDIA-Linux-x86_64-$DRV.run" "https://us.download.nvidia.com/tesla/$DRV/NVIDIA-Linux-x86_64-$DRV.run"; do curl -fsSL -o /tmp/nv.run "$u" && { echo "got $u"; break; }; done
if [ -s /tmp/nv.run ]; then apt-get install -y -qq kmod pkg-config >/dev/null 2>&1
  sh /tmp/nv.run --silent --no-kernel-modules --no-x-check --no-nouveau-check --no-systemd --no-questions --ui=none 2>&1 | tail -5 || true
  sh /tmp/nv.run --silent --no-kernel-module --no-x-check --no-nouveau-check --no-systemd --no-questions --ui=none 2>&1 | tail -5 || true
  tail -20 /var/log/nvidia-installer.log 2>/dev/null; fi
sec nvidia libs after; ldconfig -p | grep -iE "nvidia|libEGL_nv|libGLX_nv" | sort | head -30
sec vulkaninfo after; vulkaninfo --summary 2>&1 | grep -iE "deviceName|driverName|ERROR" | head -8
sec chrome probes after driver install; node /tmp/probe.mjs 2>&1 | grep -vE "^\[|GL Driver" | head -20
echo '{"stage":"diag_done","msg":"see diag.txt"}' > "$PUB/status.json"; sleep infinity

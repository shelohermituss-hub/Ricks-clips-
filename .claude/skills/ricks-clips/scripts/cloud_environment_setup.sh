#!/usr/bin/env bash
# Upload this file once as Claude Code Web > Cloud environment > Setup script.
# Installs Blender 5.2.2 LTS (the version the pipeline is built and audited on) from download.blender.org,
# FFmpeg and the system libraries Blender needs. Falls back to the distro's Blender if blender.org is unreachable.
# Needs download.blender.org in the environment's Allowed domains.
set -u
export DEBIAN_FRONTEND=noninteractive
say(){ printf '[RicksClips cloud setup] %s\n' "$*"; }
BL_VER="${RICKSCLIPS_BLENDER_VERSION:-5.2.2}"; BL_SERIES="${BL_VER%.*}"
BL_DIR="/opt/blender-$BL_VER-linux-x64"
is_root(){ [ "$(id -u)" -eq 0 ]; }
if command -v apt-get >/dev/null 2>&1 && is_root; then
  pkgs=(ffmpeg libsndfile1 libgl1 libegl1 libxi6 libxrender1 libxext6 libxkbcommon0 libsm6 libice6 libxxf86vm1 libxfixes3 xz-utils ca-certificates curl)
  say "Installing system packages: ${pkgs[*]}"
  apt-get update -qq >/tmp/ricksclips-apt.log 2>&1 && apt-get install -y --no-install-recommends "${pkgs[@]}" >>/tmp/ricksclips-apt.log 2>&1 \
    || { say 'WARNING: apt failed; last log lines:'; tail -n 35 /tmp/ricksclips-apt.log 2>/dev/null || true; }
else say 'WARNING: apt-get/root unavailable; cannot install system packages.'; fi
if [ -x "$BL_DIR/blender" ]; then say "Blender $BL_VER already installed in $BL_DIR"
elif is_root && command -v curl >/dev/null 2>&1; then
  URL="https://download.blender.org/release/Blender$BL_SERIES"; TAR="blender-$BL_VER-linux-x64.tar.xz"; TMPD="$(mktemp -d)"
  say "Downloading Blender $BL_VER from $URL"
  if curl -fsSL -o "$TMPD/$TAR" "$URL/$TAR" && curl -fsSL "$URL/blender-$BL_VER.sha256" | grep " $TAR\$" > "$TMPD/sum" \
     && [ -s "$TMPD/sum" ] && (cd "$TMPD" && sha256sum -c sum >/dev/null) && tar -xJf "$TMPD/$TAR" -C /opt; then
    say "Blender $BL_VER installed and checksum verified"
  else say "WARNING: official Blender $BL_VER download/verification failed"; fi
  rm -rf "$TMPD"
fi
if [ -x "$BL_DIR/blender" ] && is_root; then ln -sfn "$BL_DIR" /opt/blender; ln -sf /opt/blender/blender /usr/local/bin/blender
elif ! command -v blender >/dev/null 2>&1 && command -v apt-get >/dev/null 2>&1 && is_root; then
  say 'Falling back to the distro Blender package (older than the pipeline version; check cloud_doctor output)'
  apt-get install -y --no-install-recommends blender >>/tmp/ricksclips-apt.log 2>&1 || say 'WARNING: apt blender failed'
fi
for bin in python3 node npm blender ffmpeg ffprobe; do
  if command -v "$bin" >/dev/null 2>&1; then say "FOUND $bin: $(command -v "$bin")"; else say "MISSING $bin"; fi
done
command -v blender >/dev/null 2>&1 && say "Blender version: $(blender --version 2>/dev/null | head -n1)"
if [ -x /usr/bin/google-chrome ]; then say 'FOUND Chrome for Testing: /usr/bin/google-chrome'; else say 'WARNING: system Chrome not found'; fi
say 'System setup finished. Project Python/npm packages are installed by the repository SessionStart hook.'
# Exit zero so a transient mirror failure does not block the session; cloud_doctor reports missing tools.
exit 0

#!/usr/bin/env bash
# Installs RicksClips packages only inside Claude Code Web sessions.
set -u
[ "${CLAUDE_CODE_REMOTE:-}" = "true" ] || exit 0
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="$ROOT/.venv"; MARKER="$ROOT/.cloud-deps.sha256"
REQ="$ROOT/requirements-cloud.txt"; PKG="$ROOT/templates/threejs_film/package.json"; LOCK="$ROOT/templates/threejs_film/package-lock.json"
HASH="$(sha256sum "$REQ" "$PKG" "$LOCK" "${BASH_SOURCE[0]}" 2>/dev/null | sha256sum | awk '{print $1}')"
if [ -n "$HASH" ] && [ -f "$MARKER" ] && [ "$(cat "$MARKER" 2>/dev/null)" = "$HASH" ] && [ -x "$VENV/bin/python" ] && [ -d "$ROOT/templates/threejs_film/node_modules/playwright" ] && [ -d "$ROOT/templates/threejs_film/node_modules/three" ]; then
  echo '[RicksClips] Dependencies already match project inputs.'; exit 0
fi
fail=0
python3 -m venv "$VENV" || fail=1
if [ "$fail" -eq 0 ]; then "$VENV/bin/python" -m pip install --disable-pip-version-check -r "$REQ" || fail=1; fi
if [ "$fail" -eq 0 ] && command -v npm >/dev/null 2>&1; then
  (cd "$ROOT/templates/threejs_film" && PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm install --no-audit --no-fund) || fail=1
else [ "$fail" -ne 0 ] || { echo '[RicksClips] WARNING: npm missing.' >&2; fail=1; }; fi
if [ "$fail" -eq 0 ]; then
  sha256sum "$REQ" "$PKG" "$LOCK" "${BASH_SOURCE[0]}" 2>/dev/null | sha256sum | awk '{print $1}' > "$MARKER"
  echo '[RicksClips] Python and Three.js/Playwright dependencies installed.'
else rm -f "$MARKER"; echo '[RicksClips] WARNING: dependency installation failed; inspect output and rerun this script.' >&2; fi
# Do not block Claude startup on a temporary package mirror issue. Run cloud_doctor.sh to see exact failures.
exit 0

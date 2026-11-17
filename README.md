# RicksClips — Claude Code Web Edition

Regular Claude Code project Skill release.

## Quick install
1. Push this entire folder, including hidden `.claude/`, to GitHub.
2. In Claude Code Web, connect GitHub and open a session on this repository.
3. Configure one Cloud Environment: upload `.claude/skills/ricks-clips/scripts/cloud_environment_setup.sh` as its Setup script; select Limited network access with package managers enabled; add hosts from `.claude/skills/ricks-clips/CLOUD_NETWORK_DOMAINS.txt`.
4. Start a fresh cloud session. The setup script installs Blender/FFmpeg; the repository SessionStart hook installs Python/npm dependencies.
5. Invoke `/ricks-clips` and ask Claude to install, run the cloud doctor and all offline tests.

Read `.claude/skills/ricks-clips/CLOUD_MODE.md` for detailed configuration, secrets, commands and render limitations.

## Important
The hosted VM is CPU-limited and has no guaranteed GPU. It does not inherit your Windows GPU or BlenderKit login. Software WebGL previews and headless Blender operations are supported; long full-resolution renders may need your local GPU workstation or a GPU runner. The Skill must measure and report actual results.

The original Windows installer remains at `.claude/skills/ricks-clips/install.py` for local use only.

# RicksClips — Claude Code Web runtime

## Included

- Normal project Skill: `.claude/skills/ricks-clips/SKILL.md`.
- 16 project-level agents: `.claude/agents/*.md`.
- Python virtual environment: Pillow, NumPy, SciPy, SoundFile, Faster-Whisper and headless OpenCV.
- Three.js + Playwright project dependencies; the cloud VM's preinstalled Chrome for Testing is used for rendering.
- Blender CLI, FFmpeg and required system libraries via the Cloud Environment Setup Script.
- A repository SessionStart hook that installs/updates Python and npm packages on cloud startup/resume, with a dependency hash to skip repeat installs.

Python 3 and Node.js/npm are already preinstalled by the Claude hosted cloud VM. The environment script installs missing system packages only. This is a Linux cloud build; `install.py` and the original PowerShell commands remain for Windows local use.

## One-time setup in Claude Code Web

A repository Skill cannot itself edit the saved cloud environment's setup script or network policy. Configure these once:

1. Push the entire release folder to GitHub. Keep hidden `.claude/` files in the commit.
2. Open `claude.ai/code`, connect GitHub and select this repository.
3. Use the Cloud environment selector to create/edit an environment for RicksClips.
4. Set Network access to **Limited** and keep **Allow package managers** enabled.
5. Add the hosts from `CLOUD_NETWORK_DOMAINS.txt` to Allowed domains. If a provider redirects downloads to another CDN hostname, add the exact host shown in the error and retry.
6. In the environment's **Setup script** setting, upload/select `scripts/cloud_environment_setup.sh` from this Skill folder; save.
7. Start a new cloud session. The environment script installs Blender/FFmpeg; the committed `.claude/settings.json` SessionStart hook installs Python/npm project dependencies.

The one-time environment setup is necessary because cloud environments are saved account settings outside Git. After it is configured, future cloud sessions reuse the cached system toolchain and verify project packages through the hook.

## Installation request to Claude

Invoke `/ricks-clips` and say:

> Install RicksClips in this cloud environment. Read CLOUD_MODE.md, run scripts/cloud_session_start.sh and scripts/cloud_doctor.sh, execute the offline smoke tests, repair issues you can safely fix, and report exact PASS/WARN/FAIL results. Do not create a film until installation verification is complete.

The SessionStart hook runs automatically for normal single-repository cloud sessions outside Project threads. The manual command is a safe retry. If Blender/FFmpeg is missing, upload/run the environment setup script and start a fresh cloud session. Do not report success while required tools are missing.

## Commands

Run from this Skill folder (`$CLAUDE_PROJECT_DIR/.claude/skills/ricks-clips`). Use `.venv/bin/python`:

```bash
.venv/bin/python tools/asset_hub.py search all "weathered coastal lighthouse" --kind model --limit 12
.venv/bin/python tools/asset_hub.py search polyhaven "wet stone" --kind material
.venv/bin/python tools/asset_hub.py search ambientcg "weathered stone" --kind material
node tools/check_motion_quality.mjs
node tools/test_look3d_api.mjs
node tools/test_asset_loader.mjs
node scripts/cloud_browser_smoke.mjs
.venv/bin/python tools/test_asset_hub.py
```

Install Three.js dependencies with `npm install` in `templates/threejs_film` (not `npm ci` against the old lock file; the source Asset Hub instructions require refreshing it). The hook sets `PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1` and uses the VM's system Chrome instead of downloading another browser.

## Cloud rendering limits

Anthropic-hosted cloud VMs have limited compute and no guaranteed GPU. In cloud mode the renderer is configured to use Chrome for Testing + SwiftShader/software WebGL. Use an explicit software render:

```bash
node templates/threejs_film/render_gpu.mjs episodes/<episode>/film.json --gpu-info --software
node templates/threejs_film/render_gpu.mjs episodes/<episode>/film.json --storyboard --software --scale 0.35
node templates/threejs_film/render_gpu.mjs episodes/<episode>/film.json --animatic --software --scale 0.35
```

The `--gpu-info` result must be read. SwiftShader/llvmpipe/software means a CPU preview, not GPU rendering. Start with short low-scale renders and measure a 2–5 second sample before a longer job. A complete 1080x1920/30fps film may be too slow for the standard cloud VM; when so, leave a portable episode project and render on the Windows GPU workstation or a GPU runner. Do not pretend a long render completed if the VM stopped it.

Blender runs headless with `blender -b` and can build/convert/check scenes and make small CPU previews. Large Cycles renders on CPU can be very slow. Never assume a GPU exists without a successful diagnostic.

## Secrets and provider access

Never commit `.env`, API keys, OAuth tokens, cookies or BlenderKit credentials. Prefer Cloud Environment **Network Secrets**, which inject API headers outside the session VM. Never paste credentials into chat prompts, files or Git commits.

- **Fish Audio**: add a Network Secret for host `api.fish.audio`, Secret type **Bearer**, header `Authorization`, prefix `Bearer`, value = your Fish API key. The cloud version of `tools/fish_tts.py` accepts the proxy-injected header.
- **Sketchfab**: add a Network Secret for host `api.sketchfab.com`, Secret type **Bearer**, header `Authorization`, prefix `Bearer`, value = your Sketchfab OAuth token. Automatic download remains limited to downloadable CC0/CC-BY models with attribution.
- **Poly Haven** and **ambientCG**: public APIs; no key required. Respect the attribution/User-Agent rules documented in `docs/ASSET_HUB.md`.
- **Fab**: manual acquisition and local import by the account owner only. No login automation, scraping, payments or licence bypass.
- **BlenderKit**: a Windows add-on login does not transfer into cloud. Treat the bridge as unavailable unless the user signs in/configures it on that cloud VM.

Cloud Environment variables are readable by sessions using that environment. Use a private personal environment for credentials; never put personal credentials in a shared environment.

## Voice and transcription in the cloud (measured 2026-11-17)

- faster-whisper weights are cached in `hf_cache/` (git-ignored; `HF_HOME` is set by the SessionStart hook through `CLAUDE_ENV_FILE`). `tools/voice_prep.py` reads `RICKCLIPS_WHISPER_MODEL` (default `small.en`) and `RICKCLIPS_WHISPER_LANG` (e.g. `fr` with the multilingual `small`). If the model cannot be downloaded the tool stops with the list of hosts to allow.
- Offline TTS fallback when no Fish Audio key is configured: Piper (`piper-tts` in `requirements-cloud.txt`), French voice `hf_cache/piper/fr_FR-siwis-medium.onnx` (from `huggingface.co/rhasspy/piper-voices`):
  `echo "texte" | .venv/bin/python -m piper -m hf_cache/piper/fr_FR-siwis-medium.onnx -f episodes/<film>/voice/raw.wav`
  then `HF_HOME=$PWD/hf_cache RICKCLIPS_WHISPER_MODEL=small RICKCLIPS_WHISPER_LANG=fr .venv/bin/python tools/voice_prep.py episodes/<film>/voice/raw.wav 1.0 episodes/<film>/voice`.
- Motion-library poses: `m:<id>+held` draws only what the hands hold (e.g. the lantern) without the move's 2D backdrop; `+props` keeps the old behaviour (backdrop included, meant for the motion previewer).
- Worked cloud example from voice to MP4: `episodes/le-dernier-phare/` (see its `README.md`).

## Outputs

Episodes, assets, reports and renders live under this Skill's `episodes/`, `library/` and `out/` folders in the cloned GitHub repository. Cloud sessions work on a branch; review the changes before merging. Do not commit `.venv`, `node_modules`, `.cloud-deps.sha256`, model weights or secrets. Keep the source Asset Hub licence/provenance restrictions in force.

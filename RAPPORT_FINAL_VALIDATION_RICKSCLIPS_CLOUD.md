# Final validation report — RicksClips in Claude Code Web

Date: 2026-11-17 · Branch: `ccr-00f60cb8-lenpig` · Environment: personal cloud environment `ricks-clips`
Machine: Ubuntu 24.04.5 LTS, 4 vCPU, 15 GB RAM, **no GPU** (WebGL = SwiftShader on CPU).

**Success criterion met:** RicksClips created and exported a real animated sequence (8 s, 1080×1920, 30 fps, H.264 + AAC) in Claude Code Web, from voice to MP4, without the Windows PC. Final cinematic quality gate on the video: **PASS (11 PASS / 0 WARN / 0 FAIL / 0 NOT RUN)**.

Legend: **PASS** really tested and working · **WARN** partial or limited · **FAIL** real failure · **BLOCKED** needs a permission, a secret or an outside action.

---

## 1. Test video "LE DERNIER PHARE"

| Item | Value |
|---|---|
| MP4 | `.claude/skills/ricks-clips/episodes/le-dernier-phare/final.mp4` |
| Actual duration | **8.000 s** (240 frames) |
| Resolution | **1080 × 1920** (vertical) |
| FPS | **30/1** (constant) |
| Video | H.264 High, yuv420p, CRF 20, about 6.2 Mb/s |
| Audio | AAC-LC 48 kHz stereo 192 kb/s; mix −15.0 LUFS integrated, −1.0 dBTP |
| Size | **6,447,235 bytes (6.1 MiB)** |
| Final render time | **1264 s (21 min 04 s)** for 240 frames = **5.26 s/frame** (software WebGL), + 7 s sound mix + < 1 s mux |
| Total production chain | voice 3 s, transcription 4 s, plan 1 s, render 21 min, mix 7 s, QC about 4 min |

Content: a night storm on a rocky headland; animated sea (swell, foam, spray); island with Poly Haven PBR rocks (CC0 `coast_land_rocks_01`, applied to 16 meshes); lighthouse with red bands, gallery, lantern room, lamp and two rotating beams; keeper's cottage with a lit window; painted storm sky; rain; wind; fog. The lightning (`ctx.fx.bolt`, with re-strikes) puts the lamp out on "éteint"; the lamp flickers back on "lumière". The 2D character Lina (form `teengirl`, black outlines) carries a lantern from the motion library (`m:lantern/A|B|C+held`), with readable expressions (`k:worried` → `k:scared` → `k:concentrate` → `k:surprised` → `k:proud`), `motion_polish` (breathing, auto blink) and French captions. Camera: two flowing orbits (3.3 s and 3.6 s) around Lina, 3 rests. Offline French voice (Piper) and a mix of rain, surf, wind, thunder, lantern creak, lamp ignition and an A-minor → C-major pad.

QC images (`episodes/le-dernier-phare/qc/`): `contact_sheet_1s.jpg` (one frame per second), `frame_000/040/068/080/109/150/175/239.jpg`, `blender_from_lock_f109_threejs_eevee_cycles.jpg`, plus reports `cinematic_quality/`, `frame_checks.md`, `plan_report.md`, `flicker_floor.json`, `av_sync.json`.

### Video quality control

| Check | Command | Result |
|---|---|---|
| Delivery | `tools/check_delivery.py final.mp4` | **PASS** 1080×1920, 30 fps, 8.000 s, h264, AAC |
| Cinematic gate | `tools/check_cinematic_quality.py film.json --video final.mp4 --require-audio --film-analysis --render-geometry` | **PASS** 11/0/0/0 |
| Pixel analysis (21 gates) | (included above) | **0 FAIL, 3 WARN**: travel length p90 1.92 s (target 2.1), median speed 1.73 px/f (target about 4), rest share plan 40 % vs picture 52 % |
| Geometric frame checks | `frame_checks/check.mjs` (via `--render-geometry`) | **PASS** 17 PASS, 0 WARN, 0 FAIL (head, body, face, feet, body in set) |
| Camera plan | `tools/film_plan.py check` | **PASS** 0 FAIL, 3 WARN of 41 gates |
| Flicker | `tools/frame_checks/flicker.py <frames> --region floor` | **WARN**: 10 frames flagged, all in the 3 planned light events (strike f67-80, lamp ignition f152-161, far bolt f210-216). Outside them: 0 frames (PASS on f2-65, 84-150, 163-207, 219-239) |
| A/V sync | faster-whisper re-transcription of the final MP4 vs `words.json` | **PASS** 23/23 words, median offset 0 ms, max 40 ms |
| Motion library | `tools/check_motion_quality.mjs` | **PASS** 42/42 modules, 195/195 refs, 2640 poses |

The video went through **4 real QC rounds**. They exposed defects that were then fixed rather than ignored:
- v1: moves too short, speed too low.
- v2: too many rests.
- v3: moves fragmented under the 2 px/f threshold.
- v4: PASS.

---

## 2. Installed software

| Software | Version | Status |
|---|---|---|
| Blender | 5.2.2 LTS (official, SHA-256 verified) | PASS |
| FFmpeg / ffprobe | 6.1.1-3ubuntu5 (libx264, aac) | PASS |
| Python | 3.13.18 (`.venv`) | PASS |
| Node.js / npm | 22.23.4 / 10.9.9 | PASS |
| Chrome for Testing | 153.0.8010.12 (`/usr/bin/google-chrome`) | PASS |
| Playwright (project) | 1.49.1 | PASS |
| Three.js | 0.165.0 | PASS |
| Python dependencies | Pillow 13.0.0, numpy 2.5.5, scipy 1.18.1, soundfile 0.14.0, faster-whisper 1.2.1, opencv-python-headless 5.0.0.93, ctranslate2 4.9.0, onnxruntime 1.32.0, huggingface-hub 2.4.0, **piper-tts 1.8.0** (added) | PASS |
| Models (cache `hf_cache/`, git-ignored) | faster-whisper `small` (multilingual, int8, 464 MB) · Piper `fr_FR-siwis-medium` (61 MB) | PASS |

---

## 3. Results by component

### A. Network and providers
| Component | Status | Detail / test command |
|---|---|---|
| Hosts allowed in `ricks-clips` | PASS | 20 exact hosts added after approval, including redirect CDNs (`acg-download.struffelproductions.com`, `us.aws.cdn.hf.co`) found through real errors. List: `CLOUD_NETWORK_DOMAINS.txt` |
| Poly Haven | **PASS** | `asset_hub.py search polyhaven rock --kind material` → results; `download polyhaven coast_land_rocks_01 --resolution 1k` → 57 MB ingested, used in the film |
| ambientCG | **PASS** | search `rock` → Rock064…; `download ambientcg Rock064 --resolution 1K` → zip extracted (`.blend`, PBR maps) |
| Sketchfab search | **PASS** | `search sketchfab "lighthouse rock"` → Tillamook Rock Lighthouse (CC-BY), etc. |
| Sketchfab download | **BLOCKED** | `GET /v3/models/<uid>/download` → 401: needs the Network Secret `api.sketchfab.com` (Bearer OAuth) |
| Fab | **WARN** (by design) | No API: `asset_hub.py` builds a search link; acquisition is manual (Epic account) then `asset_hub.py import-local` |
| BlenderKit search | **PASS** (after fix) | Anonymous search (`search blenderkit rock` → 3 royalty_free results) |
| BlenderKit download | **BLOCKED** | Needs `BLENDERKIT_API_KEY` or the add-on login; the tool now says so clearly |
| Fish Audio | **BLOCKED** | `POST /v1/tts` → 401: needs the Network Secret `api.fish.audio` (Bearer). Workaround in place: Piper (offline) |
| Hugging Face | **PASS** | model + voice download |
| Environment variables | PASS (absence checked) | `FISH_API_KEY`, `SKETCHFAB_OAUTH_TOKEN`, `BLENDERKIT_API_KEY`: not set (no value printed) |

### B. Transcription
| Component | Status | Detail |
|---|---|---|
| HF connectivity + cache | PASS | `HF_HOME=<skill>/hf_cache`, exported by the SessionStart hook (`CLAUDE_ENV_FILE`) |
| Model | PASS | `small` int8 (only one model downloaded) |
| Transcription | PASS | `voice_prep.py` on a Piper wav: correct French text; final film 23/23 words |
| Clear error message | PASS | Missing model → message listing the hosts to allow (tested with `HF_HUB_OFFLINE=1`) |

### C. `episodes/` and `check_views`
| Component | Status | Detail |
|---|---|---|
| `episodes/` tree | PASS | `episodes/README.md`, `baboon-signalman/` and `goldrush/` folders ready, `le-dernier-phare/` complete |
| Approved views present | PASS | 16/16 identical (`node tools/check_views.mjs`) |
| 7 missing characters | **BLOCKED** | `jack.mjs`, `goldrush.mjs`, `goldrush2.mjs`, `goldrush_today.mjs` are not in the archive. They are hand-written sheets approved by CB, not rebuildable. Copy them from the PC (exact paths in `episodes/README.md`). The check stays strict, not disabled |

### D. Blender (CPU)
| Test | Status | Measurement |
|---|---|---|
| Background mode | PASS | `blender -b --python-exit-code 1 ...` |
| Load a `.blend` | PASS | ambientCG `Rock064_1K-JPG.blend`, 0.01 s, 8 images, none missing |
| Textures / materials | PASS | 1024² PBR maps loaded and rendered |
| EEVEE (CPU) | PASS / WARN speed | 540×960: 7.1 s (simple scene), 65–103 s (film lock, CPU shader compilation) |
| Cycles CPU 32 spp + denoise | PASS | 540×960: 7.3 s (simple scene), 20–25 s (film lock) |
| GLB export / import | PASS | Blender round trip 2.9 MB with textures; three.js lock `coast.glb` (67 meshes, 14 materials) imported in 0.4 s |
| three.js → Blender transfer (`from_lock.py`) | PASS | Same camera, card and geometry on frame 109 (`qc/blender_from_lock_f109_*.jpg`) |
| Image export | PASS | PNG |
| Limit | WARN | Full 1080×1920 Blender: about 4× the 540×960 cost, so 80 s to 7 min/frame on CPU. Not viable for a full film; the Blender layer stays optional (CB_RULES §11). The kit's storm sky and rain have no Blender equivalent |

### E. Three.js and browser
| Test | Status | Detail |
|---|---|---|
| Node/npm, Three.js, Playwright, Chromium | PASS | Cloud Doctor 12 PASS / 1 WARN (GPU) / 0 FAIL |
| WebGL | PASS | WebGL 2.0, ANGLE/SwiftShader (`render_gpu.mjs --gpu-info --software`) |
| 3D scene loading | PASS | Episode set `coast.js` + kit3d (sky, PBR, relief, terrain, rocks, grass, fx.bolt) |
| Image export | PASS | `--frames` stills; 1.8–2.7 s/frame at 0.4–0.5×, 5.3 s/frame at 1× |
| Sequence → video | PASS | `--animatic --scale 1` |
| Character Motion | PASS | `m:lantern/*` moves, `motion_polish`, Motion QA |
| Environment Realism Engine | PASS | terrain/detail/atmosphere/sky/fx + Asset Hub material (`places.materials`) |
| Cinematic Quality Control | PASS | `film_plan`, `check_cinematic_quality`, `frame_checks`, `flicker` |

### F. FFmpeg and assembly
| Test | Status | Measurement |
|---|---|---|
| H.264 1080×1920 30 fps | PASS | libx264 High yuv420p |
| Audio processing | PASS / WARN | AAC 48 kHz; `loudnorm` resamples to 96 kHz unless `-ar 48000` is given (the project does not use it) |
| Joining sequences | PASS / WARN | concat demuxer OK; drift of about 20 ms per AAC join (35 ms after 2). The project mixes and muxes once |
| A/V sync | PASS | flash/beep test 9–35 ms; final film max 40 ms |

---

## 4. Errors found and fixes made

| # | Problem | Fix | Files |
|---|---|---|---|
| 1 | All providers and HF blocked by the network | 20 exact hosts allowed (`ricks-clips` environment, approved) | env + `CLOUD_NETWORK_DOMAINS.txt` |
| 2 | BlenderKit: crash without the add-on, but Blender returns 0, so an empty list instead of an error | Search without a token (or with `BLENDERKIT_API_KEY`); download clearly refused without a key; `--python-exit-code 1` | `tools/blenderkit_tool.py`, `tools/asset_hub.py` |
| 3 | faster-whisper: `small.en` hard-coded, no cache, unclear error | `RICKCLIPS_WHISPER_MODEL/LANG`, `HF_HOME` via hook, explicit error | `tools/voice_prep.py`, `scripts/cloud_session_start.sh` |
| 4 | No voice without a Fish Audio key | Piper TTS (offline) added | `requirements-cloud.txt`, `CLOUD_MODE.md` |
| 5 | `+props` drew the move's 2D backdrop (rectangle) in the 3D set | New `+held` option (held objects only) | `templates/threejs_film/puppets.mjs` |
| 6 | Lantern: hard 170 px halo clipped by the card | Soft 105 px halo | `templates/motion_styles/moves/act_tools2.mjs` |
| 7 | Asset Hub material results/errors never printed | `assets_applied` / `ASSET ERROR` in `render.mjs` and `render_gpu.mjs` | `film.js`, `render*.mjs` |
| 8 | Texture error = `[object Event]` | Message names the file | `asset_loader.mjs` |
| 9 | `--export-lock` exported `noExport` objects nested in a group (light beams) | Nested objects filtered out | `film.js` (`exportSet`) |
| 10 | Mix: true peak handled as linear in my script | Corrected (dBTP) + soft knee | `episodes/le-dernier-phare/sound/mix.py` |
| 11 | Camera: 3 video QC rounds failed (moves, rests) | Plan rewritten, orbit moves | `episodes/le-dernier-phare/film.json` |

Known harmless messages: 404 `act_tools2_front.mjs` (optional probe in `film.js`, caught by design); EGL warnings in Blender background mode; Chrome's own requests to `www.google.com` (refused, no effect).

Non-regression after the fixes: Cloud Doctor 12/1/0, Asset Hub 16/16, Motion QA PASS, Look3D PASS, Asset Loader PASS, Motion polish PASS, browser smoke PASS, check_views 16 OK / 7 missing (unchanged), frame_checks 3/3 CAUGHT.

---

## 5. Hardware limits

- No GPU: three.js renders on CPU through SwiftShader: **5.3 s/frame at 1080×1920**, so about 21 min for 8 s and about 2 h 40 for a 60 s film (estimate from the measured rate).
- EEVEE on CPU: shader compilation dominates (65–103 s for one 540×960 frame of the set). Cycles CPU is faster here (20–25 s).
- 4 vCPU: one render at a time. Several renders in parallel slow each other down.
- A full-resolution Blender layer over a whole film is not realistic in the cloud: use the Windows GPU workstation or a GPU runner.

## 6. Configuration still needed

1. **Network Secret Fish Audio**: host `api.fish.audio`, `Authorization: Bearer <key>` (environment settings, Network Secrets).
2. **Network Secret Sketchfab**: host `api.sketchfab.com`, `Authorization: Bearer <OAuth token>`. On the first download, add the CDN host shown in the error if needed.
3. **BlenderKit**: a `BLENDERKIT_API_KEY` key (private environment) for downloads.
4. **Fab**: manual acquisition by the account owner, then `asset_hub.py import-local`.
5. **Episode sheets**: copy the 4 files listed in `episodes/README.md` from the PC.
6. **Optional**: wildcard domains (`*.polyhaven.com`, etc.) can only be added in the settings (exact hosts are already in place).

---

## 7. Addendum — LE DERNIER PHARE, 50 s, rendered on RunPod (2026-11-17)

| Item | Value |
|---|---|
| MP4 | `.claude/skills/ricks-clips/episodes/le-dernier-phare-50s/final.mp4` · GoFile: https://gofile.io/d/rI6a7eet |
| Format | 50.000 s, 1080×1920, 30 fps (1500 frames), H.264 CRF 18 + AAC 192 kb/s, 44,982,746 bytes |
| SHA-256 | `1c779940c37d163db210ea6fd3d5ed9f683882e191f0efb114daf2e05aa960a1` (pod = local copy) |
| Machine | RunPod RTX 4090 pod (48 vCPU), $0.89/h; **render on CPU** (SwiftShader, 6 processes), 3092 s = 2.06 s/frame |
| RunPod cost | **$0.94** total (balance $8.33 → $7.39): failed pod 1, render pod 2, GPU diagnostic pod. All pods deleted (`pods: []`) |
| GoFile | Upload PASS (size reported by GoFile = local size, page HTTP 200). **Download not verified by SHA-256**: GoFile now refuses the contents API to guest accounts (401) and its site scripts moved (404). From this session GoFile is blocked (TLS tunnel reset) |
| Delivery QC | `check_delivery.py` PASS |
| Cinematic QC (video) | **FAIL**: 9 PASS / 2 FAIL. Pixel analysis: travel p90 1.56 s, roll p99 2.45°/f, voice pace 2.29 words/s (narration deliberately slow, below Rick's 3.5–4.5). frame_checks: Lina cut by the edge on f518-615 ("foudre") and f655-682; 3 WARN: Lina's body crosses the gallery rail by 1–2 % |

### RTX 4090 GPU: cause found and fixed
- Pod 1: Chrome saw only SwiftShader, and 24 software processes saturated the CPU (Playwright 30 s timeout, 0 frames). Deleted.
- `scripts/runpod/gpu_diag.sh` on a 4090: the NVIDIA EGL/Vulkan libraries **are** mounted. Headless ANGLE **Vulkan fails without `--disable-vulkan-surface`** (no WebGL2), and the second attempt used `gl` (needs X) instead of **`gl-egl`**. With either fix, Chrome reports `ANGLE (NVIDIA, Vulkan 1.4.329 (NVIDIA GeForce RTX 4090))` / `NVIDIA GeForce RTX 4090/PCIe/SSE2, OpenGL ES 3.2`.
- Fixed in `render_gpu.mjs` (Linux: `--disable-vulkan-surface`, `RICKCLIPS_GPU_ANGLE`, `RICKCLIPS_GPU_EXTRA_ARGS`) and `scripts/runpod/render_pod.sh` (tries vulkan then gl-egl, writes missing loader files, publishes `gpu_diag.txt`). The 50 s film was already 2/3 rendered on CPU, so it was not restarted. Next renders use the GPU.

### Keys (Network Secrets, entered through the secure form, checked with authenticated requests)
Fish Audio (`api.fish.audio`, Bearer) 200 · Sketchfab (`api.sketchfab.com`, `Token`) 200 · BlenderKit (`www.blenderkit.com`, Bearer) 200 · RunPod (`api.runpod.io` GraphQL, Bearer) 200. `rest.runpod.io` answers 502 upstream (not used).

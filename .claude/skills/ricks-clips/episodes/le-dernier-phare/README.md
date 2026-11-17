# LE DERNIER PHARE: cloud validation film (2026-11-17)

An 8-second test film (1080x1920, 30 fps, H.264 + AAC), made entirely in Claude Code Web with the RicksClips kit, without the Windows PC.
Story: the last lighthouse goes out under the lightning; Lina raises her lantern, and the light comes back.

| File | Role |
|---|---|
| `voice/raw.wav` | Voice (offline Piper TTS, French voice fr_FR-siwis-medium) |
| `voice/voice.wav`, `voice/words.json`, `voice/voice_gates.json` | `tools/voice_prep.py` (faster-whisper `small`, fr): trim, word timings, gates |
| `film.json` | Cast (form:teengirl), place `coast` (Poly Haven PBR material on `cliff_rock`), 4 camera stations, acts on the words, fx, moods, sound |
| `sets/coast.js` | Set: animated sea, foam and spray, rocks and island, lighthouse (lamp, rotating beams), cottage, night-storm sky, lightning (`ctx.fx.bolt`), rain, wind, fog |
| `assets/coast_land_rocks_01/` | Poly Haven CC0 textures (diff, normal GL, rough 1k) + provider manifest |
| `sound/mix.py` → `sound/mix.wav`, `sound/mix_report.json` | Mix: voice + rain/surf/wind beds + thunder, lantern, lamp ignition + Am→C pad (kit `templates/audio`) |
| `final.mp4` | Delivered film |
| `qc/` | Quality-control images and reports |

## Reproduce (from the skill folder)

```bash
E=episodes/le-dernier-phare; export HF_HOME=$PWD/hf_cache
echo "Cette nuit-là, le dernier phare de la côte s'est éteint. Alors Lina a levé sa lanterne, et la lumière est revenue." \
  | .venv/bin/python -m piper -m hf_cache/piper/fr_FR-siwis-medium.onnx --length-scale 0.95 --sentence-silence 0.25 -f $E/voice/raw.wav
RICKCLIPS_WHISPER_MODEL=small RICKCLIPS_WHISPER_LANG=fr .venv/bin/python tools/voice_prep.py $E/voice/raw.wav 1.0 $E/voice
.venv/bin/python tools/film_plan.py check $E/film.json                       # 0 FAIL, 3 WARN of 41 gates
.venv/bin/python tools/check_cinematic_quality.py $E/film.json              # pre-render gate
(cd templates/threejs_film && node render_gpu.mjs ../../$E/film.json --animatic --scale 1 --seed 7)   # software WebGL in the cloud
.venv/bin/python $E/sound/mix.py
ffmpeg -y -i $E/out/animatic.mp4 -i $E/sound/mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -ar 48000 -shortest -movflags +faststart $E/final.mp4
.venv/bin/python tools/check_delivery.py $E/final.mp4
.venv/bin/python tools/check_cinematic_quality.py $E/film.json --video $E/final.mp4 --require-audio --film-analysis
```

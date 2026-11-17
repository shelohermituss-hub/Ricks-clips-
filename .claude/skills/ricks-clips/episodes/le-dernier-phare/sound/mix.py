"""LE DERNIER PHARE: sound mix (cloud validation film, 2026-11-17).
Built ONLY from the kit's own synthesis code (templates/audio: dsp.py, sfx_gen.py, instruments.py), timed from out/plan/sound_events.json.
  .venv/bin/python episodes/le-dernier-phare/sound/mix.py
Writes sound/mix.wav (48 kHz, stereo, 24-bit, the film's exact length) and sound/mix_report.json (loudness, true peak, cue list).
Voice = voice/voice.wav (Piper TTS, fr_FR-siwis-medium, offline). Beds: rain, surf, wind. Events: thunder, lantern creak, lamp ignition.
Music: a slow minor pad that turns major when the light comes back, ducked under the voice."""
import json, os, sys
import numpy as np
EP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(EP, "..", "..", "templates", "audio"))
from dsp import (SR, ns, rng, lp, hp, bp, colored, smooth_noise, place, st, widen, make_ir, convolve_st, integrated, momentary_max,
                 true_peak, norm_to, read_wav, write_wav, dbg, pan)
from sfx_gen import water_bed, breeze, creak, whoosh
from instruments import pad, glock, timpani, m2f

film = json.load(open(os.path.join(EP, "film.json"), encoding="utf-8"))
DUR = film["end"] / film["fps"]
N = ns(DUR)
ev = {e["name"]: e["t"] for e in json.load(open(os.path.join(EP, "out", "plan", "sound_events.json")))}
R = rng(2026)
cues = []

# ---------------- voice ----------------
v, sr = read_wav(os.path.join(EP, "voice", "voice.wav")); assert sr == SR, sr
v = v[0] if v.shape[0] == 1 else v.mean(0)
voice = np.zeros((2, N)); place(voice, hp(v, 80), 0.0)
voice = voice + 0.12 * convolve_st(voice, make_ir(0.9, 3))[:, :N]                       # a little night air on the voice
voice = norm_to(voice, -16.0, "integrated")

# ---------------- beds ----------------
rain = np.zeros((2, N))
for ch in range(2):
    hiss = bp(colored(N, R, 0.25), 1800, 9000, 1) * (0.75 + 0.25 * smooth_noise(N, R, 0.7))
    drops = np.zeros(N); idx = R.integers(0, N, int(DUR * 260)); drops[idx] = R.uniform(.2, 1, len(idx)) * R.choice([-1, 1], len(idx))
    rain[ch] = hiss + 0.6 * bp(drops, 2500, 7000, 2)
rain = norm_to(rain, -31.0, "integrated"); cues.append({"t": 0.0, "name": "rain_bed", "lufs": -31})
surf = water_bed(DUR, R, close=1.0, slosh_rate=0.35)[:, :N]
swell = 0.55 + 0.45 * np.sin(2 * np.pi * np.arange(N) / SR / 4.2 - 1.0) ** 2                  # breakers every ~4 s (the set's swell)
surf = norm_to(lp(surf * swell, 2400) + 0.5 * lp(colored(N, R, 1.6), 180)[None, :] * swell, -30.0, "integrated"); cues.append({"t": 0.0, "name": "surf_bed", "lufs": -30})
wind = norm_to(breeze(DUR, R, level=1.0, gust=0.45, bright=700)[:, :N], -33.0, "integrated"); cues.append({"t": 0.0, "name": "storm_wind", "lufs": -33})

# ---------------- events ----------------
sfx = np.zeros((2, N))
t0 = ev.get("thunder_close", 2.27)
crack_n = ns(0.35); crack = bp(colored(crack_n, R, 0.0), 900, 7000, 2) * np.exp(-np.arange(crack_n) / SR * 14)
rumble_n = ns(3.6); rumble = lp(colored(rumble_n, R, 2.0), 140, 2) * (np.minimum(1, np.arange(rumble_n) / ns(0.12)) * np.exp(-np.arange(rumble_n) / SR * 1.1)) * (0.7 + 0.3 * smooth_noise(rumble_n, R, 3))
thunder = np.zeros((2, ns(4.5))); place(thunder, widen(crack, R, 9, .8), 0.0); place(thunder, widen(rumble, R, 17, .9), 0.04, 2.2)
thunder = thunder + 0.6 * convolve_st(thunder, make_ir(2.4, 7))[:, :thunder.shape[1]]
place(sfx, norm_to(thunder, -17.0), t0 - 0.03); cues.append({"t": round(t0 - 0.03, 3), "name": "thunder_close (crack + rumble)", "lufs_max_m": -17})
t1 = ev.get("lantern_creak", 3.73)
place(sfx, norm_to(pan(creak(0.45, R, rate0=140, rate1=210), 0.25), -27.0), t1); cues.append({"t": t1, "name": "lantern_creak", "lufs_max_m": -27})
t2 = ev.get("lamp_ignite_hum", 5.07)
ign = np.zeros((2, ns(3.0))); place(ign, whoosh(0.6, R, peak=0.35, f_lo=300, f_hi=2600), 0.0, 0.7)
hn = ns(2.9); th = np.arange(hn) / SR; hum = sum(np.sin(2 * np.pi * f * th) / k for k, f in enumerate([110, 220, 330, 440], 1)) * np.minimum(1, th / 0.35) * np.exp(-th * 0.5)
place(ign, pan(hum * 0.4, -0.2), 0.15)
ign = ign + 0.35 * convolve_st(ign, make_ir(1.6, 11))[:, :ign.shape[1]]
place(sfx, norm_to(ign, -24.0), t2 - 0.1); cues.append({"t": round(t2 - 0.1, 3), "name": "lamp_ignite (whoosh + mains hum)", "lufs_max_m": -24})

# ---------------- music: A minor pad, then a lift to C major and a small glock motif on the light ----------------
mus = np.zeros((2, N + ns(2)))
place(mus, pad([m2f(m) for m in (45, 57, 60, 64)], t2 - 0.3, vel=0.45, r=R, att=1.6, rel=0.8, warm=700), 0.0)
place(mus, pad([m2f(m) for m in (48, 55, 60, 64, 67)], DUR - t2 + 0.2, vel=0.55, r=R, att=0.5, rel=1.0, warm=1200), t2 - 0.25)
place(mus, timpani(m2f(33), vel=0.6, r=R), t0)
for i, m in enumerate((72, 76, 79, 84)):
    place(mus, pan(glock(m2f(m), vel=0.45, r=R), -0.3 + 0.2 * i), t2 + 0.25 + 0.32 * i)
mus = mus[:, :N]
mus = norm_to(mus, -26.0, "integrated")
env = np.abs(voice).mean(0); env = lp(env, 6); duck = 1.0 - 0.5 * np.clip(env / (env.max() + 1e-9) * 3, 0, 1)    # -6 dB under speech
mus = mus * duck; cues.append({"t": 0.0, "name": "music_pad_Am_to_C (ducked under voice)", "lufs": -26})

# ---------------- master ----------------
for _n, _x in (("voice", voice), ("rain", rain), ("surf", surf), ("wind", wind), ("sfx", sfx), ("music", mus)):
    if not np.isfinite(_x).all(): print("NaN in", _n, int((~np.isfinite(_x)).sum()))
mix = voice + rain + surf + wind + sfx + mus
fade = np.ones(N); fade[:ns(0.25)] = np.linspace(0, 1, ns(0.25)); fade[-ns(0.5):] = np.linspace(1, 0, ns(0.5)); mix = mix * fade
mix = norm_to(mix, -14.0, "integrated")
K = dbg(-3.0); ax = np.abs(mix)                                                    # soft knee above -3 dBFS: tames the thunder crack instead of turning the whole mix down
mix = np.where(ax < K, mix, np.sign(mix) * (K + (1 - K) * np.tanh((ax - K) / (1 - K))))
tp = true_peak(mix)                                                                # dBTP (4x oversampled)
if tp > -1.0:                                                                      # safety gain to -1 dBTP
    mix = mix * dbg(-1.0 - tp)
write_wav(os.path.join(EP, "sound", "mix.wav"), mix)
rep = {"duration_s": round(mix.shape[1] / SR, 3), "sample_rate": SR, "channels": 2, "integrated_lufs": round(float(integrated(mix)), 2),
       "true_peak_dbtp": round(float(true_peak(mix)), 2), "voice_lufs": round(float(integrated(voice)), 2), "cues": cues}
json.dump(rep, open(os.path.join(EP, "sound", "mix_report.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in rep.items() if k != "cues"}))

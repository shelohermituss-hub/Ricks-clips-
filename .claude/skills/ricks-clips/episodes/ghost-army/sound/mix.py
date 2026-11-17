"""THE GHOST ARMY: sound mix, built only from the kit's synthesis code (templates/audio), timed from film.json
(place spans from out/plan/camera_baked.json, set events from places.<name>.events, cues from out/plan/sound_events.json).
  .venv/bin/python episodes/ghost-army/sound/mix.py
Writes sound/mix.wav (48 kHz stereo 24-bit, the film's exact length) and sound/mix_report.json.
Voice: voice/voice.wav (Fish Audio "rick", speed 1.2). Beds per place, crossfaded on the cuts. Events on their frames.
Music: a playful 1940s swing (walking bass, brushes, a fife-and-brass riff), tension on the river, relief on the crossing,
then a quiet music box for the last line (story bible)."""
import json, os, sys
import numpy as np
EP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(EP, "..", "..", "templates", "audio"))
from dsp import (SR, ns, rng, lp, hp, bp, colored, smooth_noise, place, widen, make_ir, convolve_st, integrated,
                 true_peak, norm_to, read_wav, write_wav, dbg, pan)
from sfx_gen import (breeze, bird_chirps, crickets, babble, push_thump, whoosh, bubbles, rattle, creak, clink, boot, water_bed, stroll_step)
from instruments import pad, glock, timpani, m2f, pluck, brush, fife, brass, musicbox, vibes, snare

film = json.load(open(os.path.join(EP, "film.json"), encoding="utf-8"))
FPS = film["fps"]; DUR = film["end"] / FPS; N = ns(DUR)
cam = json.load(open(os.path.join(EP, "out", "plan", "camera_baked.json")))
cam = cam.get("frames", cam) if isinstance(cam, dict) else cam
spans = []
for c in cam:
    if not spans or spans[-1][0] != c["place"]: spans.append([c["place"], c["f"] / FPS, (c["f"] + 1) / FPS])
    else: spans[-1][2] = (c["f"] + 1) / FPS
EV = {k: v.get("events", {}) for k, v in film["places"].items()}
cue = {e["name"]: e["t"] for e in json.load(open(os.path.join(EP, "out", "plan", "sound_events.json")))}
words = json.load(open(os.path.join(EP, "voice", "words.json")))
def word_t(w, n=1):
    k = 0
    for x in words:
        if x["w"].lower().strip('.,!?:;"…') == w:
            k += 1
            if k == n: return x["s"]
    raise KeyError(w)
R = rng(1944); cues = []

def env_span(a, b, xf=0.25):
    """1 inside [a, b], short crossfades at the cuts"""
    t = np.arange(N) / SR
    return np.clip((t - a + xf) / (2 * xf), 0, 1) * np.clip((b + xf - t) / (2 * xf), 0, 1)

# ---------------- voice ----------------
v, sr = read_wav(os.path.join(EP, "voice", "voice.wav")); assert sr == SR, sr
v = v[0] if v.shape[0] == 1 else v.mean(0)
voice = np.zeros((2, N)); place(voice, hp(v, 80), 0.0)
voice = norm_to(voice, -16.0, "integrated")

# ---------------- beds, one per place ----------------
def bed(kind, d):
    if kind == "field":   # dawn: birds, a light breeze, a cow far away
        x = breeze(d, R, level=.7, gust=.2, bright=800)[:, :ns(d)] + 0.8 * np.vstack([bird_chirps(d, R, .7, "sparrow"), bird_chirps(d, R, .5, "blackbird")])[:, :ns(d)]
        return norm_to(x, -30.0, "integrated")
    if kind == "camp":    # open meadow, compressors hissing, rubber squeaks
        hiss = bp(colored(ns(d), R, .2), 1500, 7000, 1) * (.6 + .4 * smooth_noise(ns(d), R, .5))
        thr = lp(colored(ns(d), R, 1.5), 120) * (.8 + .2 * np.sin(2 * np.pi * 24 * np.arange(ns(d)) / SR))
        x = breeze(d, R, level=.6, gust=.2)[:, :ns(d)] + .5 * pan(hiss * .4, -.4) + .5 * pan(thr, .3) + .5 * np.vstack([bird_chirps(d, R, .3, "sparrow")] * 2)[:, :ns(d)]
        return norm_to(x, -30.0, "integrated")
    if kind == "road":    # moonlit night: crickets, poplars in the wind
        x = np.vstack([crickets(d, R, 4), crickets(d, R, 3)])[:, :ns(d)] * .6 + breeze(d, R, level=.6, gust=.3, bright=600)[:, :ns(d)]
        return norm_to(x, -31.0, "integrated")
    if kind in ("radio", "photo"):   # interior room tone, lamp hum
        n = ns(d); t = np.arange(n) / SR
        x = lp(colored(n, R, 1.0), 900) + .15 * np.sin(2 * np.pi * 60 * t) + .08 * np.sin(2 * np.pi * 120 * t)
        return norm_to(np.vstack([x, np.roll(x, 300)]), -36.0, "integrated")
    if kind == "cafe":    # chatter, cups
        x = sum(pan(babble(d, R, R.uniform(95, 220), R.uniform(.9, 1.15)), R.uniform(-.8, .8)) for _ in range(6))[:, :ns(d)]
        for i in range(int(d * 1.5)): place(x, pan(clink(R, bright=.8) * .3, R.uniform(-.7, .7)), R.uniform(0, d - .2))
        x = x + .3 * convolve_st(x, make_ir(.8, 5))[:, :x.shape[1]]
        return norm_to(x, -29.0, "integrated")
    if kind == "river":   # night wind over the water, far artillery rumble to the south
        n = ns(d); x = breeze(d, R, level=.8, gust=.35, bright=500)[:, :n] + .7 * water_bed(d, R, close=.4, slosh_rate=.25)[:, :n]
        return norm_to(x, -30.0, "integrated")
    if kind == "bedroom": # night, a curtain breathing, crickets outside
        x = .5 * np.vstack([crickets(d, R, 2)] * 2)[:, :ns(d)] + breeze(d, R, level=.5, gust=.25, bright=500)[:, :ns(d)]
        return norm_to(x, -34.0, "integrated")
    if kind == "attic":   # warm afternoon, old wood
        n = ns(d); x = np.vstack([lp(colored(n, R, 1.2), 700)] * 2)
        for tc in (R.uniform(.5, 1.5), R.uniform(2.5, 3.5)): place(x, pan(creak(.6, R, rate0=70, rate1=110) * .5, -.3), tc)
        return norm_to(x, -34.0, "integrated")
    raise ValueError(kind)

beds = np.zeros((2, N))
for p, a, b in spans:
    a0 = max(0.0, a - .3); d = b - a0 + .6
    x = bed(p, d); y = np.zeros((2, N)); place(y, x, a0)
    beds += y * env_span(a, b); cues.append({"t": round(a, 2), "name": "bed_" + p, "until": round(b, 2)})

# ---------------- events ----------------
sfx = np.zeros((2, N))
def put(x, t, lufs, name, p=0.0):
    place(sfx, norm_to(pan(x, p) if x.ndim == 1 else x, lufs), t); cues.append({"t": round(t, 3), "name": name, "lufs_max_m": lufs})

# hook: the tank is set down (a rubbery bounce), the pat makes a hollow "boing", the bikes skid
put(lp(push_thump(R), 500) + .4 * lp(push_thump(R), 300), EV["field"]["set"] / FPS, -22.0, "tank_set_down_rubber_thump")
n = ns(.45); t = np.arange(n) / SR; boing = np.sin(2 * np.pi * (180 + 60 * np.exp(-t * 9)) * t) * np.exp(-t * 7) * (1 + .3 * np.sin(2 * np.pi * 11 * t))
put(boing, EV["field"]["dent"] / FPS, -24.0, "pat_dent_boing", .2)
n = ns(1.0); t = np.arange(n) / SR
skid = bp(colored(n, R, .2), 600, 3200, 2) * np.minimum(1, t / .05) * np.exp(-t * 2.6) + .5 * np.sin(2 * np.pi * (2400 - 600 * t) * t) * np.exp(-t * 4)
put(skid, cue["bike_brakes_skid"] - .3, -25.0, "bike_brakes_skid x2", -.4); put(skid * .8, cue["bike_brakes_skid"] - .15, -27.0, "bike_brakes_skid_2", -.6)
# "very strong": a tiny wink glint
put(glock(m2f(96), vel=.4, r=R, dur=.6), word_t("winks") + .1, -30.0, "wink_glint", .3)
# "made of rubber": the valve, air whistling out, the barrel sagging
n = ns(2.2); t = np.arange(n) / SR; f = 1400 - 700 * t / 2.2
air = .6 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * .8) + bp(colored(n, R, .1), 1200, 6000, 1) * np.exp(-t * 1.1)
put(air, EV["field"]["deflate"] / FPS, -23.0, "valve_air_whistle + sag", -.2)
# camp: the bulldozer's engine and the toothed beam scraping track marks
n = ns(3.2); t = np.arange(n) / SR
dozer = sum(np.sin(2 * np.pi * k * 38 * t) / k for k in range(1, 8)) * (.8 + .2 * np.sin(2 * np.pi * 9 * t)) * np.minimum(1, t / .4) * np.minimum(1, (3.2 - t) / .6)
dozer = lp(dozer, 900) + .3 * rattle(3.2, R, density=20, heavy=True)[:n]
put(dozer, cue["dozer_engine"] - .4, -24.0, "dozer_engine + track rattle", .3)
# road: one truck... then a hundred tanks out of the speaker (engines, tracks, shouts, disc crackle, band-limited like a horn speaker)
put(lp(dozer, 500) * .7, word_t("truck") - .3, -28.0, "halftrack_idle", -.3)
th = cue["tank_column_playback"]; n = ns(5.6); t = np.arange(n) / SR
eng = sum(lp(np.sin(2 * np.pi * np.cumsum(np.full(n, f0) * (1 + .02 * smooth_noise(n, R, .8))) / SR), 400) for f0 in (31, 37, 44, 52))
col = eng + .6 * rattle(5.6, R, density=60, heavy=True)[:n] + .25 * babble(5.6, R, 120, 1.0, rate=3.0)[:n] + .15 * bp(colored(n, R, 0), 2000, 7000, 1) * (R.random(n) < .002)
col = bp(col, 180, 4200, 2) * np.minimum(1, t / .8) * np.minimum(1, (5.6 - t) / 1.2)
col2 = widen(col, R, 23, .9); col2 = col2 + .5 * convolve_st(col2, make_ir(2.8, 17))[:, :col2.shape[1]]
put(col2, th - .4, -19.0, "speaker: a hundred tanks (engines, tracks, shouts, crackle)")
# radio: Morse beeps, copying the "fist"
n = ns(3.4); morse = np.zeros(n); tt_ = 0.0
for sym in "-.-. --- .--. -.--   ..-. .. ... -":
    if sym == " ": tt_ += .12; continue
    d = .06 if sym == "." else .18; i0 = ns(tt_); i1 = min(n, ns(tt_ + d)); tq = np.arange(i1 - i0) / SR
    morse[i0:i1] += np.sin(2 * np.pi * 720 * tq) * np.minimum(1, tq / .004) * np.minimum(1, (d - tq) / .004); tt_ += d + .06
    if tt_ > 3.3: break
put(morse, cue["morse_beeps"] - .3, -27.0, "morse_beeps", .2)
# café: the accordion on a chair (a tremolo pad, French waltz chords)
acc = np.zeros((2, ns(8.5)))
for i, ch in enumerate([(57, 60, 64), (55, 59, 62), (53, 57, 60), (52, 56, 59)] * 2):
    place(acc, pad([m2f(m) for m in ch], 1.0, vel=.45, r=R, att=.05, rel=.15, warm=2200, detune=12, trem=lambda t: 1 + .25 * np.sin(2 * np.pi * 6.5 * t)), i * 1.05)
put(acc, cue["cafe_room_accordion"], -31.0, "cafe_accordion")
# sergeant laughs: "ha ha ha" (short voiced bursts) + cigar ash hiss on the rubber
lt = cue["sergeant_laugh"]; n = ns(1.3); t = np.arange(n) / SR; laugh = np.zeros(n)
for k in range(5):
    i0 = ns(k * .21); m = ns(.14); tq = np.arange(m) / SR
    laugh[i0:i0 + m] += sum(np.sin(2 * np.pi * h * (125 - 12 * k) * tq) / h for h in range(1, 12)) * np.sin(np.pi * tq / .14) ** 2
laugh = bp(laugh, 200, 3000, 1) + .2 * bp(colored(n, R, 0), 800, 3000, 1) * (laugh != 0)
put(laugh, lt, -22.0, "sergeant_laugh", .25)
# river: the inflation wave (a run of hisses across the field)
for i in range(10): put(whoosh(.5, R, peak=.2, f_lo=800, f_hi=5000), EV["river"]["inflate"] / FPS + i * .28, -30.0 - i * .3, "inflate_hiss", -.6 + .12 * i)
# the barrage: a whistle falling into each burst on the frame it flashes (set: 10 bursts, every 8 frames from EV.shell)
for i in range(10):
    tb = (EV["river"]["shell"] + i * 8) / FPS; n = ns(.9); t = np.arange(n) / SR; fw = 1800 - 1100 * t / .9
    whis = .5 * np.sin(2 * np.pi * np.cumsum(fw) / SR) * np.minimum(1, t / .1)
    if tb - .9 > 0: put(whis, tb - .9, -31.0, "shell_whistle", -.5 + .1 * i)
    bn = ns(2.4); tq = np.arange(bn) / SR
    boom = lp(colored(bn, R, 2.0), 160, 2) * np.minimum(1, tq / .01) * np.exp(-tq * 2.2) + .4 * bp(colored(bn, R, .3), 700, 4000, 1) * np.exp(-tq * 18)
    boom = widen(boom, R, 13, .8); boom = boom + .5 * convolve_st(boom, make_ir(2.0, 9 + i))[:, :boom.shape[1]]
    put(boom, tb, -18.0 - (i % 3), "shell_impact")
# the crossing: silence but for paddles and the bridge creaking under the real tanks
tc = cue["river_silence_paddles"]
for i in range(6): put(bubbles(.5, R, 18, f_lo=200, f_hi=1200), tc - 1.2 + i * .55, -31.0, "paddle_splash", .3)
put(creak(2.0, R, rate0=40, rate1=70), tc - .6, -30.0, "pontoon_creak", .4)
# attic: the trunk lid, then the skin unfolding (soft rubber rustle)
put(creak(.8, R, rate0=90, rate1=150), word_t("fooled") - .6, -27.0, "trunk_lid_creak", -.2)
put(whoosh(1.0, R, peak=.4, f_lo=300, f_hi=1800), EV["attic"]["lift_skin"] / FPS + .4, -29.0, "rubber_skin_unfold", .1)

# ---------------- music ----------------
mus = np.zeros((2, N + ns(4)))
BPM = 132.0; beat = 60.0 / BPM; sw = beat * 2 / 3                       # swung eighths
river_t = next(a for p, a, b in spans if p == "river"); bed_t = next(a for p, a, b in spans if p == "bedroom")
cross_t = cue["river_silence_paddles"] - 2.5; attic_t = next(a for p, a, b in spans if p == "attic")
# swing: walking bass + brushes until the river, a short break on the road (the speaker is the music there)
road = next((a, b) for p, a, b in spans if p == "road")
prog = [(43, 47, 50, 52), (48, 52, 55, 57), (43, 47, 50, 52), (50, 54, 57, 59)]   # G, C, G, D (one bar each)
t = 0.4; bar = 0
while t < river_t - 1.0:
    quiet = road[0] - .2 < t < road[1] - .3
    ch = prog[bar % 4]
    for k in range(4):
        tb = t + k * beat
        if not quiet:
            place(mus, pan(pluck(m2f(ch[k] - 12), vel=.7, r=R, dur=.5, bright=.35), -.2), tb)
            place(mus, pan(brush(vel=.35 if k % 2 == 0 else .55, r=R, dur=.3, swish=(k % 2 == 0)), .35), tb)
            place(mus, pan(brush(vel=.25, r=R, dur=.15), .35), tb + sw)
    t += 4 * beat; bar += 1
# the riff: fife (clarinet-like) and a muted brass answer, on the chapter starts
riff = [(0, .5, 74), (.67, .33, 76), (1, .5, 79), (1.67, .33, 76), (2, 1.0, 74)]
for p, a, b in spans:
    if p in ("field", "camp", "radio", "cafe"):
        t0 = a + .25
        for (o, d, m) in riff: place(mus, pan(fife(m2f(m), d * beat, vel=.55, r=R), .25), t0 + o * beat)
        place(mus, pan(brass(m2f(55), 1.2 * beat, vel=.45, r=R, kind="horn"), -.3), t0 + 3 * beat)
# the river: low pad and a heartbeat on the timpani while the decoys inflate and the shells fall
place(mus, pad([m2f(m) for m in (38, 45, 50, 53)], cross_t - river_t, vel=.45, r=R, att=1.2, rel=.8, warm=700), river_t)
k = 0
while river_t + k * .75 < cross_t: place(mus, timpani(m2f(26), vel=.25 + .3 * min(1, k / 12), r=R, dur=.9), river_t + k * .75); k += 1
# relief: D major opens as the real army crosses, then soft vibes in the bedroom
place(mus, pad([m2f(m) for m in (38, 50, 54, 57, 62)], bed_t - cross_t + .5, vel=.5, r=R, att=.8, rel=1.2, warm=1300), cross_t)
for i, m in enumerate((66, 69, 74, 69, 71, 67)): place(mus, pan(vibes(m2f(m), vel=.45, r=R, dur=1.6), -.2 + .08 * i), bed_t + .3 + i * .7)
# the last line: a quiet music box (the same riff, slowed), the loop closes
for i, (o, d, m) in enumerate(riff + [(3.0, 1.0, 79), (4.0, 1.5, 74)]):
    place(mus, pan(musicbox(m2f(m + 12), vel=.5, r=R, dur=2.0), .1), attic_t + .4 + o * .55)
place(mus, pad([m2f(m) for m in (43, 55, 59, 62)], DUR - attic_t + 1, vel=.3, r=R, att=1.5, rel=1.5, warm=800), attic_t)
mus = mus[:, :N]; mus = norm_to(mus, -25.0, "integrated")
envv = lp(np.abs(voice).mean(0), 6); duck = 1.0 - 0.5 * np.clip(envv / (envv.max() + 1e-9) * 3, 0, 1)
mus = mus * duck; cues.append({"t": 0.0, "name": "music: swing (G) -> river tension -> D major relief -> music box", "lufs": -25})

# ---------------- master ----------------
for nm, x in (("voice", voice), ("beds", beds), ("sfx", sfx), ("music", mus)):
    assert np.isfinite(x).all(), nm
mix = voice + beds + sfx + mus
fade = np.ones(N); fade[:ns(.2)] = np.linspace(0, 1, ns(.2)); fade[-ns(.6):] = np.linspace(1, 0, ns(.6)); mix = mix * fade
mix = norm_to(mix, -14.0, "integrated")
K = dbg(-3.0); ax = np.abs(mix); mix = np.where(ax < K, mix, np.sign(mix) * (K + (1 - K) * np.tanh((ax - K) / (1 - K))))
tp = true_peak(mix)
if tp > -1.0: mix = mix * dbg(-1.0 - tp)
write_wav(os.path.join(EP, "sound", "mix.wav"), mix)
rep = {"duration_s": round(mix.shape[1] / SR, 3), "sample_rate": SR, "channels": 2, "integrated_lufs": round(float(integrated(mix)), 2),
       "true_peak_dbtp": round(float(true_peak(mix)), 2), "voice_lufs": round(float(integrated(voice)), 2), "cues": cues}
json.dump(rep, open(os.path.join(EP, "sound", "mix_report.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in rep.items() if k != "cues"}), len(cues), "cues")

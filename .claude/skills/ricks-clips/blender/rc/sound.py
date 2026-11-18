"""rc.sound — post-production sound for an rc scene (deliverable 2 / pipeline phase 12, 2026-11-18). Pure Python (numpy + scipy).
Builds a stereo 48 kHz track that follows the scene's OWN events, so every interaction and effect is heard where it is seen:
  beds     breeze + birds for the whole length (seeded)
  physics  crash -> timber tear + wood crack + metal snaps at the computed release frame; drop -> push thump; roll -> rumble;
           glass_shatter -> glass clinks; collapse -> wood cracks; deform -> metal clink
  fx       fire -> crackle bed over its frames; sparks -> clinks; explosion -> whoosh + boom; dust -> soft thump
  anim     hinge -> door creak (swing squeak) at its open frame; vehicle_drive -> engine rattle while moving
Reuses the procedural generators of templates/audio (sfx_gen.py, dsp.py). Deterministic: every sound has its own seed.
    python3 -m rc.sound <place.json> <assemble report.json> <out.wav>"""
import json, os, sys
import numpy as np

AUD = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "templates", "audio")
sys.path.insert(0, AUD)

def build(P, report, out_wav):
    import sfx_gen as G
    from dsp import SR, st, rng
    import soundfile as sf
    fps = P.get("fps", 30); f0, f1 = P.get("frames", [0, 299]); dur = (f1 - f0 + 1) / fps; n = int(dur * SR) + SR
    mix = np.zeros((2, n)); log = []
    def put(x, t, g=1.0, p=0.0):
        x = np.asarray(x, float); x = st(x) if x.ndim == 1 else x
        if x.shape[0] != 2: x = x.T
        i = max(0, int((t - f0 / fps) * SR)); j = min(n, i + x.shape[1])
        if j > i: mix[0, i:j] += x[0, :j - i] * g * (1 - max(0, p)); mix[1, i:j] += x[1, :j - i] * g * (1 + min(0, p))
    sec = lambda f: f / fps
    put(G.breeze(dur, rng(1), level=.6), sec(f0), .35); put(G.bird_chirps(dur, rng(2), density=.35), sec(f0), .25); log.append("beds: breeze, birds")
    rel = {ph.get("name", ph["type"]): r.get("release") for ph, r in zip(P.get("physics", []), report.get("physics", []))}
    for ph in P.get("physics", []):
        nm = ph.get("name", ph["type"]); f = rel.get(nm) or ph.get("at_frame") or ph.get("release")
        if f is None: continue
        t = sec(f)
        if ph["type"] == "crash": put(G.timber_tear(rng(10)), t, .9); put(G.wood_crack(rng(11)), t + .05, .9); [put(G.bolt_snap(rng(12 + k)), t + .08 * k, .35) for k in range(3)]
        elif ph["type"] == "drop": put(G.push_thump(rng(20)), t + .25, .8)
        elif ph["type"] == "roll": put(G.rattle(1.8, rng(21), density=14.0, heavy=True), t - .6, .4)
        elif ph["type"] == "glass_shatter": [put(G.clink(rng(30 + k), bright=1.6), t + .02 * k, .5) for k in range(10)]
        elif ph["type"] == "collapse": [put(G.wood_crack(rng(40 + k)), t + .15 * k, .5) for k in range(3)]
        elif ph["type"] == "deform": put(G.clink(rng(50), f0=180, dur=.3), t, .6)
        log.append("%s @f%d" % (nm, f))
    for e in P.get("fx", []):
        f = report.get("fx_frames", {}).get(e.get("name", e["type"])) if isinstance(e.get("frame"), str) else e.get("frame")
        if e["type"] == "fire":
            a, b = e["frames"]; put(G.rattle(sec(b - a), rng(60), density=22.0) * .5, sec(a), .25); log.append("fire crackle f%d-%d" % (a, b))
        elif f is None: continue
        elif e["type"] == "sparks": [put(G.clink(rng(70 + k), bright=2.0, dur=.06), sec(f) + .03 * k, .25) for k in range(6)]
        elif e["type"] == "explosion_stylized": put(G.whoosh(1.2, rng(80), peak=.1, f_lo=80, f_hi=900), sec(f) - .05, .9); put(G.wood_crack(rng(81)), sec(f), .7); log.append("blast @f%d" % f)
        elif e["type"] == "dust_burst": put(G.push_thump(rng(90)), sec(f), .35)
    for a in P.get("animation", []):
        if a["type"] == "hinge": put(G.swing_squeak(rng(100), a=1.0), sec(a["open"]), .6); log.append("door creak @f%d" % a["open"])
        if a["type"] == "vehicle_drive":
            s = a.get("start", a["frames"][0]); put(G.rattle(sec(a["frames"][1] - s), rng(110), density=40.0, heavy=True), sec(s), .35); log.append("engine from f%d" % s)
    pk = float(np.abs(mix).max()) or 1.0; mix = mix / pk * .89                          # peak at -1 dBFS
    sf.write(out_wav, mix[:, :int(dur * SR)].T, SR); return {"wav": out_wav, "seconds": round(dur, 2), "events": log}

if __name__ == "__main__":
    a = sys.argv[1:]; print(json.dumps(build(json.load(open(a[0])), json.load(open(a[1])), a[2]), indent=1))

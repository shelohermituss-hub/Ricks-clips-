"""ISOLATED ANALYSIS SCRIPT (style_analysis, priority 3, 2026-11-20). The audio cannot be listened to here; this measures what can be
measured from the signal and the word timings:
  - music bed: level during the gaps between words (>= 120 ms, away from word edges by 40 ms) vs level during words -> voice-to-bed ratio
  - bed presence: share of gaps whose level is above -50 dBFS (silence would be lower)
  - tonal bed: spectral flatness in gaps (low = tonal / musical, high = noise)
  - band balance: sub-bass (<120 Hz) / low-mid / presence (2-5 kHz) / air (>8 kHz) in words and in gaps
  - SFX candidates: onsets (>9 dB rise in 50 ms) NOT within 60 ms of a word start, with their peak level over the local bed
    .venv/bin/python references/style_analysis/tools/audio_layers.py V01"""
import sys, os, json, subprocess, tempfile
import numpy as np, soundfile as sf
A = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); V = sys.argv[1]
wav = os.path.join(tempfile.mkdtemp(), "a.wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(A, "_sources", V + ".mp4"), "-ac", "1", "-ar", "22050", wav], check=True)
x, sr = sf.read(wav); words = json.load(open(os.path.join(A, "data", V, "words.json")))["words"]
def db(a): return 20 * np.log10(np.sqrt(np.mean(a ** 2)) + 1e-9)
inw = np.zeros(len(x), bool)
for w in words: inw[int(max(0, w["s"] - .04) * sr):int((w["e"] + .04) * sr)] = True
gaps = []; i = 0
while i < len(x):
    if not inw[i]:
        j = i
        while j < len(x) and not inw[j]: j += 1
        if (j - i) / sr >= .12: gaps.append((i, j))
        i = j
    else: i += 1
def bands(seg):
    if len(seg) < 2048: return None
    S = np.abs(np.fft.rfft(seg[:len(seg) // 2048 * 2048].reshape(-1, 2048) * np.hanning(2048), axis=1)) ** 2; P = S.mean(0); f = np.fft.rfftfreq(2048, 1 / sr)
    tot = P.sum() + 1e-12; g = lambda a, b: float(P[(f >= a) & (f < b)].sum() / tot)
    flat = float(np.exp(np.mean(np.log(S + 1e-12), axis=1)).mean() / (S.mean(axis=1).mean() + 1e-12))
    return {"sub_<120Hz": round(g(0, 120), 3), "low_120-500": round(g(120, 500), 3), "mid_500-2k": round(g(500, 2000), 3), "presence_2-5k": round(g(2000, 5000), 3), "air_>8k": round(g(8000, sr / 2), 3), "flatness": round(flat, 4)}
gx = np.concatenate([x[a:b] for a, b in gaps]) if gaps else np.zeros(1); wx = x[inw]
gap_db = [db(x[a:b]) for a, b in gaps]
hop = int(sr * .05); env = np.array([db(x[k:k + hop]) for k in range(0, len(x) - hop, hop)]); rise = np.diff(env)
starts = [w["s"] for w in words]; sfx = []
for k in range(1, len(rise) - 1):
    if rise[k] > 9 and rise[k] >= rise[k - 1] and rise[k] >= rise[k + 1]:
        t = (k + 1) * .05
        if min(abs(t - s) for s in starts) > .06:
            loc = np.median(env[max(0, k - 20):k]); pk = env[k + 1:k + 4].max()
            sfx.append({"t": round(t, 2), "peak_dbfs": round(float(pk), 1), "over_local_bed_db": round(float(pk - loc), 1)})
r = {"video": V, "method": __doc__.split("\n")[1:9], "voice_dbfs_rms": round(db(wx), 1), "gaps_count": len(gaps), "gaps_total_s": round(sum(b - a for a, b in gaps) / sr, 2),
     "bed_dbfs_rms_in_gaps": round(db(gx), 1), "voice_to_bed_db": round(db(wx) - db(gx), 1), "gaps_above_-50dBFS_share": round(float(np.mean([g > -50 for g in gap_db])) if gap_db else 0, 2),
     "bands_words": bands(wx), "bands_gaps": bands(gx), "sfx_candidates_off_word_onsets": sfx, "sfx_count": len(sfx)}
json.dump(r, open(os.path.join(A, "data", V, "audio_layers.json"), "w"), indent=1)
print(V, "voice %.1f dBFS | bed %.1f dBFS | voice-bed %.1f dB | gaps %d (%.1f s) bed present %.0f%% | flatness gaps %.3f words %.3f | sfx candidates %d" % (
    r["voice_dbfs_rms"], r["bed_dbfs_rms_in_gaps"], r["voice_to_bed_db"], r["gaps_count"], r["gaps_total_s"], 100 * r["gaps_above_-50dBFS_share"], (r["bands_gaps"] or {}).get("flatness", 0), (r["bands_words"] or {}).get("flatness", 0), r["sfx_count"]))

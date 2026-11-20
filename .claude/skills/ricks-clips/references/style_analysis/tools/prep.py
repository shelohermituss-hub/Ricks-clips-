"""ISOLATED ANALYSIS SCRIPT (style_analysis mission, 2026-11-20). Not part of the production pipeline.
For one source video it writes, under references/style_analysis/:
  data/<V>/tech.json        ffprobe facts + SHA-256
  data/<V>/frame_diff.json  mean absolute difference between consecutive frames (every frame, 90x160 grey) + histogram distance
  data/<V>/cuts_auto.json   cut / fast-transition candidates from the two signals (to be verified by eye)
  data/<V>/per_second.json  luma, saturation, contrast, motion per second
  data/<V>/audio.json       EBU R128 loudness, RMS envelope (50 ms), onset times
  data/<V>/words.json       word timings (faster-whisper small.en) unless --no-whisper
  evidence/<V>/overview_XX.jpg   contact sheets at 2 fps with frame numbers
  _work/<V>/f10/            frames at 10 fps, 360x640 (not in git; regenerate with this script)
    .venv/bin/python references/style_analysis/tools/prep.py V01 "<title>" """
import sys, os, json, subprocess, hashlib, glob
import numpy as np, cv2
HERE = os.path.dirname(os.path.abspath(__file__)); A = os.path.dirname(HERE)
V = sys.argv[1]; title = sys.argv[2]; src = os.path.join(A, "_sources", V + ".mp4")
D = os.path.join(A, "data", V); E = os.path.join(A, "evidence", V); W = os.path.join(A, "_work", V)
for d in (D, E, W, os.path.join(W, "f10")): os.makedirs(d, exist_ok=True)
def run(*a): return subprocess.run(a, capture_output=True, text=True)
pr = json.loads(run("ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", src).stdout)
vs = [s for s in pr["streams"] if s["codec_type"] == "video" and s["codec_name"] != "mjpeg"][0]; au = [s for s in pr["streams"] if s["codec_type"] == "audio"]
h = hashlib.sha256(open(src, "rb").read()).hexdigest()
tech = {"id": V, "title": title, "file": os.path.basename(src), "size_bytes": os.path.getsize(src), "sha256": h, "duration_s": float(pr["format"]["duration"]),
        "width": vs["width"], "height": vs["height"], "ratio": "9:16" if vs["width"] * 16 == vs["height"] * 9 else "%d:%d" % (vs["width"], vs["height"]),
        "fps": vs["r_frame_rate"], "frames": int(vs["nb_frames"]), "video_codec": vs["codec_name"], "video_profile": vs.get("profile"), "pix_fmt": vs.get("pix_fmt"),
        "video_bitrate": int(vs.get("bit_rate", 0)), "audio_codec": au[0]["codec_name"] if au else None, "audio_rate": int(au[0]["sample_rate"]) if au else None,
        "audio_channels": au[0]["channels"] if au else None, "audio_bitrate": int(au[0].get("bit_rate", 0)) if au else None, "bitrate_total": int(pr["format"]["bit_rate"]),
        "tags": pr["format"].get("tags", {})}
json.dump(tech, open(os.path.join(D, "tech.json"), "w"), indent=1)
cap = cv2.VideoCapture(src); prev = None; prevh = None; diffs = []; hd = []; sec = {}; n = 0
while True:
    ok, fr = cap.read()
    if not ok: break
    small = cv2.resize(fr, (90, 160), interpolation=cv2.INTER_AREA); g = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY).astype(np.float32)
    hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV); hist = cv2.calcHist([hsv], [0, 1], None, [16, 8], [0, 180, 0, 256]).flatten(); hist /= hist.sum() + 1e-9
    d = float(np.abs(g - prev).mean()) if prev is not None else 0.0; x = float(np.abs(hist - prevh).sum()) if prevh is not None else 0.0
    diffs.append(round(d, 2)); hd.append(round(x, 3)); prev, prevh = g, hist
    rgb = small[..., ::-1].astype(np.float32) / 255; lum = (rgb * [.2126, .7152, .0722]).sum(2); mx, mn = rgb.max(2), rgb.min(2); sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    s = sec.setdefault(n // 30, {"luma": [], "sat": [], "con": [], "mot": []}); s["luma"].append(lum.mean()); s["sat"].append(sat.mean()); s["con"].append(lum.std()); s["mot"].append(d)
    n += 1
cap.release()
json.dump({"frames_decoded": n, "diff": diffs, "hist": hd}, open(os.path.join(D, "frame_diff.json"), "w"))
dd = np.array(diffs); hh = np.array(hd); cuts = []
for i in range(2, n - 2):
    loc = np.median(dd[max(0, i - 8):i + 9]) + 1e-3
    if (dd[i] > 18 and dd[i] > 3.5 * loc) or (hh[i] > .9 and dd[i] > 10):
        kind = "hard_cut" if dd[i] > 3.5 * max(dd[i - 1], dd[i + 1], 1e-3) or hh[i] > .9 else "fast_move_or_transition"
        cuts.append({"frame": i, "t": round(i / 30, 3), "diff": float(dd[i]), "hist": float(hh[i]), "kind": kind})
json.dump({"method": "frame diff 90x160 grey > 18 and > 3.5 x local median, or HSV histogram L1 > .9; candidates only, verified by eye in the per-video analysis", "candidates": cuts},
          open(os.path.join(D, "cuts_auto.json"), "w"), indent=1)
json.dump([{"s": k, **{a: round(float(np.mean(v)), 3) for a, v in s.items()}} for k, s in sorted(sec.items())], open(os.path.join(D, "per_second.json"), "w"))
run("ffmpeg", "-v", "error", "-y", "-i", src, "-vf", "fps=10,scale=360:640", "-q:v", "4", os.path.join(W, "f10", "t%04d.jpg"))
run("ffmpeg", "-v", "error", "-y", "-i", src, "-vf", "fps=2,scale=180:320,drawtext=text='%{eif\\:n*15\\:d}':x=4:y=4:fontsize=20:fontcolor=white:box=1:boxcolor=black@0.6,tile=10x4", "-q:v", "4", os.path.join(E, "overview_%02d.jpg"))
wav = os.path.join(W, "a.wav"); run("ffmpeg", "-v", "error", "-y", "-i", src, "-ac", "1", "-ar", "16000", wav)
st = os.path.join(W, "st.wav"); run("ffmpeg", "-v", "error", "-y", "-i", src, "-ar", "44100", st)
lo = run("ffmpeg", "-hide_banner", "-i", src, "-af", "ebur128=peak=true", "-f", "null", "-").stderr
import re, soundfile as sf
summ = lo[lo.rfind("Summary:"):]; g = lambda k: (re.search(k + r":\s*(-?[\d.]+)", summ) or [None, None])[1]
x, sr = sf.read(wav); hop = int(sr * .05); rms = [float(np.sqrt(np.mean(x[i:i + hop] ** 2) + 1e-12)) for i in range(0, len(x) - hop, hop)]; db = 20 * np.log10(np.array(rms) + 1e-9)
flux = np.maximum(0, np.diff(db)); on = [round((i + 1) * .05, 2) for i in range(1, len(flux) - 1) if flux[i] > 9 and flux[i] >= flux[i - 1] and flux[i] >= flux[i + 1]]
y, sr2 = sf.read(st); corr = float(np.corrcoef(y[:, 0], y[:, 1])[0, 1]) if y.ndim == 2 else 1.0
quiet = []; run_ = None
for i, v in enumerate(db):
    if v < -45: run_ = i if run_ is None else run_
    else:
        if run_ is not None and i - run_ >= 4: quiet.append([round(run_ * .05, 2), round(i * .05, 2)])
        run_ = None
json.dump({"integrated_lufs": g("I"), "loudness_range_lu": g("LRA"), "true_peak_dbfs": g("Peak"), "stereo_lr_correlation": round(corr, 3), "rms_db_50ms": [round(float(v), 1) for v in db],
           "onsets_s_(rise>9dB/50ms)": on, "quiet_spans_s_(<-45dB,>=0.2s)": quiet}, open(os.path.join(D, "audio.json"), "w"))
if "--no-whisper" not in sys.argv:
    from faster_whisper import WhisperModel
    m = WhisperModel("small.en", device="cpu", compute_type="int8"); segs, _ = m.transcribe(x.astype(np.float32), word_timestamps=True)   # the samples themselves: PyAV in this venv cannot open the file (metadata_errors bug)
    words = [{"w": w.word.strip(), "s": round(w.start, 2), "e": round(w.end, 2)} for s in segs for w in s.words]
    json.dump({"model": "faster-whisper small.en (timings +-0.1 s; text may contain recognition errors)", "words": words}, open(os.path.join(D, "words.json"), "w"), indent=0)
print("PREP", V, n, "frames", len(cuts), "cut candidates", len(glob.glob(os.path.join(W, "f10", "*.jpg"))), "frames@10fps")

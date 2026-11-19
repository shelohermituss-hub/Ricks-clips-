"""Analyse a REFERENCE VIDEO the same way every time (CB 2026-11-19: "je te donne d'autres vidéos de référence pour que tu comprennes
exactement ce que je veux"; method: docs/PREPRODUCTION_FR.md "Ajouter une vidéo de référence à la base de style").
    python3 tools/analyze_reference.py <video.mp4> <slug>          -> references/<slug>/
Writes (the source video and big extractions stay LOCAL, .gitignore written in the folder):
  source.mp4 (copy, ignored)          specs.json   format, fps, duration, bitrate, audio
  ref_measures.json   reference_compare.measure: per second luma / saturation / motion / edge, hard cuts, action peaks
  loudness.json       EBU R128 integrated LUFS + loudness range (ffmpeg ebur128)
  words.json, transcript.txt, voice.json   faster-whisper word times; words/s, longest pause, pauses > 0.35 s
  shots.json          shots between hard cuts (start, end, length, the words spoken in it)
  sheet_NN.jpg        contact sheets, 2 frames per second, 20 frames a sheet, time stamped (to LOOK at every shot)
  summary.json        the numbers that go into references/STYLE_BIBLE_FR.md section 9
"""
import json, os, shutil, statistics, subprocess, sys
import numpy as np
SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(SKILL, "tools"))

def run(a): return subprocess.run(a, capture_output=True, text=True)

def specs(src):
    p = json.loads(run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", src]).stdout)
    v = next(s for s in p["streams"] if s["codec_type"] == "video"); a = next((s for s in p["streams"] if s["codec_type"] == "audio"), {})
    n, d = map(int, v["r_frame_rate"].split("/"))
    return {"width": v["width"], "height": v["height"], "fps": round(n / d, 3), "duration_s": round(float(p["format"]["duration"]), 2),
            "video_kbps": round(int(p["format"].get("bit_rate", 0)) / 1000), "audio": {"codec": a.get("codec_name"), "rate": a.get("sample_rate"), "channels": a.get("channels")}}

def loudness(src):
    e = run(["ffmpeg", "-nostats", "-i", src, "-filter_complex", "ebur128", "-f", "null", "-"]).stderr.splitlines()
    I = [l for l in e if l.strip().startswith("I:")]; LRA = [l for l in e if l.strip().startswith("LRA:")]
    return {"integrated_lufs": float(I[-1].split()[1]) if I else None, "lra_lu": float(LRA[-1].split()[1]) if LRA else None}

def words(src):
    from faster_whisper import WhisperModel
    m = WhisperModel(os.environ.get("RICKCLIPS_WHISPER_MODEL", "small.en"), device="cpu", compute_type="int8")
    pcm = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", src, "-f", "s16le", "-ac", "1", "-ar", "16000", "-"], capture_output=True, check=True).stdout
    segs, _ = m.transcribe(np.frombuffer(pcm, np.int16).astype(np.float32) / 32768.0, word_timestamps=True, beam_size=5, vad_filter=False)
    return [{"w": w.word.strip(), "s": round(float(w.start), 3), "e": round(float(w.end), 3)} for s in segs for w in s.words]

def sheets(src, out, dur):
    tmp = os.path.join(out, "_sheet_frames"); os.makedirs(tmp, exist_ok=True)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", src, "-vf", "fps=2,scale=216:384", os.path.join(tmp, "f%04d.jpg")], check=True)
    from PIL import Image, ImageDraw
    fl = sorted(os.listdir(tmp)); k = 0
    for i in range(0, len(fl), 20):
        S = Image.new("RGB", (216 * 10, 384 * 2), "black"); d = ImageDraw.Draw(S)
        for j, f in enumerate(fl[i:i + 20]):
            S.paste(Image.open(os.path.join(tmp, f)), ((j % 10) * 216, (j // 10) * 384)); d.rectangle(((j % 10) * 216, (j // 10) * 384, (j % 10) * 216 + 52, (j // 10) * 384 + 16), fill="black")
            d.text(((j % 10) * 216 + 3, (j // 10) * 384 + 2), "%.1fs" % ((i + j) / 2), fill="yellow")
        S.save(os.path.join(out, "sheet_%02d.jpg" % k), quality=85); k += 1
    shutil.rmtree(tmp); return k

def main(src, slug):
    out = os.path.join(SKILL, "references", slug); os.makedirs(out, exist_ok=True)
    open(os.path.join(out, ".gitignore"), "w").write("source.mp4\n*.wav\nframes/\nhi/\nshots/*/\n")
    dst = os.path.join(out, "source.mp4")
    if not os.path.exists(dst): shutil.copy(src, dst)
    S = specs(dst); json.dump(S, open(os.path.join(out, "specs.json"), "w"), indent=1)
    import reference_compare
    M = reference_compare.measure(dst); json.dump(M, open(os.path.join(out, "ref_measures.json"), "w"), indent=1)
    Ld = loudness(dst); json.dump(Ld, open(os.path.join(out, "loudness.json"), "w"), indent=1)
    W = words(dst); json.dump(W, open(os.path.join(out, "words.json"), "w"), indent=0)
    open(os.path.join(out, "transcript.txt"), "w").write(" ".join(w["w"] for w in W) + "\n")
    gaps = [round(b["s"] - a["e"], 3) for a, b in zip(W, W[1:])]; talk_end = W[-1]["e"] if W else 0
    V = {"words": len(W), "words_per_s": round(len(W) / max(talk_end - (W[0]["s"] if W else 0), 1e-6), 2), "voice_from_s": W[0]["s"] if W else None,
         "voice_to_s": talk_end, "longest_pause_s": max(gaps) if gaps else 0, "pauses_over_0_35": [(round(W[i]["e"], 2), g) for i, g in enumerate(gaps) if g > .35]}
    json.dump(V, open(os.path.join(out, "voice.json"), "w"), indent=1)
    cuts = [0.0] + M["hard_cuts"] + [M["seconds"]]
    shots = [{"n": i + 1, "t0": a, "t1": b, "len_s": round(b - a, 2), "words": " ".join(w["w"] for w in W if a <= w["s"] < b)} for i, (a, b) in enumerate(zip(cuts, cuts[1:])) if b - a > .05]
    json.dump(shots, open(os.path.join(out, "shots.json"), "w"), indent=1)
    ns = sheets(dst, out, S["duration_s"])
    per = [p["motion"] for p in M["per_second"]]; o = M["overall"]
    SUM = {"slug": slug, "duration_s": S["duration_s"], "resolution": "%dx%d" % (S["width"], S["height"]), "fps": S["fps"], "words": V["words"], "words_per_s": V["words_per_s"],
           "longest_pause_s": V["longest_pause_s"], "lufs": Ld["integrated_lufs"], "lra": Ld["lra_lu"], "hard_cuts": o["hard_cuts"], "seconds_per_hard_cut": round(S["duration_s"] / max(1, o["hard_cuts"]), 2),
           "motion_per_second_median": round(statistics.median(per), 1), "motion_median_x1000": o["motion_median_x1000"], "peaks_per_10s": o["peaks_per_10s"],
           "luma": o["luma"], "saturation": o["saturation"], "contrast": o["contrast"], "edge_detail": o["edge_detail"], "still_frames_pct": o["still_frames_pct"], "sheets": ns}
    json.dump(SUM, open(os.path.join(out, "summary.json"), "w"), indent=1); print(json.dumps(SUM)); return SUM

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

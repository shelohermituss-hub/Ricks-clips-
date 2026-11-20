"""Assemble a rendered shot into a watchable clip: frames -> video, white flash on the last frames (optional), word-by-word captions
(white bold, thick black outline, centred at 70 % of the height, one or two words at a time) and the voice.
    python3 finish_clip.py <frames dir with f####.png> <first frame> <last frame> <out.mp4> [--flash N]"""
import sys, json, os, subprocess
H = os.path.dirname(os.path.abspath(__file__)); EP = os.path.join(H, "..")
d, f0, f1, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]; flash = int(sys.argv[sys.argv.index("--flash") + 1]) if "--flash" in sys.argv else 0
W = json.load(open(os.path.join(EP, "voice", "words.json"))); t0, t1 = f0 / 30.0, (f1 + 1) / 30.0
font = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; vf = ["scale=540:960:flags=lanczos"]
ws = [w for w in W if t0 - .01 <= w["s"] < t1]; i = 0
while i < len(ws):                                                              # short words are shown with the next one (1-2 words per caption)
    grp = [ws[i]]
    if len(ws[i]["w"]) <= 3 and i + 1 < len(ws) and ws[i + 1]["s"] - ws[i]["e"] < .25: grp.append(ws[i + 1])
    a = grp[0]["s"] - t0; b = (ws[i + len(grp)]["s"] - t0) if i + len(grp) < len(ws) else (t1 - t0)
    txt = " ".join(g["w"] for g in grp).replace("'", "’").replace(":", "\\:").replace(",", "\\,")
    vf.append("drawtext=fontfile=%s:text='%s':fontsize=46:fontcolor=white:borderw=5:bordercolor=black:x=(w-text_w)/2:y=h*0.70-text_h/2:enable='between(t,%.3f,%.3f)'" % (font, txt, a, b - .001))
    i += len(grp)
if flash:
    n = f1 - f0 + 1; vf.append("fade=t=out:st=%.3f:d=%.3f:color=white" % ((n - flash) / 30.0, flash / 30.0))
cmd = ["ffmpeg", "-v", "error", "-y", "-framerate", "30", "-start_number", str(f0), "-i", os.path.join(d, "f%04d.png"), "-ss", "%.3f" % t0, "-t", "%.3f" % (t1 - t0), "-i", os.path.join(EP, "voice", "voice.wav"),
       "-vf", ",".join(vf), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "17", "-c:a", "aac", "-b:a", "160k", "-shortest", out]
subprocess.run(cmd, check=True); print("CLIP", out)

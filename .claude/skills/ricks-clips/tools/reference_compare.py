"""Measure a video against the official reference standard (fortress reference, REFERENCE_LOOK_BIBLE.md v2.0).
    .venv/bin/python tools/reference_compare.py <video.mp4> [--out result.json] [--night-from S --night-to S ...]
Used by `production_controller.py compare-reference` and gate F. Same metrics that measured the reference (2026-11-18):
frames scaled to 90x160, Rec.709 luma; saturation (max-min)/max; crushed <0.02; burned >0.98; contrast = per-frame luma std;
motion = mean |luma(t)-luma(t-1)| x1000; still frame = motion < 2; edge detail = mean |vertical| + mean |horizontal| luma difference between neighbour pixels;
peaks = local maxima of the 8-frame luma change above 0.08 at least 15 frames apart (transitions or fast moves);
hard cut = a one-frame histogram jump with no change around it."""
import json, os, subprocess, sys
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STD = os.path.join(ROOT, "production", "config", "reference_standard.json")
W, H = 90, 160

def frames(src):
    p = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", src, "-map", "0:v:0", "-vf", "scale=%d:%d,fps=30" % (W, H), "-pix_fmt", "rgb24", "-f", "rawvideo", "-"], capture_output=True)
    if p.returncode or not p.stdout: raise SystemExit("ffmpeg could not read %s: %s" % (src, p.stderr.decode()[-300:]))
    return np.frombuffer(p.stdout, np.uint8).reshape(-1, H, W, 3).astype(np.float32) / 255

def measure(src):
    a = frames(src); n = len(a)
    L = a @ np.array([.2126, .7152, .0722], np.float32); mx, mn = a.max(-1), a.min(-1); S = (mx - mn) / np.clip(mx, 1e-4, None)
    diff = np.r_[0, np.abs(np.diff(L, axis=0)).mean((1, 2))]
    edge = np.abs(np.diff(L, axis=1)).mean((1, 2)) + np.abs(np.diff(L, axis=2)).mean((1, 2))
    d8 = np.r_[np.zeros(8), np.abs(L[8:] - L[:-8]).mean((1, 2))]
    peaks, last = [], -99
    for i in range(1, n - 1):
        if d8[i] > .08 and d8[i] >= d8[i - 1] and d8[i] >= d8[i + 1] and i - last >= 15: peaks.append(i); last = i
    hist = np.stack([np.histogram(x, bins=32, range=(0, 1))[0] for x in L]).astype(np.float32); hist /= hist.sum(1, keepdims=True)
    hd = np.r_[0, .5 * np.abs(np.diff(hist, axis=0)).sum(1)]; med = np.median(diff)
    cuts = [i for i in range(1, n) if hd[i] > .18 and diff[i] > max(.06, 6 * med) and (i < 2 or diff[i] > 3 * max(diff[i - 1], diff[i + 1] if i + 1 < n else 0, 1e-3))]
    sec = lambda s: slice(s * 30, (s + 1) * 30)
    per = [dict(t=s, luma=round(float(L[sec(s)].mean()), 3), sat=round(float(S[sec(s)].mean()), 3), crushed=round(float((L[sec(s)] < .02).mean()), 4),
                burned=round(float((L[sec(s)] > .98).mean()), 4), motion=round(float(diff[sec(s)].mean() * 1000), 2), edge=round(float(edge[sec(s)].mean()), 4))
           for s in range(int(np.ceil(n / 30)))]
    dur = n / 30
    return dict(video=src, frames=n, seconds=round(dur, 2), per_second=per, hard_cuts=[round(c / 30, 2) for c in cuts], peaks=[round(p / 30, 2) for p in peaks],
                overall=dict(luma=round(float(L.mean()), 3), saturation=round(float(S.mean()), 3), contrast=round(float(L.std((1, 2)).mean()), 3),
                             crushed=round(float((L < .02).mean()), 4), burned=round(float((L > .98).mean()), 4), motion_median_x1000=round(float(med * 1000), 2),
                             still_frames_pct=round(float((diff < .002).mean() * 100), 1), edge_detail=round(float(edge.mean()), 4),
                             hard_cuts=len(cuts), peaks_per_10s=round(len(peaks) / dur * 10, 2)))

def compare(m, night=()):
    std = json.load(open(STD)); T = std["thresholds"]; o = m["overall"]; R = []
    def add(k, ok, val, target, warn=False): R.append(dict(metric=k, value=val, target=target, status="PASS" if ok else ("WARN" if warn else "FAIL")))
    isn = lambda t: any(a <= t < b for a, b in night)
    day = [p for p in m["per_second"] if not isn(p["t"])]; nig = [p for p in m["per_second"] if isn(p["t"])]
    add("edge_detail", o["edge_detail"] >= T["edge_detail_min"], o["edge_detail"], ">= %s (ref %s)" % (T["edge_detail_min"], std["measured_reference"]["edge_detail"]))
    dl = round(float(np.mean([p["luma"] for p in day])), 3) if day else None
    add("luma_day", dl is None or T["luma_day"][0] <= dl <= T["luma_day"][1], dl, "%s-%s" % tuple(T["luma_day"]))
    if nig: nl = round(float(np.mean([p["luma"] for p in nig])), 3); add("luma_night", nl >= T["luma_night_min"], nl, ">= %s" % T["luma_night_min"])
    add("crushed", o["crushed"] <= T["crushed_max"], o["crushed"], "<= %s" % T["crushed_max"])
    add("burned", o["burned"] <= T["burned_max"], o["burned"], "<= %s" % T["burned_max"])
    add("saturation", T["saturation"][0] <= o["saturation"] <= T["saturation"][1], o["saturation"], "%s-%s (ref %s)" % (T["saturation"][0], T["saturation"][1], std["measured_reference"]["saturation"]))
    hot = [p["t"] for p in m["per_second"] if p["sat"] > T["saturation_shot_max"]]
    add("saturation_seconds_over_max", not hot, len(hot), "0 s above %s (seconds: %s)" % (T["saturation_shot_max"], hot[:20]))
    add("still_frames_pct", o["still_frames_pct"] <= T["still_frames_pct_max"], o["still_frames_pct"], "<= %s" % T["still_frames_pct_max"])
    add("motion_median_x1000", o["motion_median_x1000"] >= T["motion_median_min_x1000"], o["motion_median_x1000"], ">= %s (ref %s)" % (T["motion_median_min_x1000"], std["measured_reference"]["motion_median_x1000"]))
    add("peaks_per_10s", o["peaks_per_10s"] >= T["peaks_per_10s_min"], o["peaks_per_10s"], ">= %s (ref %s)" % (T["peaks_per_10s_min"], std["measured_reference"]["peaks_per_10s"]))
    add("hard_cuts", o["hard_cuts"] == 0, o["hard_cuts"], "0 unless listed as deliberate in DECISIONS.md (at %s s)" % m["hard_cuts"], warn=True)
    return R

if __name__ == "__main__":
    a = sys.argv[1:]; src = a[0]; out = a[a.index("--out") + 1] if "--out" in a else None
    night = [(float(a[i + 1]), float(a[i + 3])) for i in range(len(a)) if a[i] == "--night-from"]
    m = measure(src); R = compare(m, night); m["compare"] = R
    for r in R: print("%-5s %-28s %-10s %s" % (r["status"], r["metric"], r["value"], r["target"]))
    print("overall", m["overall"])
    if out: json.dump(m, open(out, "w"), indent=1)

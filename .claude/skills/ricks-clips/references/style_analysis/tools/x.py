"""ISOLATED ANALYSIS HELPERS (style_analysis mission). Run with .venv/bin/python from the skill folder.
  seq  <V> <f0> <f1> [step]      every frame f0..f1 (step 1 = frame by frame) -> _work/<V>/seq_<f0>_<f1>/f%05d.jpg (360x640)
                                 + contact sheets _work/<V>/seq_<f0>_<f1>/sheet_NN.jpg (8 x 3 tiles, frame number burnt in). READ THE SHEETS.
  still <V> <frame> [name]       one full-resolution evidence still -> evidence/<V>/<V>_f<frame>[_name].jpg (720x1280, kept in git)
  crop <V> <frame> x0 y0 x1 y1 [name]   an enlarged crop (source pixels, 720x1280 space) -> evidence/<V>/<V>_f<frame>_crop[_name].jpg
  color <V> <frame> x0 y0 x1 y1 [label] mean colour of a region: sRGB hex, HSV (deg, %, %), CIE Lab, n pixels, std -> printed as JSON
  kmeans <V> <frame> [k]         dominant colours of a whole frame (k-means in Lab, k=6): hex + share
Frame numbers are 0-based source frames at 30 fps; timecode = frame / 30."""
import sys, os, json, subprocess, glob
import numpy as np, cv2
HERE = os.path.dirname(os.path.abspath(__file__)); A = os.path.dirname(HERE)
cmd, V = sys.argv[1], sys.argv[2]; src = os.path.join(A, "_sources", V + ".mp4")
def frame(n):
    cap = cv2.VideoCapture(src); cap.set(cv2.CAP_PROP_POS_FRAMES, n); ok, fr = cap.read(); cap.release()
    if not ok: sys.exit("cannot read frame %d" % n)
    return fr
def tc(n): s = n / 30.0; return "%02d:%02d:%06.3f" % (0, int(s // 60), s % 60)
if cmd == "seq":
    f0, f1 = int(sys.argv[3]), int(sys.argv[4]); step = int(sys.argv[5]) if len(sys.argv) > 5 else 1
    out = os.path.join(A, "_work", V, "seq_%d_%d" % (f0, f1)); os.makedirs(out, exist_ok=True)
    cap = cv2.VideoCapture(src); cap.set(cv2.CAP_PROP_POS_FRAMES, f0); tiles = []; n = f0
    while n <= f1:
        ok, fr = cap.read()
        if not ok: break
        if (n - f0) % step == 0:
            sm = cv2.resize(fr, (360, 640), interpolation=cv2.INTER_AREA); cv2.imwrite(os.path.join(out, "f%05d.jpg" % n), sm, [cv2.IMWRITE_JPEG_QUALITY, 85])
            t = cv2.resize(fr, (225, 400), interpolation=cv2.INTER_AREA); cv2.rectangle(t, (0, 0), (118, 24), (0, 0, 0), -1)
            cv2.putText(t, "%d %.2fs" % (n, n / 30), (3, 17), cv2.FONT_HERSHEY_SIMPLEX, .5, (255, 255, 255), 1, cv2.LINE_AA); tiles.append(t)
        n += 1
    cap.release(); sheets = []
    for i in range(0, len(tiles), 24):
        grp = tiles[i:i + 24]; grp += [np.zeros_like(tiles[0])] * (24 - len(grp)); rows = [np.hstack(grp[r * 8:(r + 1) * 8]) for r in range(3)]
        p = os.path.join(out, "sheet_%02d.jpg" % (i // 24)); cv2.imwrite(p, np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 82]); sheets.append(p)
    print(json.dumps({"frames": len(tiles), "range": [f0, f1], "step": step, "sheets": sheets}))
elif cmd == "still":
    n = int(sys.argv[3]); name = ("_" + sys.argv[4]) if len(sys.argv) > 4 else ""; p = os.path.join(A, "evidence", V, "%s_f%05d%s.jpg" % (V, n, name))
    cv2.imwrite(p, frame(n), [cv2.IMWRITE_JPEG_QUALITY, 80]); print(p, tc(n))
elif cmd == "crop":
    n = int(sys.argv[3]); x0, y0, x1, y1 = map(int, sys.argv[4:8]); name = ("_" + sys.argv[8]) if len(sys.argv) > 8 else ""
    c = frame(n)[y0:y1, x0:x1]; k = max(1, int(900 / max(c.shape[:2]))); c = cv2.resize(c, None, fx=k, fy=k, interpolation=cv2.INTER_CUBIC)
    p = os.path.join(A, "evidence", V, "%s_f%05d_crop%s.jpg" % (V, n, name)); cv2.imwrite(p, c, [cv2.IMWRITE_JPEG_QUALITY, 85]); print(p, tc(n))
elif cmd == "color":
    n = int(sys.argv[3]); x0, y0, x1, y1 = map(int, sys.argv[4:8]); label = sys.argv[8] if len(sys.argv) > 8 else ""
    c = frame(n)[y0:y1, x0:x1]; px = c.reshape(-1, 3).astype(np.float32); m = px.mean(0); one = np.uint8([[m]])
    hsv = cv2.cvtColor(one, cv2.COLOR_BGR2HSV)[0, 0]; lab = cv2.cvtColor(np.float32([[m / 255]]), cv2.COLOR_BGR2Lab)[0, 0]
    print(json.dumps({"video": V, "frame": n, "timecode": tc(n), "label": label, "region_xyxy": [x0, y0, x1, y1], "n_pixels": int(len(px)),
                      "hex": "#%02x%02x%02x" % (int(m[2]), int(m[1]), int(m[0])), "rgb": [int(m[2]), int(m[1]), int(m[0])],
                      "hsv_deg_pct": [int(hsv[0]) * 2, round(hsv[1] / 2.55), round(hsv[2] / 2.55)], "lab": [round(float(v), 1) for v in lab],
                      "std_rgb": [round(float(v), 1) for v in px.std(0)[::-1]], "method": "mean of the region in the decoded H.264 frame (8-bit, limited by compression)"}))
elif cmd == "kmeans":
    n = int(sys.argv[3]); k = int(sys.argv[4]) if len(sys.argv) > 4 else 6
    sm = cv2.resize(frame(n), (90, 160), interpolation=cv2.INTER_AREA); lab = cv2.cvtColor(sm.astype(np.float32) / 255, cv2.COLOR_BGR2Lab).reshape(-1, 3)
    _, lb, ce = cv2.kmeans(lab, k, None, (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, .5), 3, cv2.KMEANS_PP_CENTERS)
    out = []
    for i in np.argsort(-np.bincount(lb.flatten(), minlength=k)):
        bgr = cv2.cvtColor(np.float32([[ce[i]]]), cv2.COLOR_Lab2BGR)[0, 0] * 255; out.append({"hex": "#%02x%02x%02x" % tuple(int(max(0, min(255, v))) for v in bgr[::-1]), "share": round(float((lb == i).mean()), 3)})
    print(json.dumps({"video": V, "frame": n, "timecode": tc(n), "k": k, "colors": out, "method": "k-means in CIE Lab on the frame reduced to 90x160"}))

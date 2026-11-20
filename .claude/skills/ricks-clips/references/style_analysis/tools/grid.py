"""ISOLATED ANALYSIS HELPER: a crop of a source frame with a labelled pixel grid (source 720x1280 coordinates), to measure characters by eye.
    .venv/bin/python references/style_analysis/tools/grid.py V01 800 x0 y0 x1 y1 out.jpg [step]"""
import sys, os, cv2
A = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V, f, x0, y0, x1, y1, out = sys.argv[1], int(sys.argv[2]), *map(int, sys.argv[3:7]), sys.argv[7]; step = int(sys.argv[8]) if len(sys.argv) > 8 else 20
cap = cv2.VideoCapture(os.path.join(A, "_sources", V + ".mp4")); cap.set(cv2.CAP_PROP_POS_FRAMES, f); ok, fr = cap.read()
c = fr[y0:y1, x0:x1].copy(); k = max(1, int(1000 / max(c.shape[:2]))); c = cv2.resize(c, None, fx=k, fy=k, interpolation=cv2.INTER_NEAREST)
for x in range(x0 - x0 % step + step, x1, step):
    X = (x - x0) * k; cv2.line(c, (X, 0), (X, c.shape[0]), (0, 255, 255) if x % 100 == 0 else (0, 160, 160), 1)
    if x % 100 == 0: cv2.putText(c, str(x), (X + 2, 14), cv2.FONT_HERSHEY_SIMPLEX, .45, (0, 255, 255), 1)
for y in range(y0 - y0 % step + step, y1, step):
    Y = (y - y0) * k; cv2.line(c, (0, Y), (c.shape[1], Y), (255, 0, 255) if y % 100 == 0 else (160, 0, 160), 1)
    if y % 100 == 0: cv2.putText(c, str(y), (2, Y - 3), cv2.FONT_HERSHEY_SIMPLEX, .45, (255, 0, 255), 1)
cv2.imwrite(out, c, [cv2.IMWRITE_JPEG_QUALITY, 88]); print(out, k)

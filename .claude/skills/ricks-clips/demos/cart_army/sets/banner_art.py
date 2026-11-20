"""the banner of the fort: a white tiger rampant on blue, a gold chevron under it, a gold border.  python3 banner_art.py <out.png>"""
import os, sys
p = sys.argv[1]
from PIL import Image, ImageDraw
W, Hh = 512, 1472; im = Image.new("RGB", (W, Hh), (22, 58, 190)); d = ImageDraw.Draw(im); gold = (236, 190, 50); wh = (240, 240, 235)
d.rectangle((0, 0, W - 1, Hh - 1), outline=gold, width=22)
# the tiger, rampant: body, haunch, head, legs, tail, stripes
d.ellipse((150, 380, 360, 820), fill=wh); d.ellipse((190, 250, 380, 450), fill=wh); d.polygon([(215, 270), (240, 205), (275, 262)], fill=wh); d.polygon([(310, 262), (350, 205), (368, 280)], fill=wh)
for x0, y0, x1, y1 in ((120, 430, 215, 500), (320, 470, 430, 530), (135, 760, 230, 950), (270, 780, 360, 960)): d.rounded_rectangle((x0, y0, x1, y1), 40, fill=wh)
d.arc((40, 520, 250, 900), 60, 250, fill=wh, width=34)
for y in range(430, 800, 62): d.line((175, y, 335, y + 28), fill=(22, 58, 190), width=13)
d.ellipse((235, 318, 262, 345), fill=(20, 20, 30)); d.ellipse((305, 318, 332, 345), fill=(20, 20, 30)); d.polygon([(270, 372), (298, 372), (284, 392)], fill=(20, 20, 30))
d.line([(80, 1260), (256, 1090), (432, 1260)], fill=gold, width=44, joint="curve")
os.makedirs(os.path.dirname(p), exist_ok=True); im.save(p)

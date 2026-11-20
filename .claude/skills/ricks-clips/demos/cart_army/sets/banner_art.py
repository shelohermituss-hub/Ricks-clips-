"""the banner of the fort: a white tiger rampant on blue, a gold chevron under it, a gold border.  python3 banner_art.py <out.png>"""
import os, sys
p = sys.argv[1]
from PIL import Image, ImageDraw
W, Hh = 512, 1472; im = Image.new("RGB", (W, Hh), (22, 58, 190)); d = ImageDraw.Draw(im); gold = (236, 190, 50); wh = (240, 240, 235)
d.rectangle((0, 0, W - 1, Hh - 1), outline=gold, width=22)
# the tiger, rampant (standing on its hind legs, turned to the left, as on the reference's banner): body, head, four legs, tail, stripes
blue = (22, 58, 190)
d.polygon([(215, 880), (160, 620), (190, 430), (270, 360), (345, 430), (360, 640), (330, 880)], fill=wh)            # body, upright
d.ellipse((150, 240, 330, 420), fill=wh); d.polygon([(165, 285), (150, 215), (215, 252)], fill=wh); d.polygon([(275, 250), (330, 212), (322, 290)], fill=wh)   # head and ears
d.polygon([(150, 330), (95, 350), (150, 385)], fill=wh)                                                             # muzzle
d.polygon([(190, 470), (70, 420), (60, 470), (185, 545)], fill=wh); d.polygon([(190, 580), (80, 600), (85, 650), (200, 650)], fill=wh)   # the two fore legs, raised
d.polygon([(215, 860), (150, 1010), (95, 1010), (95, 1050), (200, 1050), (290, 880)], fill=wh)                      # hind legs
d.polygon([(330, 860), (340, 1010), (290, 1010), (290, 1050), (400, 1050), (390, 860)], fill=wh)
d.line([(350, 800), (440, 760), (455, 620), (400, 520), (430, 430)], fill=wh, width=30, joint="curve")              # the tail, in an S
for y in range(450, 860, 58): d.polygon([(350, y), (270, y + 14), (350, y + 26)], fill=blue)                         # stripes from the back
for y in range(480, 840, 70): d.polygon([(175, y + 20), (235, y + 30), (178, y + 44)], fill=blue)
for x in (205, 250): d.polygon([(x, 245), (x + 12, 290), (x + 24, 245)], fill=blue)
d.ellipse((182, 300, 206, 324), fill=(20, 20, 30)); d.polygon([(98, 345), (120, 340), (112, 360)], fill=(20, 20, 30))
d.line([(80, 1260), (256, 1090), (432, 1260)], fill=gold, width=44, joint="curve")
os.makedirs(os.path.dirname(p), exist_ok=True); im.save(p)

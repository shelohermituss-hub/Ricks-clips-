import sys
from PIL import Image, ImageDraw
F=[int(x) for x in sys.argv[3].split(',')]; A,B=sys.argv[1],sys.argv[2]; out=sys.argv[4]
W,H=270,480; rows=[F[i:i+3] for i in range(0,len(F),3)]
sheet=Image.new('RGB',(W*2*3+20,(H+30)*len(rows)),'#111'); d=ImageDraw.Draw(sheet)
for r,grp in enumerate(rows):
    for i,f in enumerate(grp):
        for j,k in enumerate([A,B]): sheet.paste(Image.open(f'{k}/f_{f:05d}.png').resize((W,H)),(i*(2*W+10)+j*W,r*(H+30)+28))
        d.text((i*(2*W+10)+5,r*(H+30)+8),f"f{f}   V3 (gauche) | enrichi + decor (droite)",fill='white')
sheet.save(out,quality=88)

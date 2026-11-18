"""Normandy stone farmhouse (Mission 2 prototype, 2026-11-18). Real architecture, not a box:
walls with true openings (2 storeys), protruding corner quoins, plinth, framed windows (frame, sill, lintel, glazing bars, glass) with plank
shutters, a plank door with iron strap hinges, a roof made of ~2,400 individual overlapping clay tiles on both slopes, ridge tiles,
two stone chimneys with caps, eaves boards, a half-round gutter and a downpipe.
Materials (names the place LookDev maps to PBR sets): stone, quoin, wood_paint (shutters/door), wood (frames), glass, roof, iron.
X = front facade direction (front faces -Y), Z up, ground 0. 10 x 6.5 m footprint, eaves 5.2 m.
    blender -b --python build_normandy_farmhouse.py -- <out dir>"""
import bpy, bmesh, math, os, random, sys
from mathutils import Vector, Matrix
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _blender_kit import reset, mat, root, bm_for, box, cyl, finish, export  # noqa: E402

OUT = sys.argv[sys.argv.index("--") + 1]; R = random.Random(41)
reset()
mat("stone", "#b8ad96", .9); mat("quoin", "#cfc6b2", .85); mat("wood_paint", "#4f6f5a", .7); mat("wood", "#6a5038", .75)
mat("glass", "#3a4a5a", .08, .0); mat("roof", "#7a4a3a", .8); mat("iron", "#2a2826", .5, .6)
H = root("normandy_farmhouse")
W, D, E, T = 10.0, 6.5, 5.2, .5                      # width (x), depth (y), eaves height, wall thickness
S = bm_for("stone")
# windows (x, sill z, w, h) on front (y = -D/2) and back; door on front
FW = [(-3.4, 1.0, 1.0, 1.35), (3.4, 1.0, 1.0, 1.35), (-3.4, 3.4, .9, 1.1), (0, 3.4, .9, 1.1), (3.4, 3.4, .9, 1.1)]
DOOR = (0.0, 0.0, 1.15, 2.2)
def wall_with_holes(y, holes, length=W):
    """a facade as slabs around rectangular holes: columns between holes, pieces above and below each hole"""
    xs = sorted(holes, key=lambda h: h[0]); edges = [-length / 2] + [v for h in xs for v in (h[0] - h[2] / 2, h[0] + h[2] / 2)] + [length / 2]
    for i in range(0, len(edges), 2):                                    # full-height columns between openings
        a, b = edges[i], edges[i + 1]
        if b - a > .01: box(S, ((a + b) / 2, y, E / 2), (b - a, T, E))
    for (x, z, w, h) in xs:                                               # below and above each opening (per hole column)
        if z > .01: box(S, (x, y, z / 2), (w, T, z))
        top = z + h; box(S, (x, y, (top + E) / 2), (w, T, E - top))
# facade holes stacked: split into per-column holes (ground + first floor in the same column)
cols = {}
for h in FW + [DOOR]: cols.setdefault(h[0], []).append(h)
def facade(y, holes):
    xs = sorted({h[0]: max(h[2] for h in hs) for h, hs in [((x, 0, 0, 0), v) for x, v in cols.items()]}.items()) if holes is None else None
front_cols = sorted(cols.items()); edges = [-W / 2]
for x, hs in front_cols: w = max(h[2] for h in hs); edges += [x - w / 2, x + w / 2]
edges.append(W / 2); y0 = -D / 2
for i in range(0, len(edges), 2):
    a, b = edges[i], edges[i + 1]
    if b - a > .01: box(S, ((a + b) / 2, y0, E / 2), (b - a, T, E))
for x, hs in front_cols:                                                   # stone between the openings of one column
    w = max(h[2] for h in hs); spans = sorted((h[1], h[1] + h[3]) for h in hs); z = 0.0
    for a, b in spans:
        if a - z > .01: box(S, (x, y0, (z + a) / 2), (w, T, a - z))
        z = b
    box(S, (x, y0, (z + E) / 2), (w, T, E - z))
wall_with_holes(D / 2, [(-2.0, 1.0, 1.0, 1.35), (2.4, 1.0, 1.0, 1.35)])                      # back
for x in (-W / 2, W / 2): box(S, (x, 0, E / 2), (T, D, E))                                    # gables (rectangular part)
for s in (-1, 1):                                                                             # gable triangles
    t = bmesh.new(); ridge = E + 3.0; prof = [(-D / 2, E), (D / 2, E), (0, ridge)]
    a = [t.verts.new((s * W / 2 - T / 2, y, z)) for y, z in prof]; b = [t.verts.new((s * W / 2 + T / 2, y, z)) for y, z in prof]
    t.faces.new(a); t.faces.new(list(reversed(b)))
    for i in range(3): t.faces.new((a[i], b[i], b[(i + 1) % 3], a[(i + 1) % 3]))
    bmesh.ops.recalc_face_normals(t, faces=t.faces)
    from _blender_kit import merge; merge(S, t)
box(S, (0, 0, .15), (W + .14, D + .14, .3))                                                   # plinth
Q = bm_for("quoin")                                                                           # corner quoins, alternating long/short
for sx in (-1, 1):
    for sy in (-1, 1):
        for k in range(int(E / .32)):
            z = .3 + k * .32 + .14; long = k % 2 == 0
            box(Q, (sx * (W / 2 - (.3 if long else .2)) , sy * (D / 2 + .02), z), (.6 if long else .4, T + .06, .28))
            box(Q, (sx * (W / 2 + .02), sy * (D / 2 - (.2 if long else .3)), z), (T + .06, .4 if long else .6, .28))
WD, WP, GL, IR = bm_for("wood"), bm_for("wood_paint"), bm_for("glass"), bm_for("iron")
def window(x, y, z, w, h, out):
    for dx in (-w / 2 + .04, w / 2 - .04): box(WD, (x + dx, y, z + h / 2), (.08, .12, h))         # jambs
    box(WD, (x, y, z + h - .04), (w, .12, .08)); box(Q, (x, y + out * .06, z - .05), (w + .2, .3, .08))   # head, stone sill
    box(Q, (x, y, z + h + .1), (w + .3, T + .04, .2))                                        # lintel
    box(GL, (x, y + out * .02, z + h / 2), (w - .1, .015, h - .1))
    box(WD, (x, y + out * .03, z + h / 2), (.035, .03, h - .1)); box(WD, (x, y + out * .03, z + h * .55), (w - .1, .03, .035))   # glazing bars
    for s in (-1, 1):                                                                          # open shutters against the wall: vertical planks + 2 battens
        sx = x + s * (w / 2 + w / 4 + .03)
        for k in range(4): box(WP, (sx - w / 4 + w / 8 * (k + .5), y + out * .3, z + h / 2), (w / 8 - .01, .03, h))
        for zz in (.2, .8): box(WP, (sx, y + out * .33, z + h * zz), (w / 2, .025, .1))
for (x, z, w, h) in FW: window(x, -D / 2 - T / 2, z, w, h, -1)
for (x, z, w, h) in [(-2.0, 1.0, 1.0, 1.35), (2.4, 1.0, 1.0, 1.35)]: window(x, D / 2 + T / 2, z, w, h, 1)
x, z, w, h = DOOR; y = -D / 2 - T / 2 + .1
for k in range(6): box(WP, (x - w / 2 + w / 6 * (k + .5), y, h / 2), (w / 6 - .008, .05, h))          # plank door
for zz in (.35, 1.8): box(IR, (x - .1, y - .04, zz), (w * .8, .015, .06)); cyl(IR, (x - w / 2 + .05, y - .02, zz), (0, 0, 1), .025, .12, seg=10)
box(Q, (x, -D / 2, h + .12), (w + .4, T + .04, .24)); box(Q, (x, -D / 2 - .35, .06), (w + .3, .5, .12))   # lintel, step
RF = bm_for("roof"); ridge = E + 3.0; slope = math.atan2(3.0, D / 2); run = math.hypot(3.0, D / 2) + .35
for s in (-1, 1):                                                                              # individual clay tiles, staggered rows
    n_rows = int(run / .19); n_cols = int((W + .6) / .26)
    for r in range(n_rows):
        d = .35 - r * .19; off = .13 if r % 2 else 0
        for c in range(n_cols):
            xx = -W / 2 - .3 + off + c * .26 + .13; yy = s * (D / 2 + .35 * math.cos(slope)) - s * (r * .19 + .1) * math.cos(slope)
            zz = E - .35 * math.sin(slope) + (r * .19 + .1) * math.sin(slope) + .05
            rot = Matrix.Rotation(-s * slope + R.uniform(-.03, .03), 3, "X") @ Matrix.Rotation(R.uniform(-.02, .02), 3, "Z")
            box(RF, (xx, yy, zz), (.24, .3, .025), rot=rot)
for c in range(int((W + .6) / .4)): cyl(RF, (-W / 2 - .3 + .2 + c * .4, 0, ridge + .08), (1, 0, 0), .11, .42, seg=10)   # ridge tiles
for sx in (-1, 1):                                                                              # chimneys on the gables
    box(S, (sx * (W / 2 - .45), 0, ridge + .5), (.7, .9, 2.0)); box(Q, (sx * (W / 2 - .45), 0, ridge + 1.55), (.85, 1.05, .12))
    for k in (-1, 1): cyl(RF, (sx * (W / 2 - .45), k * .2, ridge + 1.75), (0, 0, 1), .08, .3, seg=10)
for s in (-1, 1):
    box(WD, (0, s * (D / 2 + .3), E - .05), (W + .6, .04, .22))                                # eaves board
    t = bmesh.new()
    cyl(IR, (0, s * (D / 2 + .42), E - .12), (1, 0, 0), .07, W + .4, seg=12)                   # gutter
cyl(IR, (W / 2 - .1, -D / 2 - .42, E / 2), (0, 0, 1), .045, E, seg=10)                        # downpipe
finish(H, bevel_mats=("quoin", "wood_paint", "wood"), bevel=.012, smooth_mats=("iron",))
export(os.path.join(OUT, "normandy_farmhouse.glb"))

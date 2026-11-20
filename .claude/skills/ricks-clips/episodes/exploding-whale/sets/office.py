"""The highway department office, 1970 (shots 03-04): wood floor, painted walls, a slatted window that throws sun stripes, three desks,
a wall map, a blackboard. Open top (never in frame) so the sky fills the room softly; the sun comes low through the window wall.
    import office; Mo = office.build(scene, board=False)"""
import bpy, bmesh, math
from mathutils import Vector
import beach
from rc import look
col = beach.col

def _tex(name, ph, recolor, tile, fallback):
    try: return look.tex(name, ph, tile=tile, recolor=recolor, value=1.0, normal=1.0, spec=.25, macro=.1)
    except Exception as e:
        print("TEX FALLBACK", name, e); m = bpy.data.materials.new(name); m.use_nodes = True; m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*fallback, 1); return m

def _box(name, size, loc, m, c, bevel=.01):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts: v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
    if bevel: bmesh.ops.bevel(bm, geom=bm.edges[:], offset=bevel, segments=2, affect="EDGES")
    o = beach.mesh_obj(name, bm, m, c, smooth=False); o.location = loc; return o

def plain(name, rgb, rough=.6, emit=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough
    if emit: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = emit
    return m

DESKS = (-2.6, 0.0, 2.6)

def desk(c, x, y=.7, wood=None):
    top = _box("desk_top_%d" % round(x * 10), (1.7, .8, .06), (x, y, .76), wood, c); _box("desk_body_%d" % round(x * 10), (1.6, .7, .7), (x, y, .38), wood, c)
    _box("paper_%d" % round(x * 10), (.3, .22, .05), (x + .5, y - .1, .815), plain("paper", (.9, .88, .8), .8), c, bevel=.004)
    return top

def build(scene, board=False):
    c = col("L_SET"); Mo = beach.light(scene, "gold", az=-90, el=27); Mo.update(exposure=-.1, sat=1.06, contrast="Medium High Contrast")
    for o in list(bpy.data.objects):
        if o.name == "bounce_fill": bpy.data.objects.remove(o)
    floor = _tex("office_floor", "weathered_planks", "#8a5a34", 1.6, (.3, .18, .09)); wall = plain("office_wall", (.50, .62, .50), .85); trim = plain("office_trim", (.30, .20, .12), .5)
    wood = _tex("office_desk", "weathered_planks", "#6b3f22", .7, (.2, .1, .05))
    _box("floor", (12, 9, .1), (0, 0, -.05), floor, c, 0); _box("wall_back", (12, .15, 7.0), (0, 2.2, 3.5), wall, c, 0); _box("wall_right", (.15, 9, 7.0), (5.2, -2, 3.5), wall, c, 0)
    _box("picture_rail", (12, .05, .08), (0, 2.1, 2.55), trim, c, 0)
    _box("skirting", (12, .04, .14), (0, 2.11, .07), trim, c, 0)
    for i in range(9):                                                   # the window wall on the left: slats, the sun draws stripes across the room
        _box("slat_%d" % i, (.12, 9, .16), (-5.2, -2, .5 + i * .33), trim, c, 0)
    _box("wall_left_low", (.15, 9, .5), (-5.2, -2, .25), wall, c, 0)
    look.bounce_fill(c, at=(0, -4.5, 2.6), aim=(0, 1.5, 1.2), energy=260.0, size=5.0, name="office_fill")
    if board:
        _box("board_frame", (2.9, .06, 1.7), (0, 2.08, 1.55), trim, c); _box("board", (2.7, .04, 1.5), (0, 2.05, 1.55), plain("blackboard", (.035, .07, .05), .9), c, 0)
        _box("chalk_tray", (2.7, .1, .04), (0, 2.0, .78), trim, c)
    else:
        for x in DESKS: desk(c, x, wood=wood)
        _box("map_frame", (.05, 2.0, 1.4), (5.1, .6, 1.6), trim, c); _box("map_sea", (.04, 1.86, 1.26), (5.07, .6, 1.6), plain("map_sea", (.25, .5, .75), .7), c, 0)
        _box("map_land", (.04, 1.1, 1.26), (5.05, .98, 1.6), plain("map_land", (.78, .72, .5), .7), c, 0)
        _box("map_road", (.04, .06, 1.26), (5.03, .46, 1.6), plain("map_road", (.8, .05, .04), .5, .6), c, 0)        # the beach drawn as a red road
        for i, x in enumerate((-4.2, -1.3, 1.3, 4.0)):                       # filing cabinets with three drawers and handles
            _box("cabinet_%d" % i, (.9, .45, 1.3), (x, 1.9, .65), plain("cabinet", (.26, .36, .30), .4), c)
            for k in range(3): _box("drawer_%d_%d" % (i, k), (.8, .03, .36), (x, 1.665, .24 + k * .41), plain("cabinet_front", (.32, .44, .37), .35), c); _box("handle_%d_%d" % (i, k), (.22, .03, .03), (x, 1.64, .30 + k * .41), plain("steel", (.7, .7, .7), .25), c, .005)
    return Mo

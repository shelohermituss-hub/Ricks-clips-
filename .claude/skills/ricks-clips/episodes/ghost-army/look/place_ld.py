"""Ghost Army LookDev prototype (stage 9): one place, from the lock, through the look, to proof stills.
    blender -b --python place_ld.py -- <field|cafe|road> <out_dir> [samples]
Each step is logged as APPLIED / SKIPPED with its count, so the report says what really changed (a module in code is not a step done)."""
import bpy, sys, os, json, math, time, traceback
from mathutils import Vector
A = sys.argv[sys.argv.index("--") + 1:]; PLACE, OUT = A[0], A[1]; SAMPLES = int(A[2]) if len(A) > 2 else 128
SK, EP = os.environ["SKILL"], os.environ["EP"]; sys.path.insert(0, os.path.join(SK, "templates")); sys.path.insert(0, os.path.join(EP, "look"))
from blender_look import from_lock as FL
import ld
os.makedirs(OUT, exist_ok=True); LOG = []
def step(name, fn):
    t = time.time()
    try: r = fn(); LOG.append(dict(step=name, status="APPLIED", result=r, s=round(time.time() - t, 1))); print("STEP APPLIED", name, r)
    except Exception as e: LOG.append(dict(step=name, status="SKIPPED", error=repr(e)[:300])); print("STEP SKIPPED", name, repr(e)[:300]); traceback.print_exc()
PRESET = dict(field="morning", cafe="interior", road="night")[PLACE]
FRAMES = dict(field=[30, 150, 285], cafe=[1185, 1245, 1305], road=[800, 880, 960])[PLACE]
t0 = time.time(); K = FL.build(bpy.context.scene, EP, place=PLACE, preset=PRESET, samples=SAMPLES, res=37.5, motion_blur=False)
LOG.append(dict(step="from_lock.build", status="APPLIED", result=dict(set_objects=len(K["set"]), cards=len(K["cards"]), keep_clear=len(K["keep_clear"])), s=round(time.time() - t0, 1)))
KC = [(x, y, r) for x, y, r in K["keep_clear"]]
ld.cycles(SAMPLES)
def mats_with(word): return [m for m in bpy.data.materials if word in m.name.lower()]
def by_material(word, mat):
    n = 0
    for o in bpy.data.objects:
        if o.type != "MESH": continue
        for s in o.material_slots:
            if s.material and word in s.material.name.lower(): s.material = mat; n += 1
    return n
def tank_rubber():   # the Blender-modelled decoys (inflatable_tank GLB inside the set): rubberised canvas, olive, wrinkled
    m = ld.pbr("ld_rubber_canvas", "fabric_leather_02", tile=.6, tint=(.33, .38, .2), rough_mul=.8, bump=.6)
    return ld.assign(r"^(hull_bladder|turret_bladder|track_bladder|cupola_bladder|mantlet_cushion|gun_segments|wheel_cushions|hatch_cushion|patch_)", m)

def room_bounds():
    W = [o for o in ld.objects(r"^(wall_back|wall_left|wall_right|floor)")]; pts = [o.matrix_world @ Vector(c) for o in W for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))); hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts))); return lo, hi
def room_center(): lo, hi = room_bounds(); return (lo + hi) / 2
def room_size(k=1.0): lo, hi = room_bounds(); return tuple((hi - lo) * k)
def cafe_lights():
    lo, hi = room_bounds(); c = (lo + hi) / 2; n = 0
    win = ld.objects(r"^cafe_window")
    if win: w = win[0]; p = w.matrix_world.translation; ld.area("ld_window", p + (p - c).normalized() * .4 + Vector((0, 0, .3)), c - Vector((0, 0, .6)), 900, 1.6, (1, .95, .86)); ld.sun("ld_sun", (p - c).normalized() + Vector((0, 0, .8)), 2.5, (1, .9, .75), .02); n += 2
    for k in (-.25, .25): ld.point("ld_lamp_%d" % n, Vector((c.x + k * (hi.x - lo.x), c.y, hi.z - .35)), 120, (1, .7, .42), .12); n += 1
    ld.area("ld_fill", Vector((c.x, lo.y + .3, c.z)), c, 120, 3.0, (.85, .9, 1.0)); n += 1
    return n
def road_lamps():
    n = 0
    for o in ld.objects(r"^road_lamp_post"):
        top = o.matrix_world @ Vector((0, 0, max(c[2] for c in o.bound_box))); ld.point("ld_streetlamp_%d" % n, top + Vector((-.6, 0, -.1)), 260, (1, .72, .42), .1); n += 1
    ld.assign(r"^(road_lamp_post|road_lamp_arm|ht_lamp_post)", ld.simple("ld_iron", (.05, .05, .05), rough=.5, metal=.8)); return n


LEAVES = ld.foliage("ld_leaves", (.1, .2, .05)); GRASS = ld.foliage("ld_grass", (.16, .26, .07), .4); LEAVES_N = ld.foliage("ld_leaves_night", (.05, .09, .04), .3)
if PLACE == "field":
    step("hdri sky + light (kloofendal_misty_morning_puresky)", lambda: ld.world_hdri("kloofendal_misty_morning_puresky", strength=1.1, rot=2.2, visible=True) and "ok")
    step("low morning sun", lambda: ld.sun("ld_sun", (.82, -.5, .24), 3.2, (1, .86, .7), .03) and "ok")
    step("ground: leafy grass PBR + displacement", lambda: ld.assign(r"^ground$", ld.pbr("ld_ground", "leafy_grass", tile=2.5, disp=.06, tint=(.9, 1, .85))))
    step("dirt road: muddy tracks + displacement", lambda: ld.assign(r"^dirt_road$", ld.pbr("ld_dirt", "muddy_tracks", tile=4, disp=.12)))
    step("farm: stone walls, clay roof tiles, painted planks", lambda: ld.assign(r"^farm_walls", ld.pbr("ld_farmstone", "plaster_stone_wall_01", tile=2)) + ld.assign(r"^farm_roof", ld.pbr("ld_roof", "clay_roof_tiles", tile=2)) + ld.assign(r"^(farm_shutter|farm_door)", ld.pbr("ld_paintwood", "distressed_painted_planks", tile=1.2)))
    step("telegraph poles: weathered wood; insulators glass; wires", lambda: ld.assign(r"^(telegraph_pole|telegraph_bar|pennant_pole)", ld.pbr("ld_polewood", "brown_planks_07", tile=1.0, rough_mul=1.1)) + ld.assign(r"^pole_insulator", ld.simple("ld_insulator", (.55, .7, .62), rough=.08, transmission=.6)) + ld.assign(r"^power_line", ld.simple("ld_wire", (.02, .02, .02), rough=.4, metal=.6)))
    step("cargo truck: chipped olive paint, plank bed", lambda: ld.assign(r"^truck_(cab|hood|fender|side|bumper|tank)", ld.pbr("ld_truckpaint", "rusty_painted_metal", tile=1.2, tint=(.42, .45, .3), rough_mul=.9)) + ld.assign(r"^truck_(bed|board)", ld.pbr("ld_truckwood", "brown_planks_04", tile=1.0)))
    step("decoy tanks: rubberised canvas", tank_rubber)
    FG = ld.foliage_groups(); LOG.append(dict(step="foliage groups (instances imported as single objects)", status="APPLIED", result={k: len(v) for k, v in FG.items()}))
    step("hedges: real shrubs (shrub_02) in place of leaf clumps", lambda: ld.replace_objs(FG["hedge"], "shrub_02", fit="height"))
    step("copses and trees: leaf colour variation + bark", lambda: sum(1 for o in FG["copse"] for _ in [o.data.materials.clear(), o.data.materials.append(LEAVES)]) + ld.assign(r"^(tree|trunk|tree_trunk|poplar_trunk)", ld.pbr("ld_bark", "bark_brown_02", tile=.8)))
    step("meadow: modelled grass clumps near the lens (grass_medium_01, 1 in 2), colour variation for the rest", lambda: ld.replace_objs([o for o in FG["grass"] if o.matrix_world.translation.length < 26], "grass_medium_01", fit="height", every=2) + sum(1 for o in FG["grass"] if o.matrix_world.translation.length >= 26 for _ in [o.data.materials.clear(), o.data.materials.append(GRASS)]))
    step("dandelions and stones near the lens", lambda: ld.scatter(["dandelion_01", "stone_01"], 120, (-6, -6, 10, 12), KC, seed=4, scale=(.6, 1.1), near=(4, -2, 6)))
    step("morning air (volumetric haze)", lambda: ld.fog_box((0, 30, 8), (240, 240, 30), .0035, (.95, .88, .8)) and "ok")
elif PLACE == "cafe":
    step("lights: window sun + warm practicals + soft fill", lambda: cafe_lights())
    step("floor: worn tiles", lambda: ld.assign(r"^floor$", ld.pbr("ld_cafefloor", "floor_tiles_06", tile=1.2, rough_mul=.9)))
    step("walls: painted plaster", lambda: ld.assign(r"^(wall_back|wall_left|wall_right)", ld.pbr("ld_cafewall", "painted_plaster_wall", tile=2.2, tint=(1, .9, .72))))
    step("ceiling + beams: plaster, dark planks", lambda: ld.assign(r"^ceiling$", ld.pbr("ld_cafeceil", "damaged_plaster", tile=2)) + ld.assign(r"^ceiling_beam", ld.pbr("ld_beam", "dark_wooden_planks", tile=1.0)))
    step("wainscot, chair rail, shelves: dark varnished wood", lambda: ld.assign(r"^(wainscot|chair_rail|bar_shelf|skirting_board)", ld.pbr("ld_wains", "dark_wooden_planks", tile=.9, rough_mul=.7)))
    step("zinc bar top: brushed metal", lambda: ld.assign(r"^(bar_top|zinc_bar)", ld.pbr("ld_zinc", "metal_plate", tile=.8, rough_mul=.7)))
    step("bar mirror: real mirror", lambda: ld.assign(r"^bar_mirror", ld.simple("ld_mirror", (.9, .92, .95), rough=.03, metal=1.0)))
    step("bistro tables (round_wooden_table_01)", lambda: ld.replace(r"^cafe_table$", "round_wooden_table_01", fit="height") + ld.assign(r"^cafe_table_leg", None, hide=True))
    step("chairs (wooden_stool_02 / painted_wooden_chair_01)", lambda: ld.replace(r"^(cafe_chair_seat|spy_chair_seat|accordion_chair)", "painted_wooden_chair_01", fit="footprint") + ld.assign(r"^(chair_leg|spy_chair_leg|chair_back)", None, hide=True))
    step("bottles (wine_bottles_01)", lambda: ld.replace(r"^(shelf_bottle|bottle)$", "wine_bottles_01", fit="height"))
    step("cups and saucers: glazed china", lambda: ld.assign(r"^(coffee_cup|saucer)", ld.simple("ld_china", (.92, .9, .85), rough=.15)))
    step("window: glass + frame light", lambda: ld.assign(r"^cafe_window", ld.simple("ld_glass", (.9, .95, 1), rough=.02, transmission=1.0)))
    step("cigarette haze in the room (volumetric)", lambda: ld.fog_box(room_center(), room_size(.95), .02, (1, .93, .82), .4) and "ok")
elif PLACE == "road":
    step("night HDRI for light/reflections only (cobblestone_street_night)", lambda: ld.world_hdri("cobblestone_street_night", strength=.35, visible=False, bg=(.012, .02, .05)) and "ok")
    step("moon (cold key)", lambda: ld.sun("ld_moon", (-.3, .6, .5), .35, (.62, .72, 1.0), .01) and "ok")
    step("cobbles: real displacement, wet", lambda: ld.assign(r"^road$", ld.pbr("ld_cobble", "cobblestone_floor_04", tile=1.6, disp=.05, wet=.75)))
    step("verges: wet mud and grass", lambda: ld.assign(r"^ground$", ld.pbr("ld_verge", "brown_mud_leaves_01", tile=3, disp=.04, wet=.5)))
    step("puddles: dark mirror water", lambda: ld.assign(r"^puddle", ld.simple("ld_puddle", (.02, .025, .03), rough=.02)))
    FG = ld.foliage_groups(); LOG.append(dict(step="foliage groups (instances imported as single objects)", status="APPLIED", result={k: len(v) for k, v in FG.items()}))
    step("poplars: bark + dark wet leaves", lambda: ld.assign(r"^poplar_trunk", ld.pbr("ld_bark", "bark_willow", tile=.7, wet=.4)) + sum(1 for o in FG["hedge"] + FG["copse"] for _ in [o.data.materials.clear(), o.data.materials.append(LEAVES_N)]))
    step("verge grass: modelled wet grass near the lens (grass_medium_02, 1 in 3)", lambda: ld.replace_objs([o for o in FG["grass"] if abs(o.matrix_world.translation.x) < 12 and o.matrix_world.translation.y < 30], "grass_medium_02", fit="height", every=3))
    step("half-track: chipped olive paint, wet", lambda: ld.assign(r"^(sound_halftrack_paint|ht_speaker_(frame|cradle|driver)|ht_driver_cap|ht_horn_(rib|rim))", ld.pbr("ld_htpaint", "rusty_painted_metal", tile=1.0, tint=(.36, .4, .26), rough_mul=.8, wet=.3)) + ld.assign(r"^(ht_speaker_horn|ht_horn)", ld.simple("ld_horn", (.62, .64, .6), rough=.25, metal=1.0)))
    step("street lamps: iron + warm bulbs with halos", lambda: road_lamps())
    step("ghost tanks hidden (in the film they are faint sound ghosts, opacity ~0 at these frames)", lambda: ld.assign(r"^(hull_bladder|turret_bladder|track_bladder|cupola_bladder|mantlet_cushion|gun_segments|gun_bands|wheel_cushions|hatch_cushion|patch_|hull_seams|turret_seams|straps|d_rings|valve_|tank_star|tank_stencil)", None, hide=True))
    step("rainy night air (volumetric, lamp halos)", lambda: ld.fog_box((0, 30, 6), (60, 120, 14), .012, (.7, .78, 1.0), .5) and "ok")

json.dump(LOG, open(os.path.join(OUT, PLACE + "_steps.json"), "w"), indent=1)
T = ld.proofs(OUT, PLACE, FRAMES); ld.write_credits(OUT)
json.dump(dict(place=PLACE, frames=FRAMES, samples=SAMPLES, timings=T, steps=LOG), open(os.path.join(OUT, PLACE + "_report.json"), "w"), indent=1)
print("PLACE DONE", PLACE, json.dumps(T))

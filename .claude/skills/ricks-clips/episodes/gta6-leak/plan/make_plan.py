"""Writes plan.json for gta6-leak (the plan is data; this script keeps it readable and the voice timings exact)."""
import json, os
H = os.path.dirname(os.path.abspath(__file__)); V = os.path.join(H, "..", "voice")
LT = {d["line"]: (d["t0"], d["t1"]) for d in json.load(open(os.path.join(V, "line_times.json")))}
W = json.load(open(os.path.join(V, "words.json")))
F = lambda t: int(round(t * 30))
def cam(t, pos, aim, lens, move, framing="medium"): return {"t": round(t, 2), "pos": pos, "aim": aim, "lens": lens, "move": move, "framing": framing}
def act(id, who, t0, t1, what, anim, micro, reactions, consequences, sfx, recipe=None):
    a = {"id": id, "who": who, "f": [F(t0), F(t1)], "what": what, "anim": anim, "micro": micro, "reactions": reactions, "consequences": consequences, "sfx": sfx}
    if recipe: a["recipe"] = recipe
    return a
L = LT
P = {
"title": "He Leaked GTA 6 From A Hotel Room", "kind": "video", "style": "references/STYLE_BIBLE_FR.md", "format": "1080x1920", "fps": 30,
"duration_s": round(W[-1]["e"] + 0.6, 2),
"notes": "Narration EN, voix Fish 'rick' (voice/). Faits et sources: research/SOURCES.md. Aucune marque Rockstar/GTA dessinée: le jeu = écrans flous, boîte générique « 6 ». Droits: personnages de notre distribution.",
"voice": {"text": " ".join(w["w"] for w in W), "words": len(W), "file": "voice/voice.wav", "duration_s": round(W[-1]["e"], 2)},
"hook": {"action": "plug_in", "t": 0.3},
"captions": {"words": [1, 3], "style": "white bold rounded, thick black outline, centred at 70 % height, one change per word (words.json)"},
"loop": "last shot pushes into the switched-off cell TV, whose reflection matches the hotel TV of the first frame",
"facts": [
  {"fact": "18 — eighteen years old", "shot": "S02", "prop": "hotel key card sleeve with a birthday sticker '18' + bail tag on his ankle"},
  {"fact": "90 clips (over 90)", "shot": "S04", "prop": "upload counter on the laptop-TV screen climbing 0 -> 90 CLIPS UPLOADED"},
  {"fact": "$5 million — 5,000,000", "shot": "S05", "prop": "giant invoice printed on the studio printer: DAMAGE $5,000,000"},
  {"fact": "thousands of hours", "shot": "S05", "prop": "wall clock spinning + timesheet board '4,000 HRS'"},
  {"fact": "secure hospital, indefinite", "shot": "S06", "prop": "hospital door sign SECURE WARD + stamp INDEFINITE on the file"},
  {"fact": "90,421,491 views in 24 h — record", "shot": "S07", "prop": "dusk billboard counter 90,421,491 VIEWS + trophy plaque WORLD RECORD"},
  {"fact": "fit for trial — moved to prison", "shot": "S08", "prop": "doctor's stamp FIT FOR TRIAL on the file"},
  {"fact": "Nov 16 guilty plea, Nov 19 release, 3 days, GTA 6", "shot": "S09", "prop": "tear-off calendar NOV 16 -> NOV 19 + shop window poster with a big '6' (no logo)"}],
"needs": [
  {"id": "hotel_room", "kind": "set", "source": "script (sets/hotel.py): bed, bedside lamp, wall TV, curtains, carpet scan", "state": "to build"},
  {"id": "carpet", "kind": "texture", "source": "polyhaven:fabric_pattern_05 or ambientcg Carpet (to pick at download)", "state": "to download"},
  {"id": "wood_floor", "kind": "texture", "source": "polyhaven:wood_floor_deck / laminate_floor_02", "state": "to download"},
  {"id": "concrete_wall_008", "kind": "texture", "source": "polyhaven:concrete_wall_008", "state": "cached"},
  {"id": "night_city_hdri", "kind": "hdri", "source": "polyhaven (city night, CC0, to pick)", "state": "to download"},
  {"id": "tv_stick, phone, keyboard, remote", "kind": "props", "source": "script (small detailed props, rounded bevels)", "state": "to build"},
  {"id": "cast", "kind": "characters", "source": "cast: hacker, police, judge, doctor, programmer, gamer, nurse", "state": "drawn by tools/card_service.py"},
  {"id": "sounds", "kind": "sfx", "source": "templates/audio sfx_gen + rc.sound", "state": "to generate"}],
"places": [
 {"id": "hotel", "description": "budget hotel room at night: double bed with a crumpled duvet, bedside lamp, wall TV, half-drawn curtains with the city lights, room-service tray, ugly patterned carpet, 'DO NOT DISTURB' hanger",
  "ground": {"name": "carpet", "texture": "polyhaven:fabric_pattern_05", "tile": 1.2, "extra": "coffee stain, crisps crumbs near the bed"},
  "surfaces": [{"name": "walls", "texture": "polyhaven:beige_wall_001"}, {"name": "headboard", "texture": "polyhaven:fabric_leather_02"}],
  "sky": "city night through the window (lit windows, a few neon signs), HDRI for reflections only",
  "light": {"sun": {"elevation": -10, "azimuth": 0, "energy": 0.0, "angle": 1.5}, "fill": 0.08, "mood": "night: blue TV glow + warm bedside lamp",
            "practicals": ["TV screen emission 6 (blue-white, flickers with the screen content)", "bedside lamp 40 W warm 2700 K", "street neon through the curtains (magenta, slow pulse)"]},
  "shadows": "hard TV-light shadow of his head and hands on the duvet and wall; lamp shadow of the bed corner on the carpet; curtain slats stripe the wall",
  "props": [{"id": "tv_stick", "source": "script"}, {"id": "phone", "source": "script"}, {"id": "keyboard", "source": "script"}, {"id": "room_service_tray", "source": "script + polyhaven food props"},
            {"id": "do_not_disturb_hanger", "source": "script + text decal"}, {"id": "key_card_sleeve_18", "source": "script + text decal"}, {"id": "energy_drink_cans", "source": "script"}]},
 {"id": "corridor", "description": "hotel corridor outside his door: patterned carpet, door 214, police officer on a chair with a paper cup",
  "ground": {"name": "corridor carpet", "texture": "polyhaven:fabric_pattern_05", "tile": 1.2},
  "surfaces": [{"name": "walls", "texture": "polyhaven:beige_wall_001"}, {"name": "doors", "texture": "polyhaven:wood_table_001"}],
  "sky": "none (interior)", "light": {"sun": {"elevation": -10, "azimuth": 0, "energy": 0.0, "angle": 1.5}, "fill": 0.15, "mood": "night interior: warm sconces, light under his door flickering blue",
  "practicals": ["wall sconces warm", "blue TV flicker under the door"]},
  "shadows": "sconce pools on the carpet, the officer's long shadow across the door",
  "props": [{"id": "chair", "source": "polyhaven:woodenchair_01"}, {"id": "paper_cup", "source": "script"}, {"id": "door_214", "source": "script + decal"}, {"id": "fire_extinguisher", "source": "script"}, {"id": "ice_machine", "source": "script"}]},
 {"id": "city", "description": "the city at night seen from above: rooftops, streets of light; the 90 clips fly out of the hotel window like glowing cards and scatter over the city into thousands of phone screens lighting up",
  "ground": {"name": "streets", "texture": "polyhaven:asphalt_track", "tile": 3.0},
  "surfaces": [{"name": "rooftops", "texture": "polyhaven:concrete_wall_008"}],
  "sky": "deep night blue gradient, a few clouds lit from below", "light": {"sun": {"elevation": -8, "azimuth": 0, "energy": 0.0, "angle": 1.5}, "fill": 0.12, "mood": "night city: windows, street lamps"},
  "shadows": "little sun; the flying clips cast moving light pools on the roofs",
  "props": [{"id": "instanced_buildings", "source": "script (boxes with window textures, built for the frame)"}, {"id": "street_lamps", "source": "script"}, {"id": "billboards", "source": "script"}, {"id": "clip_cards", "source": "script (90 emissive cards)"}]},
 {"id": "studio", "description": "a game studio open office in panic: rows of desks, big monitors, coffee everywhere, red alarm light, printer spitting the damage invoice",
  "ground": {"name": "office floor", "texture": "polyhaven:laminate_floor_02", "tile": 2.0},
  "surfaces": [{"name": "walls", "texture": "polyhaven:beige_wall_001"}, {"name": "desks", "texture": "polyhaven:wood_table_001"}],
  "sky": "city morning through big windows", "light": {"sun": {"elevation": 25, "azimuth": 120, "energy": 4.5, "angle": 1.5}, "fill": 0.35, "mood": "cold morning + red alarm",
  "practicals": ["rotating red alarm light", "monitor glows", "fluorescent ceiling panels"]},
  "shadows": "window frames cast long bars across the desks; alarm sweeps red shadows",
  "props": [{"id": "desks_monitors", "source": "script"}, {"id": "printer", "source": "script"}, {"id": "invoice", "source": "script + decal"}, {"id": "wall_clock", "source": "script"}, {"id": "timesheet_board", "source": "script + decal"}, {"id": "coffee_cups", "source": "script"}]},
 {"id": "court_hospital", "description": "courtroom (wood panels, judge's bench, gavel) then the secure hospital corridor (white, glass, heavy door)",
  "ground": {"name": "court floor", "texture": "polyhaven:wood_floor_deck", "tile": 1.5},
  "surfaces": [{"name": "panels", "texture": "polyhaven:wood_table_001"}, {"name": "hospital floor", "texture": "polyhaven:concrete_floor_painted"}],
  "sky": "tall court windows, overcast", "light": {"sun": {"elevation": 35, "azimuth": 200, "energy": 3.5, "angle": 3}, "fill": 0.3, "mood": "warm court wood, then cold hospital white",
  "practicals": ["brass desk lamps in court", "cold strip lights in the hospital"]},
  "shadows": "window light shafts across the court; hospital: the closing door's shadow swallows him",
  "props": [{"id": "judge_bench", "source": "script"}, {"id": "gavel", "source": "script"}, {"id": "secure_door", "source": "script + decal SECURE WARD"}, {"id": "file_stamp_indefinite", "source": "script + decal"}]},
 {"id": "billboard", "description": "a huge digital billboard over a square at purple dusk, the view counter racing to 90,421,491, people stopping with their phones up",
  "ground": {"name": "square paving", "texture": "polyhaven:brick_pavement_03", "tile": 1.5},
  "surfaces": [{"name": "buildings", "texture": "polyhaven:concrete_wall_008"}],
  "sky": "purple to orange dusk gradient, pink clouds", "light": {"sun": {"elevation": 3, "azimuth": 250, "energy": 3.0, "angle": 2}, "fill": 0.35, "mood": "purple dusk + billboard glow"},
  "shadows": "long low-sun shadows of the crowd across the paving; the billboard throws coloured light on faces",
  "props": [{"id": "billboard_counter", "source": "script + animated text decal"}, {"id": "record_trophy", "source": "script"}, {"id": "crowd_phones", "source": "script (cards)"}, {"id": "street_furniture", "source": "script"}]},
 {"id": "doctor_prison", "description": "doctor's office (stamp FIT FOR TRIAL) then the prison van / cell",
  "ground": {"name": "office lino", "texture": "polyhaven:concrete_floor_painted", "tile": 1.5},
  "surfaces": [{"name": "prison walls", "texture": "polyhaven:concrete_wall_008"}],
  "sky": "none", "light": {"sun": {"elevation": 30, "azimuth": 160, "energy": 3.0, "angle": 1.5}, "fill": 0.3, "mood": "cold daylight office, grey prison"},
  "shadows": "window bar shadows on the cell floor; desk lamp pool on the file",
  "props": [{"id": "stamp", "source": "script"}, {"id": "patient_file", "source": "script + decal"}, {"id": "cell_bunk", "source": "script"}, {"id": "small_cell_tv", "source": "script"}]},
 {"id": "shop_street", "description": "a game shop street at night: the queue of gamers in hoodies with sleeping bags, neon, a shop window with a big '6' poster (no logo), a tear-off calendar in the shop",
  "ground": {"name": "pavement", "texture": "polyhaven:brick_pavement_03", "tile": 1.5},
  "surfaces": [{"name": "shopfront", "texture": "polyhaven:concrete_wall_008"}],
  "sky": "night, wet street reflections", "light": {"sun": {"elevation": -10, "azimuth": 0, "energy": 0.0, "angle": 1.5}, "fill": 0.12, "mood": "neon night (pink / cyan)",
  "practicals": ["shop window light", "neon sign", "phone screens in the queue"]},
  "shadows": "queue silhouettes against the bright window, long neon shadows on the wet pavement",
  "props": [{"id": "queue_gamers", "source": "cast cards"}, {"id": "poster_6", "source": "script + decal"}, {"id": "calendar", "source": "script + decal"}, {"id": "sleeping_bags", "source": "script"}, {"id": "puddles", "source": "script (wet decals)"}]}],
"objects": [
 {"id": "tv_stick", "source": "script", "material": "matte black plastic, tiny LED", "states": ["in the box", "plugged in (LED on)"]},
 {"id": "phone", "source": "script", "material": "glass + aluminium, screen emission", "states": ["dark", "lit hotspot screen"]},
 {"id": "keyboard", "source": "script", "material": "black plastic keys, backlight", "states": ["on the bed", "typing (keys press)"]},
 {"id": "hotel_tv", "source": "script", "material": "glossy black bezel, emissive screen", "states": ["off", "on: code / chat / upload bar"]},
 {"id": "clips", "source": "script (90 emissive cards)", "material": "emissive video frames (blurred generic game shots, no logo)", "states": ["on screen", "flying", "landed on phones"]},
 {"id": "invoice", "source": "script + decal", "material": "paper", "states": ["printing", "unrolled across the floor"]},
 {"id": "file", "source": "script + decal", "material": "paper folder", "states": ["blank", "stamped INDEFINITE", "stamped FIT FOR TRIAL"]},
 {"id": "counter", "source": "script (text decal swapped by frame range)", "material": "emissive LED", "states": ["0", "racing", "90,421,491"]},
 {"id": "calendar", "source": "script + decal", "material": "paper", "states": ["NOV 16", "pages torn", "NOV 19"]},
 {"id": "cell_tv", "source": "script", "material": "old plastic TV", "states": ["off (reflection)"]},
 {"id": "secure_door", "source": "script + decal SECURE WARD", "material": "painted steel, wired glass window", "states": ["open", "closed and locked"]},
 {"id": "cell_door", "source": "script", "material": "steel bars", "states": ["open", "slid shut"]}],
"characters": [
 {"id": "kid", "puppet": "cast:hacker", "costume": "hoodie, pyjama trousers, socks, ankle bail tag (3D prop)", "view": "34", "held": ["tv_stick", "phone", "keyboard"]},
 {"id": "cop", "puppet": "cast:police", "costume": "uniform, paper cup", "view": "34"},
 {"id": "judge", "puppet": "cast:judge", "costume": "robe, wig", "view": "front"},
 {"id": "doctor", "puppet": "cast:doctor", "costume": "white coat, clipboard", "view": "34"},
 {"id": "dev", "puppet": "cast:programmer", "costume": "studio hoodie (no logo), headset", "view": "34"},
 {"id": "gamer", "puppet": "cast:gamer", "costume": "hoodie, sleeping bag, phone", "view": "34"}],
"shots": [], "sound": {"music": "light, mischievous bed (pizzicato + synth bass), -7.6 dB under the voice, a drop on the twist (line 7) and a sting on the punchline", "lufs": -14},
"lessons_planned": ["PI-016"],
"warn_reasons": {"recipe vs plan wording": "the matcher compares the first words of each recipe line; the remaining 'maybe forgotten' lines were read one by one: either covered in other words (fall, gust, gesture, LED) or not relevant to this action (a TV that stays OFF does not light up; typing is not a door)",
  "no recipe for clips_fly / pigeon / trophy / neighbour": "new actions of this film: their recipes are written to library/reactions/reactions.json after they are built (rule: every new action becomes a recipe)"},
"risks": ["the game must never look like Rockstar's assets: generic blurred screens only", "the sentence on 23/11 may change the last line: re-check before publishing",
          "many interiors at night: watch noise at 12 samples -> denoise on, check key frames", "cards in small rooms: keep one view per character, anchors for held props (phone, keyboard, stick)"]}
S = []
def shot(id, place, line, t0, t1, narration, tin, tout, camera, actions, changes, fx, amb, shot_type="", mood=None):
    s = {"id": id, "place": place, "line": line, "t0": round(t0, 2), "t1": round(t1, 2), "narration": narration, "transition_in": tin, "transition_out": tout,
         "camera": camera, "actions": actions, "state_changes": changes, "fx": fx, "sound": {"ambience": amb}, "handheld": True, "shot_type": shot_type}
    if mood: s["mood"] = mood
    S.append(s)
a, b = L[1]
shot("S01", "hotel", 1, 0, b, "He leaked the biggest video game on Earth from a hotel room, using nothing but a TV stick and a phone.", "first frame (loop target)", "whip pan to the door",
     [cam(0, [0.6, -0.9, 0.55], "tv port", 24, "macro push on the stick going into the TV port", "insert"), cam(1.6, [0.2, -1.6, 1.0], "kid face lit by the TV", 35, "pull back and rise: his face lights up", "close"),
      cam(3.6, [-1.2, -2.6, 1.6], "room", 28, "crane back to the whole room: stick, phone, TV", "wide"), cam(b, [-1.4, -2.9, 1.7], "room", 28, "slow drift")],
     [act("plug_in", "kid", 0.3, 1.5, "plugs the TV stick into the hotel TV", "m:button/A (hand to the port), stick follows the hand (card_anchors)", ["fingers wiggle the stick in", "LED blinks"],
          ["his hand reaches the port and the stick follows the hand from contact (no teleport)", "the TV wakes: static then a blue boot screen", "the room goes from dark to TV-blue"],
          ["the stick stays plugged with its LED on for the whole film", "the empty stick box is left on the bed"], ["click", "TV power-on hum"], "object_pick_up"),
      act("grin", "kid", 1.6, 3.4, "his face lights up blue, sly grin", "m:idle/B k:smug", ["blink", "eyebrow wiggle"], ["the face changes ON the word 'leaked' with a head pop", "the body answers the face: he leans back on the pillows, shoulders up", "TV light flickers on his face"], ["the grin stays as he settles on the bed"], ["sly 'heh'"], "emotion_beat"),
      act("phone_hotspot", "phone", 3.6, b, "the phone on the bed lights up: hotspot on", "screen emission keyed", ["vibrates on the duvet"], ["the phone screen lights up with a flicker", "the duvet under it glows"], ["phone stays lit on the bed"], ["buzz"], "device_switch"),
      act("can_tip", "kid", 4.2, 5.2, "his elbow knocks an energy-drink can off the bedside table", "m:idle/B elbow + can rigid-body keys", ["can wobbles before falling"], ["can falls and rolls, fizz sprays"], ["can lies on the carpet, a wet fizz stain"], ["can clank", "fizz"], "object_fall_drop")],
     [{"who": "tv_stick", "change": "box -> plugged in", "by_action": "plug_in"}, {"who": "hotel_tv", "change": "off -> on", "by_action": "plug_in"}, {"who": "phone", "change": "dark -> lit", "by_action": "phone_hotspot"}],
     ["TV static burst", "dust motes in the TV beam"], "night room tone, distant traffic, TV hum", "insert", "night TV")
a, b = L[2]
shot("S02", "corridor", 2, a, b, "You see, he was 18, already on bail for hacking, and hiding in that hotel under police protection.", "whip pan through the door", "slide under the door back into the room",
     [cam(a, [0, -3.5, 1.4], "door 214 + cop", 32, "slow push down the corridor", "medium"), cam(a + 3, [0.5, -2.4, 1.2], "cop", 40, "dolly to the cop's face", "close"),
      cam(b, [0.2, -1.2, 0.25], "gap under the door", 30, "drop to the floor and slide toward the blue light under the door", "insert")],
     [act("cop_yawn", "cop", a + 0.2, a + 3.0, "the officer on guard yawns and sips coffee", "m:drink/A", ["eyes heavy, head nods"], ["the face changes ON the word 'protection' with a head pop", "the body answers the face: he slumps, shoulders drop", "coffee steams", "the chair creaks"], ["the emotion stays: he dozes off", "coffee ring stays on the floor by the chair"], ["yawn", "slurp"], "emotion_beat"),
      act("cup_spill", "cop", a + 2.2, a + 3.0, "as he nods off, the paper cup tilts and drips", "cup keyed tilt in the hand anchor", ["drips"], ["coffee stream with the right thickness, splash where it lands, spreading puddle"], ["puddle by the chair stays"], ["drip", "splat"], "liquid_pour_spill"),
      act("bail_tag", "kid", a + 3.2, b, "inside: the bail tag on his ankle blinks green as he types", "card idle + 3D tag prop on the ankle anchor", ["toes wiggle"], ["the tag LED lights up and blinks with each key"], ["tag stays on his ankle all film"], ["tag beep"], "device_switch")],
     [{"who": "cop", "change": "already in place when the camera arrives (in frame from the first frame of the shot)", "by_action": "cut"}],
     ["steam from the cup", "blue flicker under the door"], "corridor hum, ice machine", "medium", "night corridor")
a, b = L[3]
shot("S03", "hotel", 3, a, b, "So he plugged the stick into the TV, grabbed a keyboard, and slipped into Rockstar's private chat.", "slide under the door", "push into the TV screen",
     [cam(a, [0, -0.6, 2.4], "keyboard on duvet", 30, "top-down insert, slow rotate", "insert"), cam(a + 2.4, [0.7, -1.2, 1.1], "kid typing", 34, "orbit around him", "close"),
      cam(b, [0, -0.25, 1.05], "TV screen", 30, "push into the TV: the chat window fills the frame (POV)", "pov")],
     [act("grab_keyboard", "kid", a, a + 1.2, "grabs the keyboard from under a pizza box", "m:button/B, keyboard follows the hands from contact", ["pizza box slides off"], ["his hands reach the keyboard and it follows the hands from contact (no teleport)", "crumbs fall off the keys"], ["pizza box open on the floor, the place where the keyboard was is empty with crumbs"], ["cardboard slide", "plastic clack"], "object_pick_up"),
      act("type", "kid", a + 1.2, b, "types fast, the chat window opens on the TV", "m:write/A fast", ["fingers blur", "tongue out"], ["keys light under his fingers", "lines of code scroll on the TV"], ["the chat window stays open on the TV"], ["keyboard rattle", "chat ping"]),
      act("access", "hotel_tv", a + 3.4, b, "the TV flashes ACCESS GRANTED in green, his grin widens", "screen decal swap", ["screen glitch"], ["the screen lights up green on his face with a flicker"], ["the chat stays open"], ["access chime"], "device_switch")],
     [{"who": "keyboard", "change": "bed -> his hands", "by_action": "grab_keyboard"}],
     ["code light scrolling on his face"], "keyboard clatter, TV hum", "insert", "night TV")
a, b = L[4]
shot("S04", "city", 4, a, b, "Then he dropped over 90 clips of the secret game for the whole internet to see.", "through the TV screen and out of the window", "clips rain down -> match cut to the studio window",
     [cam(a, [0, 0, 22], "hotel window", 40, "fly out of the window with the first clip", "aerial"), cam(a + 2, [6, -10, 30], "clips swarm", 35, "rise above the city as the swarm spreads", "aerial"),
      cam(b, [12, -18, 18], "phones lighting up", 32, "dive toward the streets", "aerial")],
     [act("upload", "kid", a, a + 1.0, "hits ENTER: the upload counter climbs to 90", "m:button/A + counter decal swap", ["finger slam"], ["the number changes on every beat 0 -> 30 -> 60 -> 90 CLIPS UPLOADED, flashes at 90", "the clips peel off the screen"], ["the final number stays on screen: 90 on the TV"], ["enter clack", "whoosh"], "countdown_display"),
      act("clips_fly", "clips", a + 0.6, b, "90 glowing clips fly out of the window over the city and land on thousands of phones", "instanced cards on seeded curves", ["each clip flutters"], ["clips burst out and flutter down, spinning, catching the light", "windows and phones light up block by block"], ["the city stays dotted with lit screens", "a few clips stuck on antennas and chimneys"], ["swarm whoosh", "notification pings"]),
      act("pigeon", "clips", a + 2.0, a + 3.0, "a pigeon on a rooftop ducks as a clip whooshes past, feathers fly", "pigeon card keyed duck", ["head bob"], ["feathers puff"], ["one feather drifts down"], ["coo", "flap"]),
      act("phones_light", "clips", a + 3.0, b, "a gamer in his bedroom jumps when his phone lights up with the clip", "m:react/confused + phone emission", ["eyes widen"], ["his phone screen lights up with a flicker on his face"], ["phone stays lit"], ["ping", "gasp"], "device_switch")],
     [{"who": "clips", "change": "screen -> sky -> phones", "by_action": "clips_fly"}],
     ["glowing clip swarm", "window lights popping on"], "city night wind, pings", "aerial", "night city")
a, b = L[5]
shot("S05", "studio", 5, a, b, "Rockstar says the leak cost them $5 million and thousands of hours of work.", "match cut: phone screens -> studio monitors", "invoice slides into the courtroom",
     [cam(a, [-3, -6, 2.2], "office", 30, "fast dolly down the aisle as people run", "wide"), cam(a + 2.2, [0.3, -1.1, 1.0], "printer", 28, "rack to the printer spitting the invoice", "insert"),
      cam(b, [0.3, -0.7, 1.6], "invoice $5,000,000", 30, "tilt down the unrolling invoice", "insert")],
     [act("panic", "dev", a, a + 2.0, "developers jump up, headsets fly, coffee spills", "m:react/fury and m:run/A for extras", ["headset cable snaps back"], ["coffee stream with the right thickness pours off the desk, splash where it lands, spreading puddle", "red alarm starts spinning"], ["coffee puddle on the floor, chairs left spinning"], ["alarm", "gasps"], "liquid_pour_spill"),
      act("invoice", "invoice", a + 2.2, b, "the printer prints a 3-metre invoice DAMAGE $5,000,000", "paper mesh unrolling (keyed)", ["paper curls at the end"], ["paper feeds out line by line, curls and unrolls over the edge onto the floor", "the clock hands spin fast"], ["the long invoice lies across the floor"], ["printer screech", "paper rustle"], "paper_print_unroll"),
      act("phones_ring", "dev", a + 0.8, a + 2.2, "every desk phone in the office lights up and rings at once", "phone emissions keyed in a wave down the aisle", ["handsets rattle in their cradles"], ["the phone screens light up with a flicker one after another down the aisle"], ["the lights stay blinking"], ["phones ringing", "chatter"], "device_switch"),
      act("faint", "dev", a + 3.4, b, "a developer reads the total and faints back into his chair", "m:fall/A into the chair", ["legs kick up"], ["chair rolls back into a desk, a mug wobbles"], ["he stays slumped, chair against the desk"], ["thud", "chair roll"], "character_hit_fall")],
     [{"who": "invoice", "change": "printer -> floor", "by_action": "invoice"}],
     ["red alarm sweep", "papers flying"], "office alarm, phones ringing", "insert", "cold morning")
a, b = L[6]
shot("S06", "court_hospital", 6, a, b, "But the court said he wasn't fit to stand trial, so instead of prison, he was locked in a secure hospital, maybe for life.", "invoice slide", "door slam to black, then light (whip)",
     [cam(a, [0, -5, 1.8], "judge", 35, "slow push to the bench", "medium"), cam(a + 2.4, [0.2, -0.8, 1.2], "gavel + file", 30, "insert on the gavel hit and the stamp", "insert"),
      cam(a + 3.6, [0, -4, 1.4], "secure door", 32, "slow track down the white corridor", "wide"), cam(b, [0, -1.6, 1.4], "door window with his face", 40, "push in as the door closes", "close")],
     [act("gavel", "judge", a + 2.4, a + 3.0, "the judge brings the gavel down", "m:hammer/A", ["wig bounces"], ["anticipation lift then a hard hit: papers jump on the bench", "camera kick on the hit"], ["file stamped INDEFINITE, a dent in the sound block"], ["gavel bang"], "strike_stamp"),
      act("door_close", "secure_door", a + 4.0, b, "the heavy secure door swings shut, he looks out through the small window", "hinge keys with overshoot", ["lock bolt slides"], ["the door swings on its hinge (ease out, small overshoot)", "the light from the corridor narrows on his face, dust swirls"], ["the door stays shut and locked, his face behind the glass"], ["heavy door", "lock clunk"], "door_open_close"),
      act("wave", "kid", a + 5.2, b, "behind the glass he gives a tiny awkward wave", "m:wave/A small", ["fingers only"], ["his breath fogs the glass"], ["a fog patch stays on the window"], ["squeak on glass"], "gesture")],
     [{"who": "kid", "change": "court -> behind the hospital door", "by_action": "door_close"}],
     ["dust in the window shafts"], "court murmur, hospital hum", "close", "warm court -> cold hospital")
a, b = L[7]
shot("S07", "billboard", 7, a, b, "And the leak didn't kill the game. A year later, the real trailer became the most watched non-music video on YouTube in a single day.", "whip from the door window", "counter blur -> doctor's office",
     [cam(a, [0, -14, 1.6], "billboard", 35, "low crane up the crowd to the billboard", "wide"), cam(a + 3.2, [0, -4, 4], "counter digits", 40, "push into the racing digits", "insert"),
      cam(b, [2, -6, 2], "crowd faces + trophy", 32, "orbit the crowd as the record trophy rises", "medium")],
     [act("counter", "counter", a + 1.0, a + 5.5, "the view counter races to 90,421,491", "decal swap per frame range (the display is the action)", ["digits blur"], ["the number changes on every beat and flashes at 90,421,491", "the crowd raises phones", "confetti cannons fire on the record"], ["the final number stays on screen: 90,421,491 + WORLD RECORD plaque"], ["digit ticking", "crowd cheer"], "countdown_display"),
      act("cheer", "gamer", a + 5.5, b, "the crowd cheers, phones up, confetti", "m:cheer/A with offsets", ["random timing per person"], ["fans stand up, arms up, flags wave, confetti"], ["confetti stays on the ground"], ["cheer", "confetti pop"], "crowd_reaction"),
      act("trophy", "counter", a + 6.0, b, "a giant record trophy rises from the billboard base", "trophy keyed rise with a bounce", ["sparkle glints"], ["spotlights swing onto it"], ["the trophy stays lit"], ["fanfare"])],
     [{"who": "counter", "change": "0 -> 90,421,491", "by_action": "counter"}],
     ["confetti", "billboard light on faces"], "square crowd, dusk city", "insert", "purple dusk")
a, b = L[8]
shot("S08", "doctor_prison", 8, a, b, "Then this year, doctors decided he was fit for trial after all, and he was moved back to prison.", "counter blur", "cell door slam",
     [cam(a, [0, -1.0, 1.5], "file on desk", 30, "top-down on the file, the stamp comes in", "insert"), cam(a + 1.8, [0.2, -1.0, 1.25], "kid face", 45, "snap push to his shocked face", "extreme_close"),
      cam(b, [0, -3.5, 1.4], "cell door", 32, "pull back as the cell door slides shut", "medium")],
     [act("stamp", "doctor", a + 0.3, a + 1.5, "the doctor stamps FIT FOR TRIAL", "m:hammer/B", ["glasses slide down"], ["anticipation lift then a hard hit: ink splat, pen jumps"], ["the file stays stamped FIT FOR TRIAL, ink mark"], ["stamp thump"], "strike_stamp"),
      act("shock", "kid", a + 1.8, a + 3.2, "his eyes pop out, sweat drop", "m:idle/B k:shocked", ["tremble"], ["the face changes on 'fit' to an exaggerated drawing (eyes pop) with a head pop", "a world effect answers: the lamp flickers, papers fly off the desk"], ["the effect fades but marks stay: papers on the floor, sweat drop until the end of the shot"], ["sting"], "extreme_emotion"),
      act("cell", "kid", a + 3.4, b, "the cell door slides shut on him", "door keys", ["bars rattle"], ["the barred door slides on its rail (ease out, small overshoot)", "light changes through the bars, bar shadows sweep across him, dust swirl"], ["the door stays shut, he is inside the cell"], ["metal slam"], "door_open_close")],
     [{"who": "kid", "change": "hospital -> cell", "by_action": "cell"}],
     ["sweat drop", "bar shadows"], "office tick, prison echo", "extreme_close", "grey prison")
a, b = L[9]
shot("S09", "shop_street", 9, a, b, "And just three days before GTA 6 finally came out, he pleaded guilty.", "cell door slam -> calendar flip", "the queue's phones -> the cell",
     [cam(a, [0, -0.6, 1.5], "calendar", 32, "insert on the calendar pages tearing NOV 16 -> NOV 19", "insert"), cam(a + 1.6, [-4, -8, 1.2], "queue + shop window '6'", 30, "low tracking along the queue in the rain", "wide"),
      cam(b, [0, -2, 1.4], "gamer's phone: headline", 40, "push into a phone showing the headline 'PLEADS GUILTY'", "insert")],
     [act("calendar", "calendar", a, a + 1.6, "calendar pages tear off from NOV 16 to NOV 19", "page meshes peel off (keyed)", ["pages flutter"], ["the number changes on each tear 16 -> 17 -> 18 -> 19 and the page flashes", "torn pages drift down"], ["the final number stays on screen: NOV 19", "pages stay on the floor"], ["paper rips"], "countdown_display"),
      act("umbrella", "gamer", a + 3.0, a + 4.0, "a gust flips a gamer's umbrella inside out", "umbrella keyed flip", ["he clings to it"], ["rain sprays on the queue"], ["the broken umbrella stays inside out"], ["whoosh", "snap"], "wind_gust"),
      act("queue", "gamer", a + 1.6, b, "gamers queue in the rain for the game; one reads the guilty plea headline on his phone", "m:wait/A, m:phone/A", ["breath steam", "shiver"], ["rain splashes on hoods", "puddles ripple"], ["wet hoodies, puddles"], ["rain", "chatter"], "rain")],
     [{"who": "calendar", "change": "NOV 16 -> NOV 19", "by_action": "calendar"}],
     ["rain", "neon reflections"], "rain, street", "insert", "neon night")
a, b = L[10]; b = P["duration_s"]
shot("S10", "doctor_prison", 10, a, b, "So the guy who showed the world GTA 6 first will probably be the last one to play it.", "the queue's phones -> the cell", "loop: the switched-off cell TV -> the hotel TV of frame 1",
     [cam(a, [0, -3.2, 1.3], "kid on the bunk", 32, "slow push in", "medium"), cam(a + 3.0, [0.1, -1.2, 1.15], "the small TV, off", 35, "push into the black screen: his reflection", "close"),
      cam(b, [0.05, -0.5, 1.1], "black screen", 30, "the reflection becomes the hotel TV of frame 1 (loop)", "extreme_close")],
     [act("sigh", "kid", a, a + 3.0, "sits on the bunk, sighs at the dead little TV", "m:react/sigh", ["shoulders drop"], ["the face changes ON the word 'last' with a head pop", "the body answers the face: he slumps, shoulders down", "dust lifts from the mattress"], ["the emotion stays: he stays slumped"], ["sigh", "springs creak"], "emotion_beat"),
      act("tv_dead", "cell_tv", a + 3.0, b, "he presses the TV button: nothing, just his reflection", "m:button/A + TV stays off", ["button clicks twice"], ["the button dips under the finger, a tiny spark, then nothing"], ["the device stays stubbornly off: the TV stays black with his reflection"], ["click click", "tiny fizz"], "device_switch"),
      act("neighbour", "gamer", a + 1.5, a + 3.0, "from the next cell, game sounds and a cheer: someone else is already playing", "off-screen sound + light flicker on the wall", ["light flickers"], ["coloured TV light from the next cell dances on his wall"], ["the light keeps flickering"], ["game music muffled", "cheer"])],
     [{"who": "kid", "change": "already in the cell (S08 cell action)", "by_action": "cell"}],
     ["dust motes", "reflection"], "prison echo, distant TV from another cell (game sounds)", "close", "grey prison")
P["shots"] = S
json.dump(P, open(os.path.join(H, "plan.json"), "w"), indent=1, ensure_ascii=False)
print("plan.json", len(S), "shots, duration", P["duration_s"])

"""Writes episodes/ghost-army/film.json (rough board v1). Positions are plan metres per place (each place has its own origin).
Every character carries "place" so it shows only in its own place (film_plan.py passes it to film.js)."""
import json, os, re
EP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = json.load(open(os.path.join(EP, 'voice', 'words.json')))
k = lambda w: re.sub(r"^[ .,?!\"';:-]+|[ .,?!\"';:-]+$", "", w).lower()
def fr(word, n=1): return round([x for x in W if k(x['w']) == word][n - 1]['s'] * 30)
END = round((W[-1]['e'] + 0.9) * 30)
def St(at, pos, aim, lens=None, subj='lou', framing='W', **o):
    # whole-body rests (W): a longer lens and the aim lifted, so the figure fills about 0.4 of the frame and the feet sit low (CB: figure 0.45, feet 0.8-0.95)
    if framing == 'W' and lens is None: lens = W_LENS; aim = [aim[0], aim[1], aim[2] + W_LIFT]
    return dict(at=at, pos=pos, aim=aim, lens=lens or 24, subject=subj, framing=framing, **o)
W_LENS, W_LIFT = 40, 0.35
C = dict(dof=0.35)   # close-ups only: a mild soft background (CB_RULES: wides and mediums fully sharp)
takes = [
 dict(id='t_hook', place='field', stations=[
   St(0, [5.0, -3.6, 0.9], [0.0, 4.0, 2.0], lens=24, shows=['tank'], hold=0.0),
   St(['suitcase', 1], [5.2, -2.6, 1.6], [1.6, 1.6, 1.5], lens=30, framing='M', lead=3, hold=0.3, travel=1.6),
   St(['bicycles', 1], [-2.2, -6.6, 1.3], [-7.2, -3.6, 1.0], subj='farmer', lead=3, hold=0.3, travel=1.0),
   St(['winks', 1], [4.2, -1.8, 1.45], [3.2, 0.5, 1.4], lens=35, framing='C', lead=3, hold=0.4, travel=1.0, **C),
   # V3 step 7: macro insert on the brass valve while the decoy sighs down (valve_air_whistle on 'rubber'); plan = the valve on the rear deck
   St(['rubber', 1], [-2.75, 4.05, 2.85], [-1.96, 5.19, 2.12], lens=50, framing='O', lead=3, travel=0.9, **C)], join_out='push'),
 dict(id='t_camp', place='camp', join_in='push', join_in_frames=3, stations=[
   St(['painters', 1], [-7.6, -7.4, 3.2], [-2.0, 6.0, 1.0], framing='P', lead=9, hold=0.3),
   St(['job', 1], [2.8, -4.4, 1.5], [1.0, -1.4, 1.3], framing='M', lead=3, hold=0.3, travel=1.4),
   St(['rule', 1], [-0.6, -2.2, 1.3], [-2.2, 2.4, 1.1], lead=3, hold=0.2, travel=1.2),
   St(['close', 1], [-5.6, 8.6, 1.5], [-4.0, 12.0, 1.4], framing='O', subj='carrier_short', lead=3, travel=0.8, **C),
   St(['army', 2], [-6.0, -30.0, 12.0], [-4.0, 14.0, 0.5], framing='P', lead=3, hold=0.2, travel=1.4, drift=[0.12, 0.08, 0.0]),
   St(['bulldozer', 1], [19.5, -12.0, 3.0], [12.0, -3.5, 0.8], framing='P', lead=3, travel=1.4)]),
 dict(id='t_road', place='road', join_out='push', stations=[
   St(['night', 1], [-1.2, -2.4, 1.4], [1.4, 4.2, 1.5], subj='sound_op', lead=4, hold=0.3),
   St(['hundred', 1], [-7.0, -9.0, 2.4], [-5.0, 22.0, 2.0], subj='sound_op', framing='P', lead=6, hold=0.3, travel=0.8, drift=[0.12, 0.08, 0.0]),
   St(['speaker', 1], [3.0, 3.6, 3.3], [0.0, 7.2, 2.7], subj='sound_op', framing='O', lead=3, travel=1.0, **C)]),
 dict(id='t_radio', place='radio', join_in='push', join_in_frames=3, join_out='push', stations=[
   St(['radio', 1], [1.8, -1.6, 1.7], [-0.2, 1.2, 1.1], subj='radio_op', framing='M', lead=9, hold=0.3),
   St(['morse', 1], [-2.0, -1.2, 1.7], [-0.3, 0.85, 1.15], subj='radio_op', framing='O', lead=3, travel=0.9, **C)]),
 dict(id='t_cafe', place='cafe', join_in='push', join_in_frames=3, stations=[
   St(['café', 1], [-1.2, -1.6, 1.7], [1.2, 3.8, 1.3], lead=9, hold=0.3),
   St(['patches', 1], [0.6, 1.6, 1.5], [1.4, 3.6, 1.2], framing='M', lead=3, hold=0.2, travel=0.9),
   St(['spies', 1], [-1.0, -0.2, 1.4], [-2.6, 1.6, 1.1], subj='spy', framing='M', lead=3, hold=0.2, travel=0.9),
   ]),
 # v1 note 3: the travel from the spy to the sergeant swept past Lou, cut by the right edge, and the sergeant arrived late. Now a cut lands on him on "sergeant".
 dict(id='t_sergeant', place='cafe', stations=[
   St(['sergeant', 1], [3.2, 0.9, 1.6], [4.0, 3.4, 1.4], subj='sergeant', framing='C', lens=30, lead=2, **C)]),
 dict(id='t_river', place='river', join_out='push', stations=[
   St(['river', 1], [-22.6, -0.4, 1.6], [-19.6, 4.6, 1.2], lead=4, hold=0.3),
   St(['hundred', 2], [-36.0, 6.0, 5.0], [-25.0, 28.0, 0.5], framing='P', lead=3, travel=1.6)]),
 dict(id='t_photo', place='photo', join_in='push', join_in_frames=3, stations=[
   # V3 step 7: open on the aerial photographs under the loupe (macro), then pull to the interpreter on 'spies'
   St(['photographs', 1], [0.75, 0.95, 1.75], [0.05, 1.6, 0.93], lens=45, subj='interpreter', framing='O', lead=9, hold=0.3),
   St(['spies', 2], [1.9, -1.3, 1.6], [-0.1, 1.0, 1.1], subj='interpreter', framing='M', lead=3, travel=0.8)]),
 dict(id='t_strike', place='river', stations=[
   St(['gun', 1], [-34.0, 10.0, 4.0], [-26.0, 26.0, 1.0], framing='P', lead=6, hold=0.15),
   # THE SIGNATURE (story bible): one crane from the shelled decoy field, rising and swinging north to the silent crossing
   St(['crosses', 1], [48.0, 22.0, 7.0], [60.0, 44.0, 0.5], subj='sergeant', framing='P', lead=3, hold=0.2, travel=3.2, via=[[-14.0, 4.0, 22.0], [24.0, 6.0, 20.0]]),
   St(['fired', 1], [55.2, 40.4, 1.3], [57.0, 44.0, 1.5], subj='sergeant', framing='C', lead=3, travel=0.9, **C)]),
 dict(id='t_bed', place='bedroom', stations=[
   St(['pillow-under-the-blanket', 1], [0.8, -1.0, 1.5], [-0.4, 2.2, 0.9], subj='boy', lead=4, hold=0.3),
   St(['outside', 1], [0.2, -0.2, 1.3], [1.3, 3.2, 1.0], subj='boy', framing='M', lead=3, travel=1.0)]),
 dict(id='t_attic', place='attic', stations=[
   St(['fooled', 1], [0.0, -2.8, 1.5], [-0.2, 1.8, 1.0], lens=30, subj='old_lou', lead=4, hold=0.3),
   St(['families', 1], [-0.4, -0.8, 1.3], [-1.0, 1.3, 1.3], subj='old_lou', framing='M', lead=3, hold=0.3, travel=1.0),
   St(['years', 1], [-0.1, -2.7, 1.25], [-0.1, 1.5, 1.2], subj='grandchild', framing='M', lead=3, travel=1.0)])]
A = []
def act(who, at, **o):
    if 'place' in o and 'pos' in o and 'move_s' not in o: o['move_s'] = 0.01   # animation audit: entering a new place is a cut, never a slide from the old place's coordinates
    A.append(dict(who=who, at=at, **o))
# ANIMATION AUDIT 2026-11-17: every act is a registered motion-library move (m:<id>), every change of place a visible walk/run at a
# believable speed (WALK m/s ~1.1, run ~3-4), no static kit pose, no planner 2-frame walk, no glide. Reasons per beat in audit/ANIMATION_AUDIT.md.
WALK = 1.1
def go(who, at, to, frm, speed=WALK, pose='m:walk/A', then=None, **o):
    """a visible walk/run: the move plays its legs while the position travels at `speed` m/s; `then` = the move on arrival"""
    import math as _m; d = _m.dist(frm[:2], to[:2]); s_ = round(max(.3, d / speed), 2)
    act(who, at, pos=to, move_s=s_, linear=True, pose=pose, **o)
    f0 = at if isinstance(at, int) else fr(at[0], at[1]) + (at[2] if len(at) > 2 else 0)
    if then: act(who, f0 + int(s_ * 30) + 1, pose=then)
    return s_
# --- field (hook): the four lift the tank (it stays above them and comes down), step out, Lou pats it, the cyclists roll in
# all four hold the hull by its long sides (measured footprint: none stands inside it, so nobody has to step out from under it)
for who, pos, d in (('lou', [0.99, 1.45, 0], -1), ('carrier_tall', [-1.4, 2.2, 0], 1), ('carrier_short', [1.4, 5.8, 0], -1), ('carrier_stocky', [-1.06, 6.36, 0], 1)):
    act(who, 0, pos=pos, place='field', view='34', dir=d, pose='m:lift/A', face='k:concentrate')     # bored hold under the load
    act(who, 52, pose='m:lift/B')                                                                       # the set-down (tank lowers f52-103)
act('carrier_tall', 112, pose='m:idle/C', face='k:sleepy')
for who, frm, to in (('carrier_short', [1.4, 5.8, 0], [6.5, 9.5, 0]), ('carrier_stocky', [-1.06, 6.36, 0], [-6.5, 11.5, 0])):
    go(who, 112, to, frm, pose='m:walk/C', face='k:sleepy', then='m:idle/C')                           # bored, they wander off behind the tank
act('lou', 100, pose='m:lift/C', face='k:smirk')                                                        # pats it like luggage on 'suitcase' (f103), where he stands
go('lou', 150, [3.0, 1.3, 0], [0.99, 1.45, 0], speed=1.4, pose='m:walk/B', view='front', then='m:idle/A')   # strolls round to the front; arrives before 'winks'
act('lou', ['winks', 1], face='k:slyWink', pose='m:cheer/A')   # "very strong": both fists up beside the head (the close-up crops anything lower)
go('lou', ['see', 1], [-1.8, 2.15, 0], [3.0, 1.3, 0], speed=4.2, pose='m:run/C', view='side', dir=-1, then='m:push/B', face='k:proud')   # sprints to the valve, one smug push
act('farmer', 0, pos=[-7.8, -12.0, 0], place='field', view='side', dir=1, pose='m:bike/A+props', face='k:standard')
act('boy', 0, pos=[-6.7, -13.0, 0], place='field', view='side', dir=1, pose='m:bike/B+props', face='k:happy')
act('farmer', ['bicycles', 1, -60], pos=[-7.8, -2.6, 0], move_s=2.0, linear=True); act('boy', ['bicycles', 1, -60], pos=[-6.7, -4.6, 0], move_s=2.0, linear=True)   # ~4.5 m/s, a real cycling speed
act('farmer', ['dead', 1], pose='m:bike/C+props', face='k:shocked', pos=[-7.8, -2.0, 0], move_s=1.4); act('boy', ['dead', 1], pose='m:bike/C+props', face='k:surprised', pos=[-6.7, -4.0, 0], move_s=1.4)   # brake: lazy pedals, rolling to a stop
act('boy', ['strong', 1], face='k:excited')
# --- camp
act('lou', ['painters', 1, -2], pos=[1.0, -1.4, 0], place='camp', view='34', dir=-1, pose='m:write/A', face='k:happy')
act('carrier_short', ['painters', 1, -2], pos=[-4.6, 9.4, 0], place='camp', visible=True, view='34', dir=1, pose='m:sweep/A', face='k:concentrate')
go('carrier_short', ['close', 1, -40], [-7.6, 9.6, 0], [-4.6, 9.4, 0], pose='m:walk/C', then='m:sweep/B')   # walks off the lens before the 'up close' insert
act('carrier_tall', ['painters', 1, -2], pos=[-2.6, 1.7, 0], place='camp', view='side', dir=1, pose='m:push/A', face='k:concentrate')
act('lou', ['job', 1], face='k:smug', view='front'); act('lou', ['nobody', 1], face='k:wink')
go('lou', ['rule', 1], [-2.0, 2.0, 0], [1.0, -1.4, 0], pose='m:walk/B', face='k:proud', then='m:board/A')   # strolls to the line he will point at
act('lou', ['army', 2], face='k:cheer', pose='m:cheer/A')
# --- road (night)
act('sound_op', ['night', 1, -4], pos=[2.0, 3.4, 0], place='road', view='34', dir=-1, pose='m:idle/A', face='k:concentrate')
act('sound_op', ['hundred', 1, -6], pose='m:button/A', face='k:smug'); act('sound_op', ['speaker', 1], face='k:proud')
# --- radio tent
act('radio_op', ['radio', 1, -4], pos=[-0.4, 0.35, 0], place='radio', view='34', dir=1, pose='m:write/A', face='k:concentrate')
act('radio_op', ['morse', 1], face='k:frozenTongue', pose='m:write/B'); act('radio_op', ['signature', 1], face='k:smug', pose='m:write/A')
# --- café
act('lou', ['café', 1, -4], pos=[1.3, 3.5, 0], place='cafe', view='34', dir=1, pose='m:whisper/A', face='k:slyWink')
act('waitress', ['café', 1, -4], pos=[2.9, 5.2, 0], place='cafe', view='34', dir=-1, pose='m:carry/A', face='k:annoyed')
go('waitress', ['spies', 1], [-0.6, 6.6, 0], [2.9, 5.2, 0], pose='m:walk/A', then='m:idle/C')        # she leaves before the sergeant's close-up
act('spy', ['café', 1, -4], pos=[-2.6, 1.15, 0], place='cafe', view='34', dir=1, pose='m:sit/C', face='k:think')
act('sergeant', ['café', 1, -4], pos=[3.9, 3.4, 0], place='cafe', view='34', dir=-1, pose='m:idle/B', face='k:skeptical')
act('lou', ['secrets', 1], face='k:wink'); act('spy', ['spies', 1], face='k:evil'); act('spy', ['laughs', 1], face='k:smug'); act('spy', ['carnival', 1], face='k:think')
act('sergeant', ['patches', 1], face='k:annoyed'); act('sergeant', ['spies', 1], face='k:browUp'); act('sergeant', ['laughs', 1], pose='m:laugh/A', face='k:laugh')
act('sergeant', ['fight', 1], face='k:smug'); act('sergeant', ['carnival', 1], face='k:laugh', pose='m:laugh/B'); act('sergeant', ['balloons', 1], pose='m:laugh/C', face='k:laugh')
# --- river (the plan and the decoys)
act('lou', ['river', 1, -4], pos=[-20.0, 4.0, 0], place='river', view='34', dir=1, pose='m:board/A', face='k:concentrate')
act('lou', ['hundred', 2], face='k:proud', pose='m:thumbs/A')
act('sergeant', ['river', 1, -6], pos=[57.0, 44.0, 0.6], move_s=0.01, place='river', view='front', dir=1, pose='m:idle/B', face='k:skeptical')   # placed on his boat while the camera is elsewhere (place change)
act('sergeant', ['north', 1], face='k:think'); act('sergeant', ['crosses', 1], face='k:surprised')
act('sergeant', ['fired', 1], face='k:shocked', pose='m:turn/A')
# --- enemy photo room
act('interpreter', ['photographs', 1, -4], pos=[0.2, 0.45, 0], place='photo', view='34', dir=1, pose='m:inspect/A', face='k:smug')
act('interpreter', ['spies', 2], face='k:evil', pose='m:button/A')                                     # "...and sends every gun": the big-moment button
# --- bedroom (the pillow trick): the boy is already outside, at the window
act('boy', ['pillow-under-the-blanket', 1, -4], pos=[1.3, 3.8, 0.6], place='bedroom', view='front', dir=1, pose='m:idle/A', face='k:smirk')
act('boy', ['outside', 1], face='k:slyWink', pose='m:thumbs/A')
# --- attic (today)
act('old_lou', ['fooled', 1, -4], pos=[-1.0, 1.2, 0], place='attic', view='34', dir=1, pose='m:idle/A', face='k:think')
act('grandchild', ['fooled', 1, -4], pos=[0.7, 1.3, 0], place='attic', view='34', dir=-1, pose='m:inspect/B', face='k:surprised')
act('old_lou', ['families', 1], face='k:smirk'); act('old_lou', ['years', 1], face='k:slyWink', pose='m:whisper/A')   # finger to the lips: shh
act('grandchild', ['years', 1, -30], pose='m:lift/A', face='k:excited')                               # lifts the deflated skin overhead (rhymes with frame 0)
sents, i = [], 0
for line in open(os.path.join(EP, 'voice', 'script.txt'), encoding='utf-8').read().replace('!', '!|').replace('? ', '?| ').replace('. ', '.| ').split('|'):
    nw = len(line.split());
    if nw:
        L = line.lower(); who = 'sound_op' if any(x in L for x in ('truck rolls', 'hundred tanks', 'engines')) else 'radio_op' if 'radio' in L else 'boy' if 'pillow' in L else 'old_lou' if any(x in L for x in ('fooled', 'families', 'secret lasted')) else 'farmer' if 'frenchmen' in L else 'sergeant' if ('sergeant' in L or 'carnival' in L or 'crosses the river' in L) else 'interpreter' if 'photographs' in L else 'lou'
        sents.append(dict(text=line.strip(), words=[i, i + nw - 1], subject=who)); i += nw
LAMP_EV = dict(field=dict(lift=[0, 60], set=fr('suitcase'), dent=fr('suitcase') + 7, deflate=fr('rubber')), road=dict(hundred=fr('hundred')), river=dict(inflate=fr('hundred', 2) - 10, shell=fr('gun') + 3, cross=fr('crosses') - 60), attic=dict(lift_skin=fr('years') - 30))
places = {}
for name, light, extra in (('field', 'morning', {}), ('camp', 'day', {}), ('road', 'night', {}), ('radio', 'interior', {}), ('cafe', 'interior', {}), ('photo', 'interior', dict(light_over=dict(sun='#cfe0ff', tint='#dfe8ff'))), ('river', 'night', {}), ('bedroom', 'night', {}), ('attic', 'golden', {})):
    places[name] = dict(set='ghost', zone=name, light=light, backdrop=8 if name in ('radio', 'cafe', 'photo', 'bedroom', 'attic') else 40, events=LAMP_EV.get(name, {}), **extra)
# v1 note 7: particles only where the place has a reason for them (dawn pollen, lamp-lit dust, the attic's sunbeam), none outside at night or in the cold photo room
DUST = dict(field=.3, camp=0, road=0, radio=.35, cafe=.25, photo=0, river=0, bedroom=0, attic=.3)   # V3: attic 1.0 -> .3 (the milky veil)
for name in places: places[name]['post'] = dict(dust=DUST[name])
# v1 note 2: night stays night but the foreground reads (kit light preset lifted: moon key and blue fill)
for name in ('road', 'river', 'bedroom'): places[name].setdefault('light_over', {}).update(si=2.0, ai=2.3, amb='#5a6ca8', hor='#33447a')
film = dict(title='THE GHOST ARMY', fps=30, size=[1080, 1920], end=END, kit3d=True, words='voice/words.json', puppet_pkg=['cast', '../../templates/vector2d_characters/code'],
  post=dict(dof=0), camera_idea=dict(name='The fake reveals itself', why='The audience is fooled first, like the enemy: each chapter opens on something real and powerful, then the camera shows the trick behind it.', signature='On "crosses" one crane rises over the river from the shelled decoys to the real army crossing in silence.'),
  cast={c: dict(puppet='cast:' + c, height=h, heads_tall=ht) for c, h, ht in (('lou', 1.78, 2.9), ('carrier_tall', 1.9, 3.0), ('carrier_stocky', 1.72, 2.8), ('carrier_short', 1.65, 2.8), ('farmer', 1.7, 2.9), ('boy', 1.2, 2.3), ('sergeant', 1.75, 2.8), ('sound_op', 1.76, 2.9), ('radio_op', 1.8, 2.9), ('spy', 1.82, 3.0), ('waitress', 1.62, 2.8), ('interpreter', 1.78, 2.9), ('grandchild', 1.25, 2.3), ('old_lou', 1.72, 2.9))},
  places=places, props=dict(tank=dict(pos=[0, 4, 1.5]), lantern=dict(pos=[0, 0, 0])), takes=takes, acts=A, sentences=sents,
  kicks=[dict(at=['balloons', 2, 3], amp=0.3)],
  # V3 step 9: the 'hit' fx on balloons#2 and its flash_white mood are retired: the layered 3D bursts carry the impact (no white-out)
  fx=[dict(at=['suitcase', 1], kind='knock', pos=[0.3, 3.6, 2.4]), dict(at=['strong', 1], kind='glint', pos=[3.0, 1.3, 1.6]), dict(at=['rubber', 1, 4], kind='steam', pos=[-1.9, 3.2, 2.2]),
      dict(at=['track', 1], kind='dust', pos=[12.0, 0.0, 0.3]), dict(at=['hundred', 1], kind='ring', pos=[0.0, 7.2, 2.75]), dict(at=['morse', 1], kind='spark', pos=[-0.5, 1.4, 0.9]),
      dict(at=['patches', 1], kind='glint', pos=[1.15, 3.45, 0.95]), dict(at=['spies', 1], kind='glint', pos=[-2.6, 1.4, 1.6]), 
      dict(at=['photographs', 1], kind='glint', pos=[0.25, 1.5, 0.95]), dict(at=['years', 1], kind='glint', pos=[0.4, 1.6, 1.8])],
  moods=[dict(at=['tank', 1], look='warm_gold'), dict(at=['rubber', 1], look='spot_dark'), dict(at=['painters', 1], look='warm_up'), dict(at=['nobody', 1], look='dark'), dict(at=['far', 1], look='warm_gold'),
         dict(at=['night', 1], look='cold_blue'), dict(at=['hundred', 1], look='cold_blue'), dict(at=['radio', 1], look='warm_up'), dict(at=['café', 1], look='warm_gold'), dict(at=['carnival', 1], look='spot_dark'),
         dict(at=['river', 1], look='cold_blue'), dict(at=['south', 1], look='dark'), dict(at=['photographs', 1], look='cold_blue'), dict(at=['balloons', 2], look='warm_up'), dict(at=['crosses', 1], look='cold_blue'),
         dict(at=['pillow-under-the-blanket', 1], look='cold_blue'), dict(at=['families', 1], look='warm_up'), dict(at=['years', 1], look='warm_gold')],
  sound=[dict(at=['suitcase', 1], name='rubber_thump'), dict(at=['bicycles', 1], name='bike_brakes_skid'), dict(at=['rubber', 1], name='valve_air_whistle'), dict(at=['bulldozer', 1], name='dozer_engine'),
         dict(at=['hundred', 1], name='tank_column_playback'), dict(at=['morse', 1], name='morse_beeps'), dict(at=['café', 1], name='cafe_room_accordion'), dict(at=['laughs', 1], name='sergeant_laugh'),
         dict(at=['hundred', 2], name='inflation_wave'), dict(at=['balloons', 2], name='shell_whistle_impacts'), dict(at=['crosses', 1], name='river_silence_paddles'), dict(at=['years', 1], name='music_box_attic')],
  # V3 steps 7-8 (2026-11-18): a camera that never parks (rest drift x2.6, gentle push) and joins without unmotivated hard cuts.
  # joins: how each take is entered (by the incoming take). 'dissolve' = n-frame blend in the edit (edit/joins.py); 'cut' = kept on purpose, with the reason.
  camera_life=dict(rest_mult=1.0, push=0.0015),
  joins=[dict(take='t_camp', kind='dissolve', frames=4, why='push-through from the deflating valve into the camp'),
         dict(take='t_road', kind='dissolve', frames=6, why='day to night: a slower blend marks the time jump'),
         dict(take='t_radio', kind='dissolve', frames=3, why='push into the horn, push out of the radio: the sound carries the join'),
         dict(take='t_cafe', kind='dissolve', frames=4, why='push-through from the radio to the cafe'),
         dict(take='t_sergeant', kind='cut', frames=0, why='deliberate comic cut on "sergeant" (v1 note 3: the travel cut Lou by the edge); same room'),
         dict(take='t_river', kind='dissolve', frames=5, why='cafe to the river at night'),
         dict(take='t_photo', kind='dissolve', frames=3, why='push-through: the decoy field becomes the enemy photograph'),
         dict(take='t_strike', kind='cut', frames=0, why='deliberate shock cut: "every gun" lands on the shelling'),
         dict(take='t_bed', kind='dissolve', frames=6, why='place and mood change: the shelling to the quiet bedroom'),
         dict(take='t_attic', kind='dissolve', frames=6, why='decades later: the time jump to the attic')],
  tween=dict(ones=True, face_frames=0, move_blend=6), motion_polish=dict(enabled=True, head_follow=0.14, hand_follow=0.08, breath=0.55, breath_rate=2.15, auto_blink=True))
json.dump(film, open(os.path.join(EP, 'film.json'), 'w'), indent=1, ensure_ascii=False)
print('film.json written: end', END, 'frames,', len(takes), 'takes,', sum(len(t['stations']) for t in takes), 'stations,', len(A), 'acts')



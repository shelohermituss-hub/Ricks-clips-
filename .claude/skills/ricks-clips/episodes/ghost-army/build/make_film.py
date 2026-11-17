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
   St(['rubber', 1], [1.6, -0.8, 1.9], [-1.3, 3.0, 1.5], lens=28, framing='O', lead=3, travel=0.9, **C)]),
 dict(id='t_camp', place='camp', stations=[
   St(['painters', 1], [-14.0, -8.0, 3.0], [-4.0, 10.0, 1.2], framing='P', lead=4, hold=0.3),
   St(['job', 1], [2.8, -4.4, 1.5], [1.0, -1.4, 1.3], framing='M', lead=3, hold=0.3, travel=1.4),
   St(['rule', 1], [-0.6, -2.2, 1.3], [-2.2, 2.4, 1.1], lead=3, hold=0.2, travel=1.2),
   St(['close', 1], [-5.6, 8.6, 1.5], [-4.0, 12.0, 1.4], framing='O', subj='carrier_short', lead=3, travel=0.8, **C),
   St(['army', 2], [-6.0, -30.0, 12.0], [-4.0, 14.0, 0.5], framing='P', lead=3, hold=0.2, travel=1.4, drift=[0.12, 0.08, 0.0]),
   St(['bulldozer', 1], [19.0, -7.0, 3.0], [12.0, 0.0, 0.6], framing='P', lead=3, travel=1.4)]),
 dict(id='t_road', place='road', stations=[
   St(['night', 1], [-1.2, -2.4, 1.4], [1.4, 4.2, 1.5], subj='sound_op', lead=4, hold=0.3),
   St(['hundred', 1], [-7.0, -9.0, 2.4], [-5.0, 22.0, 2.0], subj='sound_op', framing='P', lead=6, hold=0.3, travel=0.8, drift=[0.12, 0.08, 0.0]),
   St(['speaker', 1], [3.0, 3.6, 3.3], [0.0, 7.2, 2.7], subj='sound_op', framing='O', lead=3, travel=1.0, **C)]),
 dict(id='t_radio', place='radio', stations=[
   St(['radio', 1], [1.8, -1.6, 1.7], [-0.2, 1.2, 1.1], subj='radio_op', framing='M', lead=4, hold=0.3),
   St(['morse', 1], [-0.3, 0.2, 1.5], [-0.4, 1.6, 1.0], subj='radio_op', framing='O', lead=3, travel=0.9, **C)]),
 dict(id='t_cafe', place='cafe', stations=[
   St(['café', 1], [-1.2, -1.6, 1.7], [1.2, 3.8, 1.3], lead=4, hold=0.3),
   St(['patches', 1], [0.6, 1.6, 1.5], [1.4, 3.6, 1.2], framing='M', lead=3, hold=0.2, travel=0.9),
   St(['spies', 1], [-1.0, -0.2, 1.4], [-2.6, 1.6, 1.1], subj='spy', framing='M', lead=3, hold=0.2, travel=0.9),
   St(['carnival', 1], [2.6, 0.9, 1.6], [3.9, 3.4, 1.4], subj='sergeant', framing='C', lead=3, travel=1.2, **C)]),
 dict(id='t_river', place='river', stations=[
   St(['river', 1], [-22.6, -0.4, 1.6], [-19.6, 4.6, 1.2], lead=4, hold=0.3),
   St(['hundred', 2], [-36.0, 6.0, 5.0], [-25.0, 28.0, 0.5], framing='P', lead=3, travel=1.6)]),
 dict(id='t_photo', place='photo', stations=[
   St(['photographs', 1], [-1.4, -1.6, 1.8], [0.1, 1.2, 1.1], subj='interpreter', framing='M', lead=4, hold=0.3),
   St(['spies', 2], [1.6, -0.6, 1.6], [0.2, 1.3, 1.0], subj='interpreter', framing='M', lead=3, travel=0.8)]),
 dict(id='t_strike', place='river', stations=[
   St(['gun', 1], [-34.0, 10.0, 4.0], [-26.0, 26.0, 1.0], framing='P', lead=4, hold=0.3),
   ]),
 dict(id='t_cross', place='river', stations=[
   St(['meanwhile', 1], [49.0, 14.0, 7.0], [60.0, 34.0, 0.6], subj='sergeant', framing='P', lead=4, hold=0.3, drift=[0.12, 0.08, 0.0]),
   St(['crosses', 1], [50.0, 26.0, 6.0], [60.0, 48.0, 0.5], subj='sergeant', framing='P', lead=3, hold=0.2, travel=1.2),
   St(['fired', 1], [56.4, 40.0, 1.3], [58.6, 44.0, 1.5], subj='sergeant', framing='C', lead=3, travel=0.9, **C)]),
 dict(id='t_bed', place='bedroom', stations=[
   St(['pillow-under-the-blanket', 1], [0.8, -1.0, 1.5], [-0.4, 2.2, 0.9], subj='boy', lead=4, hold=0.3),
   St(['outside', 1], [0.2, -0.2, 1.3], [1.3, 3.2, 1.0], subj='boy', framing='M', lead=3, travel=1.0)]),
 dict(id='t_attic', place='attic', stations=[
   St(['fooled', 1], [0.3, -2.6, 1.5], [0.0, 1.8, 1.0], subj='old_lou', lead=4, hold=0.3),
   St(['families', 1], [-0.4, -0.8, 1.3], [-1.0, 1.3, 1.3], subj='old_lou', framing='M', lead=3, hold=0.3, travel=1.0),
   St(['years', 1], [0.2, -1.4, 1.2], [0.1, 1.5, 1.3], subj='grandchild', framing='M', lead=3, travel=1.0)])]
A = []
def act(who, at, **o): A.append(dict(who=who, at=at, **o))
# --- field (hook)
for who, pos, d in (('lou', [1.9, 2.6, 0], -1), ('carrier_tall', [-1.4, 2.2, 0], 1), ('carrier_short', [1.4, 5.8, 0], -1), ('carrier_stocky', [-1.8, 6.0, 0], 1)):
    act(who, 0, pos=pos, place='field', view='34', dir=d, pose='hold_up', face='k:concentrate')
for who, p_ in (('carrier_tall', [-2.4, 0.4, 0]), ('carrier_short', [3.0, 7.4, 0]), ('carrier_stocky', [-3.6, 6.8, 0])): act(who, ['suitcase', 1, -6], pos=p_, move_s=0.5, pose='stand', face='k:sleepy')   # step out from under the hull once it is set down
act('lou', ['suitcase', 1, -6], pos=[2.3, 1.0, 0], move_s=0.5, pose='knock', face='k:smirk'); act('lou', ['soldier', 1], pos=[3.0, 1.3, 0], walk=True, pose='stand', view='front')
act('lou', ['winks', 1], face='k:slyWink', pose='hands_hips'); act('lou', ['rubber', 1], pos=[-1.6, 2.4, 0], move_s=0.4, linear=True, view='side', dir=1, pose='push', face='k:proud')
act('farmer', 0, pos=[-7.8, -24.0, 0], place='field', view='side', dir=1, pose='m:bike/A+props', face='k:standard')
act('boy', 0, pos=[-6.7, -26.0, 0], place='field', view='side', dir=1, pose='m:bike/B+props', face='k:happy')
act('farmer', ['bicycles', 1, -36], pos=[-7.8, -2.6, 0], move_s=1.3, linear=True); act('boy', ['bicycles', 1, -36], pos=[-6.7, -4.6, 0], move_s=1.4, linear=True)
act('farmer', ['dead', 1], pose='flinch', view='34', dir=1, face='k:shocked'); act('boy', ['dead', 1], pose='point_out', view='34', dir=1, face='k:surprised')
act('boy', ['strong', 1], face='k:excited', pose='cheer')
# --- camp
act('lou', ['painters', 1, -2], pos=[1.0, -1.4, 0], place='camp', view='34', dir=-1, pose='write', face='k:happy')
act('carrier_short', ['painters', 1, -2], pos=[-4.6, 9.4, 0], place='camp', view='34', dir=1, pose='m:sweep/A', face='k:concentrate')
act('carrier_tall', ['painters', 1, -2], pos=[-3.6, 2.6, 0], place='camp', view='side', dir=1, pose='push', face='k:strain' if False else 'k:concentrate')
act('lou', ['job', 1], face='k:smug', view='front'); act('lou', ['nobody', 1], face='k:wink'); act('lou', ['rule', 1], pos=[-2.0, 2.0, 0], walk=True, pose='point_out', face='k:proud')
act('lou', ['far', 1], face='k:cheer', pose='cheer')
# --- road (night)
act('sound_op', ['night', 1, -4], pos=[2.0, 3.4, 0], place='road', view='34', dir=-1, pose='stand', face='k:concentrate')
act('sound_op', ['hundred', 1], pose='finger_up', face='k:smug'); act('sound_op', ['speaker', 1], face='k:proud')
# --- radio tent
act('radio_op', ['radio', 1, -4], pos=[-0.4, 0.7, 0], place='radio', view='34', dir=1, pose='write', face='k:concentrate')
act('radio_op', ['morse', 1], face='k:frozenTongue'); act('radio_op', ['signature', 1], face='k:smug')
# --- café
act('lou', ['café', 1, -4], pos=[1.3, 3.5, 0], place='cafe', view='34', dir=1, pose='lean_in', face='k:slyWink')
act('waitress', ['café', 1, -4], pos=[2.9, 5.2, 0], place='cafe', view='34', dir=-1, pose='hold_out', face='k:annoyed')
act('spy', ['café', 1, -4], pos=[-2.6, 1.4, 0], place='cafe', view='34', dir=1, pose='sit', face='k:think')
act('sergeant', ['café', 1, -4], pos=[3.9, 3.4, 0], place='cafe', view='34', dir=-1, pose='stand', face='k:skeptical')
act('lou', ['secrets', 1], face='k:wink'); act('spy', ['spies', 1], face='k:evil', pose='write')
act('sergeant', ['patches', 1], face='k:annoyed'); act('sergeant', ['spies', 1], face='k:browUp'); act('sergeant', ['laughs', 1], pose='m:laugh/A', face='k:laugh')
# --- river (the plan and the decoys)
act('lou', ['river', 1, -4], pos=[-20.0, 4.0, 0], place='river', view='34', dir=1, pose='point_out', face='k:concentrate')
act('lou', ['hundred', 2], face='k:proud', pose='hands_hips')
act('sergeant', ['meanwhile', 1, -4], pos=[58.6, 44.0, 0], place='river', view='front', dir=1, pose='stand', face='k:skeptical')
act('sergeant', ['fired', 1], face='k:shocked', pose='flinch')
# --- enemy photo room
act('interpreter', ['photographs', 1, -4], pos=[0.2, 0.7, 0], place='photo', view='34', dir=1, pose='lean_in', face='k:smug')
act('interpreter', ['spies', 2], face='k:evil', pose='point_out')
# --- bedroom (the pillow trick): the boy is already outside, at the window
act('boy', ['pillow-under-the-blanket', 1, -4], pos=[1.3, 3.8, 0.6], place='bedroom', view='front', dir=1, pose='hands_hips', face='k:smirk')
act('boy', ['outside', 1], face='k:slyWink')
# --- attic (today)
act('old_lou', ['fooled', 1, -4], pos=[-1.0, 1.2, 0], place='attic', view='34', dir=1, pose='stand', face='k:think')
act('grandchild', ['fooled', 1, -4], pos=[0.7, 1.3, 0], place='attic', view='34', dir=-1, pose='bend_down', face='k:surprised')
act('old_lou', ['families', 1], face='k:smirk'); act('old_lou', ['years', 1], face='k:slyWink', pose='finger_up')
act('grandchild', ['years', 1, -30], pose='hold_up', face='k:excited')
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
film = dict(title='THE GHOST ARMY', fps=30, size=[1080, 1920], end=END, kit3d=True, words='voice/words.json', puppet_pkg=['cast', '../../templates/vector2d_characters/code'],
  post=dict(dof=0), camera_idea=dict(name='The fake reveals itself', why='The audience is fooled first, like the enemy: each chapter opens on something real and powerful, then the camera shows the trick behind it.', signature='On "crosses" one crane rises over the river from the shelled decoys to the real army crossing in silence.'),
  cast={c: dict(puppet='cast:' + c, height=h, heads_tall=ht) for c, h, ht in (('lou', 1.78, 2.9), ('carrier_tall', 1.9, 3.0), ('carrier_stocky', 1.72, 2.8), ('carrier_short', 1.65, 2.8), ('farmer', 1.7, 2.9), ('boy', 1.2, 2.3), ('sergeant', 1.75, 2.8), ('sound_op', 1.76, 2.9), ('radio_op', 1.8, 2.9), ('spy', 1.82, 3.0), ('waitress', 1.62, 2.8), ('interpreter', 1.78, 2.9), ('grandchild', 1.25, 2.3), ('old_lou', 1.72, 2.9))},
  places=places, props=dict(tank=dict(pos=[0, 4, 1.5]), lantern=dict(pos=[0, 0, 0])), takes=takes, acts=A, sentences=sents,
  kicks=[dict(at=['balloons', 2, 3], amp=0.3)],
  fx=[dict(at=['suitcase', 1], kind='knock', pos=[0.3, 3.6, 2.4]), dict(at=['strong', 1], kind='glint', pos=[3.0, 1.3, 1.6]), dict(at=['rubber', 1, 4], kind='steam', pos=[-1.9, 3.2, 2.2]),
      dict(at=['track', 1], kind='dust', pos=[12.0, 0.0, 0.3]), dict(at=['hundred', 1], kind='ring', pos=[0.0, 7.2, 2.75]), dict(at=['morse', 1], kind='spark', pos=[-0.5, 1.4, 0.9]),
      dict(at=['patches', 1], kind='glint', pos=[1.4, 3.4, 1.3]), dict(at=['spies', 1], kind='glint', pos=[-2.6, 1.4, 1.6]), dict(at=['hundred', 2], kind='puff', pos=[-25.0, 28.0, 1.0], size=2),
      dict(at=['photographs', 1], kind='glint', pos=[0.25, 1.5, 0.95]), dict(at=['balloons', 2], kind='hit', pos=[-30.0, 26.0, 2.0], size=2), dict(at=['years', 1], kind='glint', pos=[0.4, 1.6, 1.8])],
  moods=[dict(at=['tank', 1], look='warm_gold'), dict(at=['rubber', 1], look='spot_dark'), dict(at=['painters', 1], look='warm_up'), dict(at=['nobody', 1], look='dark'), dict(at=['far', 1], look='warm_gold'),
         dict(at=['night', 1], look='cold_blue'), dict(at=['hundred', 1], look='cold_blue'), dict(at=['radio', 1], look='warm_up'), dict(at=['café', 1], look='warm_gold'), dict(at=['carnival', 1], look='spot_dark'),
         dict(at=['river', 1], look='cold_blue'), dict(at=['south', 1], look='dark'), dict(at=['photographs', 1], look='cold_blue'), dict(at=['balloons', 2], look='flash_white'), dict(at=['crosses', 1], look='cold_blue'),
         dict(at=['pillow-under-the-blanket', 1], look='cold_blue'), dict(at=['families', 1], look='warm_up'), dict(at=['years', 1], look='warm_gold')],
  sound=[dict(at=['suitcase', 1], name='rubber_thump'), dict(at=['bicycles', 1], name='bike_brakes_skid'), dict(at=['rubber', 1], name='valve_air_whistle'), dict(at=['bulldozer', 1], name='dozer_engine'),
         dict(at=['hundred', 1], name='tank_column_playback'), dict(at=['morse', 1], name='morse_beeps'), dict(at=['café', 1], name='cafe_room_accordion'), dict(at=['laughs', 1], name='sergeant_laugh'),
         dict(at=['hundred', 2], name='inflation_wave'), dict(at=['balloons', 2], name='shell_whistle_impacts'), dict(at=['crosses', 1], name='river_silence_paddles'), dict(at=['years', 1], name='music_box_attic')],
  motion_polish=dict(enabled=True, head_follow=0.14, hand_follow=0.08, breath=0.55, breath_rate=2.15, auto_blink=True))
json.dump(film, open(os.path.join(EP, 'film.json'), 'w'), indent=1, ensure_ascii=False)
print('film.json written: end', END, 'frames,', len(takes), 'takes,', sum(len(t['stations']) for t in takes), 'stations,', len(A), 'acts')

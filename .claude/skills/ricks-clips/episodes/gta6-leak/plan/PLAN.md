# Plan — He Leaked GTA 6 From A Hotel Room

Généré depuis `plan.json` par `tools/plan_to_md.py`. Narration EN, voix Fish 'rick' (voice/). Faits et sources: research/SOURCES.md. Aucune marque Rockstar/GTA dessinée: le jeu = écrans flous, boîte générique « 6 ». Droits: personnages de notre distribution.

**Durée** 54.4 s · **voix** 187 mots · **format** 1080x1920, 30 i/s · **style** `references/STYLE_BIBLE_FR.md` · **sous-titres** white bold rounded, thick black outline, centred at 70 % height, one change per word (words.json)

**Crochet** : action `plug_in` à 0.3 s · **boucle** : last shot pushes into the switched-off cell TV, whose reflection matches the hotel TV of the first frame

## Faits écrits dans le décor

| Fait | Plan | Objet du décor |
|---|---|---|
| 18 — eighteen years old | S02 | hotel key card sleeve with a birthday sticker '18' + bail tag on his ankle |
| 90 clips (over 90) | S04 | upload counter on the laptop-TV screen climbing 0 -> 90 CLIPS UPLOADED |
| $5 million — 5,000,000 | S05 | giant invoice printed on the studio printer: DAMAGE $5,000,000 |
| thousands of hours | S05 | wall clock spinning + timesheet board '4,000 HRS' |
| secure hospital, indefinite | S06 | hospital door sign SECURE WARD + stamp INDEFINITE on the file |
| 90,421,491 views in 24 h — record | S07 | dusk billboard counter 90,421,491 VIEWS + trophy plaque WORLD RECORD |
| fit for trial — moved to prison | S08 | doctor's stamp FIT FOR TRIAL on the file |
| Nov 16 guilty plea, Nov 19 release, 3 days, GTA 6 | S09 | tear-off calendar NOV 16 -> NOV 19 + shop window poster with a big '6' (no logo) |

## Besoins (téléchargés ou construits avant le premier plan)

| Quoi | Source | État |
|---|---|---|
| hotel_room | script (sets/hotel.py): bed, bedside lamp, wall TV, curtains, carpet scan | to build |
| carpet | polyhaven:fabric_pattern_05 or ambientcg Carpet (to pick at download) | to download |
| wood_floor | polyhaven:wood_floor_deck / laminate_floor_02 | to download |
| concrete_wall_008 | polyhaven:concrete_wall_008 | cached |
| night_city_hdri | polyhaven (city night, CC0, to pick) | to download |
| tv_stick, phone, keyboard, remote | script (small detailed props, rounded bevels) | to build |
| cast | cast: hacker, police, judge, doctor, programmer, gamer, nurse | drawn by tools/card_service.py |
| sounds | templates/audio sfx_gen + rc.sound | to generate |

## Lieux

### hotel — night: blue TV glow + warm bedside lamp

budget hotel room at night: double bed with a crumpled duvet, bedside lamp, wall TV, half-drawn curtains with the city lights, room-service tray, ugly patterned carpet, 'DO NOT DISTURB' hanger

- **Sol** : polyhaven:fabric_pattern_05 · **surfaces** : walls (polyhaven:beige_wall_001), headboard (polyhaven:fabric_leather_02)
- **Ciel** : city night through the window (lit windows, a few neon signs), HDRI for reflections only
- **Lumière** : soleil élév. -10°, azimut 0°, énergie 0.0, angle 1.5° ; appoint 0.08; TV screen emission 6 (blue-white, flickers with the screen content); bedside lamp 40 W warm 2700 K; street neon through the curtains (magenta, slow pulse)
- **Ombres** : hard TV-light shadow of his head and hands on the duvet and wall; lamp shadow of the bed corner on the carpet; curtain slats stripe the wall
- **Accessoires** : tv_stick (script), phone (script), keyboard (script), room_service_tray (script + polyhaven food props), do_not_disturb_hanger (script + text decal), key_card_sleeve_18 (script + text decal), energy_drink_cans (script)

### corridor — night interior: warm sconces, light under his door flickering blue

hotel corridor outside his door: patterned carpet, door 214, police officer on a chair with a paper cup

- **Sol** : polyhaven:fabric_pattern_05 · **surfaces** : walls (polyhaven:beige_wall_001), doors (polyhaven:wood_table_001)
- **Ciel** : none (interior)
- **Lumière** : soleil élév. -10°, azimut 0°, énergie 0.0, angle 1.5° ; appoint 0.15; wall sconces warm; blue TV flicker under the door
- **Ombres** : sconce pools on the carpet, the officer's long shadow across the door
- **Accessoires** : chair (polyhaven:woodenchair_01), paper_cup (script), door_214 (script + decal), fire_extinguisher (script), ice_machine (script)

### city — night city: windows, street lamps

the city at night seen from above: rooftops, streets of light; the 90 clips fly out of the hotel window like glowing cards and scatter over the city into thousands of phone screens lighting up

- **Sol** : polyhaven:asphalt_track · **surfaces** : rooftops (polyhaven:concrete_wall_008)
- **Ciel** : deep night blue gradient, a few clouds lit from below
- **Lumière** : soleil élév. -8°, azimut 0°, énergie 0.0, angle 1.5° ; appoint 0.12
- **Ombres** : little sun; the flying clips cast moving light pools on the roofs
- **Accessoires** : instanced_buildings (script (boxes with window textures, built for the frame)), street_lamps (script), billboards (script), clip_cards (script (90 emissive cards))

### studio — cold morning + red alarm

a game studio open office in panic: rows of desks, big monitors, coffee everywhere, red alarm light, printer spitting the damage invoice

- **Sol** : polyhaven:laminate_floor_02 · **surfaces** : walls (polyhaven:beige_wall_001), desks (polyhaven:wood_table_001)
- **Ciel** : city morning through big windows
- **Lumière** : soleil élév. 25°, azimut 120°, énergie 4.5, angle 1.5° ; appoint 0.35; rotating red alarm light; monitor glows; fluorescent ceiling panels
- **Ombres** : window frames cast long bars across the desks; alarm sweeps red shadows
- **Accessoires** : desks_monitors (script), printer (script), invoice (script + decal), wall_clock (script), timesheet_board (script + decal), coffee_cups (script)

### court_hospital — warm court wood, then cold hospital white

courtroom (wood panels, judge's bench, gavel) then the secure hospital corridor (white, glass, heavy door)

- **Sol** : polyhaven:wood_floor_deck · **surfaces** : panels (polyhaven:wood_table_001), hospital floor (polyhaven:concrete_floor_painted)
- **Ciel** : tall court windows, overcast
- **Lumière** : soleil élév. 35°, azimut 200°, énergie 3.5, angle 3° ; appoint 0.3; brass desk lamps in court; cold strip lights in the hospital
- **Ombres** : window light shafts across the court; hospital: the closing door's shadow swallows him
- **Accessoires** : judge_bench (script), gavel (script), secure_door (script + decal SECURE WARD), file_stamp_indefinite (script + decal)

### billboard — purple dusk + billboard glow

a huge digital billboard over a square at purple dusk, the view counter racing to 90,421,491, people stopping with their phones up

- **Sol** : polyhaven:brick_pavement_03 · **surfaces** : buildings (polyhaven:concrete_wall_008)
- **Ciel** : purple to orange dusk gradient, pink clouds
- **Lumière** : soleil élév. 3°, azimut 250°, énergie 3.0, angle 2° ; appoint 0.35
- **Ombres** : long low-sun shadows of the crowd across the paving; the billboard throws coloured light on faces
- **Accessoires** : billboard_counter (script + animated text decal), record_trophy (script), crowd_phones (script (cards)), street_furniture (script)

### doctor_prison — cold daylight office, grey prison

doctor's office (stamp FIT FOR TRIAL) then the prison van / cell

- **Sol** : polyhaven:concrete_floor_painted · **surfaces** : prison walls (polyhaven:concrete_wall_008)
- **Ciel** : none
- **Lumière** : soleil élév. 30°, azimut 160°, énergie 3.0, angle 1.5° ; appoint 0.3
- **Ombres** : window bar shadows on the cell floor; desk lamp pool on the file
- **Accessoires** : stamp (script), patient_file (script + decal), cell_bunk (script), small_cell_tv (script)

### shop_street — neon night (pink / cyan)

a game shop street at night: the queue of gamers in hoodies with sleeping bags, neon, a shop window with a big '6' poster (no logo), a tear-off calendar in the shop

- **Sol** : polyhaven:brick_pavement_03 · **surfaces** : shopfront (polyhaven:concrete_wall_008)
- **Ciel** : night, wet street reflections
- **Lumière** : soleil élév. -10°, azimut 0°, énergie 0.0, angle 1.5° ; appoint 0.12; shop window light; neon sign; phone screens in the queue
- **Ombres** : queue silhouettes against the bright window, long neon shadows on the wet pavement
- **Accessoires** : queue_gamers (cast cards), poster_6 (script + decal), calendar (script + decal), sleeping_bags (script), puddles (script (wet decals))

## Personnages (une carte, une vue chacun)

| Rôle | Distribution | Costume | Vue | Tient |
|---|---|---|---|---|
| kid | cast:hacker | hoodie, pyjama trousers, socks, ankle bail tag (3D prop) | 34 | tv_stick, phone, keyboard |
| cop | cast:police | uniform, paper cup | 34 |  |
| judge | cast:judge | robe, wig | front |  |
| doctor | cast:doctor | white coat, clipboard | 34 |  |
| dev | cast:programmer | studio hoodie (no logo), headset | 34 |  |
| gamer | cast:gamer | hoodie, sleeping bag, phone | 34 |  |

## Objets et leurs états

| Objet | Matière | États |
|---|---|---|
| tv_stick | matte black plastic, tiny LED | in the box → plugged in (LED on) |
| phone | glass + aluminium, screen emission | dark → lit hotspot screen |
| keyboard | black plastic keys, backlight | on the bed → typing (keys press) |
| hotel_tv | glossy black bezel, emissive screen | off → on: code / chat / upload bar |
| clips | emissive video frames (blurred generic game shots, no logo) | on screen → flying → landed on phones |
| invoice | paper | printing → unrolled across the floor |
| file | paper folder | blank → stamped INDEFINITE → stamped FIT FOR TRIAL |
| counter | emissive LED | 0 → racing → 90,421,491 |
| calendar | paper | NOV 16 → pages torn → NOV 19 |
| cell_tv | old plastic TV | off (reflection) |
| secure_door | painted steel, wired glass window | open → closed and locked |
| cell_door | steel bars | open → slid shut |

## Plans

### S01 — hotel (0.00 → 5.48 s), night TV

> He leaked the biggest video game on Earth from a hotel room, using nothing but a TV stick and a phone.

**Entrée** : first frame (loop target) · **sortie** : whip pan to the door · **type** : insert

**Caméra** (jamais à l'arrêt, + dérive à l'épaule) :

- 0.00 s · insert · 40 mm · macro push on the stick going into the TV port · vise tv port
- 1.60 s · close · 42 mm · pull back and rise: his face lights up · vise kid face lit by the TV
- 3.60 s · wide · 68 mm · crane back to the whole room: stick, phone, TV · vise room
- 5.48 s · medium · 50 mm · slow drift · vise room

**Actions** :

- **plug_in** (kid, images 9–45) : plugs the TV stick into the hotel TV — *m:button/A (hand to the port), stick follows the hand (card_anchors)*
  - micro : fingers wiggle the stick in; LED blinks
  - réactions : his hand reaches the port and the stick follows the hand from contact (no teleport); the TV wakes: static then a blue boot screen; the room goes from dark to TV-blue
  - conséquences qui restent : the stick stays plugged with its LED on for the whole film; the empty stick box is left on the bed
  - sons : click; TV power-on hum
- **grin** (kid, images 48–102) : his face lights up blue, sly grin — *m:idle/B k:smug*
  - micro : blink; eyebrow wiggle
  - réactions : the face changes ON the word 'leaked' with a head pop; the body answers the face: he leans back on the pillows, shoulders up; TV light flickers on his face
  - conséquences qui restent : the grin stays as he settles on the bed
  - sons : sly 'heh'
- **phone_hotspot** (phone, images 108–164) : the phone on the bed lights up: hotspot on — *screen emission keyed*
  - micro : vibrates on the duvet
  - réactions : the phone screen lights up with a flicker; the duvet under it glows
  - conséquences qui restent : phone stays lit on the bed
  - sons : buzz
- **can_tip** (kid, images 126–156) : his elbow knocks an energy-drink can off the bedside table — *m:idle/B elbow + can rigid-body keys*
  - micro : can wobbles before falling
  - réactions : can falls and rolls, fizz sprays
  - conséquences qui restent : can lies on the carpet, a wet fizz stain
  - sons : can clank; fizz

**Entrées / sorties / changements d'état** : tv_stick : box -> plugged in (par plug_in); hotel_tv : off -> on (par plug_in); phone : dark -> lit (par phone_hotspot)

**Effets** : TV static burst; dust motes in the TV beam · **ambiance sonore** : night room tone, distant traffic, TV hum

### S02 — corridor (5.48 → 11.42 s), night corridor

> You see, he was 18, already on bail for hacking, and hiding in that hotel under police protection.

**Entrée** : whip pan through the door · **sortie** : slide under the door back into the room · **type** : medium

**Caméra** (jamais à l'arrêt, + dérive à l'épaule) :

- 5.48 s · medium · 50 mm · slow push down the corridor · vise door 214 + cop
- 8.48 s · close · 42 mm · dolly to the cop's face · vise cop
- 11.42 s · insert · 40 mm · drop to the floor and slide toward the blue light under the door · vise gap under the door

**Actions** :

- **cop_yawn** (cop, images 170–254) : the officer on guard yawns and sips coffee — *m:drink/A*
  - micro : eyes heavy, head nods
  - réactions : the face changes ON the word 'protection' with a head pop; the body answers the face: he slumps, shoulders drop; coffee steams; the chair creaks
  - conséquences qui restent : the emotion stays: he dozes off; coffee ring stays on the floor by the chair
  - sons : yawn; slurp
- **cup_spill** (cop, images 230–254) : as he nods off, the paper cup tilts and drips — *cup keyed tilt in the hand anchor*
  - micro : drips
  - réactions : coffee stream with the right thickness, splash where it lands, spreading puddle
  - conséquences qui restent : puddle by the chair stays
  - sons : drip; splat
- **bail_tag** (kid, images 260–343) : inside: the bail tag on his ankle blinks green as he types — *card idle + 3D tag prop on the ankle anchor*
  - micro : toes wiggle
  - réactions : the tag LED lights up and blinks with each key
  - conséquences qui restent : tag stays on his ankle all film
  - sons : tag beep

**Entrées / sorties / changements d'état** : cop : already in place when the camera arrives (in frame from the first frame of the shot) (par cut)

**Effets** : steam from the cup; blue flicker under the door · **ambiance sonore** : corridor hum, ice machine

### S03 — hotel (11.42 → 16.58 s), night TV

> So he plugged the stick into the TV, grabbed a keyboard, and slipped into Rockstar's private chat.

**Entrée** : slide under the door · **sortie** : push into the TV screen · **type** : insert

**Caméra** (jamais à l'arrêt, + dérive à l'épaule) :

- 11.42 s · insert · 40 mm · top-down insert, slow rotate · vise keyboard on duvet
- 13.82 s · close · 42 mm · orbit around him · vise kid typing
- 16.58 s · pov · 60 mm · push into the TV: the chat window fills the frame (POV) · vise TV screen

**Actions** :

- **grab_keyboard** (kid, images 343–379) : grabs the keyboard from under a pizza box — *m:button/B, keyboard follows the hands from contact*
  - micro : pizza box slides off
  - réactions : his hands reach the keyboard and it follows the hands from contact (no teleport); crumbs fall off the keys
  - conséquences qui restent : pizza box open on the floor, the place where the keyboard was is empty with crumbs
  - sons : cardboard slide; plastic clack
- **type** (kid, images 379–497) : types fast, the chat window opens on the TV — *m:write/A fast*
  - micro : fingers blur; tongue out
  - réactions : keys light under his fingers; lines of code scroll on the TV
  - conséquences qui restent : the chat window stays open on the TV
  - sons : keyboard rattle; chat ping
- **access** (hotel_tv, images 445–497) : the TV flashes ACCESS GRANTED in green, his grin widens — *screen decal swap*
  - micro : screen glitch
  - réactions : the screen lights up green on his face with a flicker
  - conséquences qui restent : the chat stays open
  - sons : access chime

**Entrées / sorties / changements d'état** : keyboard : bed -> his hands (par grab_keyboard)

**Effets** : code light scrolling on his face · **ambiance sonore** : keyboard clatter, TV hum

### S04 — city (16.58 → 20.94 s), night city

> Then he dropped over 90 clips of the secret game for the whole internet to see.

**Entrée** : through the TV screen and out of the window · **sortie** : clips rain down -> match cut to the studio window · **type** : aerial

**Caméra** (jamais à l'arrêt, + dérive à l'épaule) :

- 16.58 s · aerial · 65 mm · fly out of the window with the first clip · vise hotel window
- 18.58 s · aerial · 65 mm · rise above the city as the swarm spreads · vise clips swarm
- 20.94 s · aerial · 65 mm · dive toward the streets · vise phones lighting up

**Actions** :

- **upload** (kid, images 497–527) : hits ENTER: the upload counter climbs to 90 — *m:button/A + counter decal swap*
  - micro : finger slam
  - réactions : the number changes on every beat 0 -> 30 -> 60 -> 90 CLIPS UPLOADED, flashes at 90; the clips peel off the screen
  - conséquences qui restent : the final number stays on screen: 90 on the TV
  - sons : enter clack; whoosh
- **clips_fly** (clips, images 515–628) : 90 glowing clips fly out of the window over the city and land on thousands of phones — *instanced cards on seeded curves*
  - micro : each clip flutters
  - réactions : clips burst out and flutter down, spinning, catching the light; windows and phones light up block by block
  - conséquences qui restent : the city stays dotted with lit screens; a few clips stuck on antennas and chimneys
  - sons : swarm whoosh; notification pings
- **pigeon** (clips, images 557–587) : a pigeon on a rooftop ducks as a clip whooshes past, feathers fly — *pigeon card keyed duck*
  - micro : head bob
  - réactions : feathers puff
  - conséquences qui restent : one feather drifts down
  - sons : coo; flap
- **phones_light** (clips, images 587–628) : a gamer in his bedroom jumps when his phone lights up with the clip — *m:react/confused + phone emission*
  - micro : eyes widen
  - réactions : his phone screen lights up with a flicker on his face
  - conséquences qui restent : phone stays lit
  - sons : ping; gasp

**Entrées / sorties / changements d'état** : clips : screen -> sky -> phones (par clips_fly)

**Effets** : glowing clip swarm; window lights popping on · **ambiance sonore** : city night wind, pings

### S05 — studio (20.94 → 25.74 s), cold morning

> Rockstar says the leak cost them $5 million and thousands of hours of work.

**Entrée** : match cut: phone screens -> studio monitors · **sortie** : invoice slides into the courtroom · **type** : insert

**Caméra** (jamais à l'arrêt, + dérive à l'épaule) :

- 20.94 s · wide · 68 mm · fast dolly down the aisle as people run · vise office
- 23.14 s · insert · 40 mm · rack to the printer spitting the invoice · vise printer
- 25.74 s · insert · 40 mm · tilt down the unrolling invoice · vise invoice $5,000,000

**Actions** :

- **panic** (dev, images 628–688) : developers jump up, headsets fly, coffee spills — *m:react/fury and m:run/A for extras*
  - micro : headset cable snaps back
  - réactions : coffee stream with the right thickness pours off the desk, splash where it lands, spreading puddle; red alarm starts spinning
  - conséquences qui restent : coffee puddle on the floor, chairs left spinning
  - sons : alarm; gasps
- **invoice** (invoice, images 694–772) : the printer prints a 3-metre invoice DAMAGE $5,000,000 — *paper mesh unrolling (keyed)*
  - micro : paper curls at the end
  - réactions : paper feeds out line by line, curls and unrolls over the edge onto the floor; the clock hands spin fast
  - conséquences qui restent : the long invoice lies across the floor
  - sons : printer screech; paper rustle
- **phones_ring** (dev, images 652–694) : every desk phone in the office lights up and rings at once — *phone emissions keyed in a wave down the aisle*
  - micro : handsets rattle in their cradles
  - réactions : the phone screens light up with a flicker one after another down the aisle
  - conséquences qui restent : the lights stay blinking
  - sons : phones ringing; chatter
- **faint** (dev, images 730–772) : a developer reads the total and faints back into his chair — *m:fall/A into the chair*
  - micro : legs kick up
  - réactions : chair rolls back into a desk, a mug wobbles
  - conséquences qui restent : he stays slumped, chair against the desk
  - sons : thud; chair roll

**Entrées / sorties / changements d'état** : invoice : printer -> floor (par invoice)

**Effets** : red alarm sweep; papers flying · **ambiance sonore** : office alarm, phones ringing

### S06 — court_hospital (25.74 → 32.24 s), warm court -> cold hospital

> But the court said he wasn't fit to stand trial, so instead of prison, he was locked in a secure hospital, maybe for life.

**Entrée** : invoice slide · **sortie** : door slam to black, then light (whip) · **type** : close

**Caméra** (jamais à l'arrêt, + dérive à l'épaule) :

- 25.74 s · medium · 50 mm · slow push to the bench · vise judge
- 28.14 s · insert · 40 mm · insert on the gavel hit and the stamp · vise gavel + file
- 29.34 s · wide · 68 mm · slow track down the white corridor · vise secure door
- 32.24 s · close · 42 mm · push in as the door closes · vise door window with his face

**Actions** :

- **gavel** (judge, images 844–862) : the judge brings the gavel down — *m:hammer/A*
  - micro : wig bounces
  - réactions : anticipation lift then a hard hit: papers jump on the bench; camera kick on the hit
  - conséquences qui restent : file stamped INDEFINITE, a dent in the sound block
  - sons : gavel bang
- **door_close** (secure_door, images 892–967) : the heavy secure door swings shut, he looks out through the small window — *hinge keys with overshoot*
  - micro : lock bolt slides
  - réactions : the door swings on its hinge (ease out, small overshoot); the light from the corridor narrows on his face, dust swirls
  - conséquences qui restent : the door stays shut and locked, his face behind the glass
  - sons : heavy door; lock clunk
- **wave** (kid, images 928–967) : behind the glass he gives a tiny awkward wave — *m:wave/A small*
  - micro : fingers only
  - réactions : his breath fogs the glass
  - conséquences qui restent : a fog patch stays on the window
  - sons : squeak on glass

**Entrées / sorties / changements d'état** : kid : court -> behind the hospital door (par door_close)

**Effets** : dust in the window shafts · **ambiance sonore** : court murmur, hospital hum

### S07 — billboard (32.24 → 39.72 s), purple dusk

> And the leak didn't kill the game. A year later, the real trailer became the most watched non-music video on YouTube in a single day.

**Entrée** : whip from the door window · **sortie** : counter blur -> doctor's office · **type** : insert

**Caméra** (jamais à l'arrêt, + dérive à l'épaule) :

- 32.24 s · wide · 68 mm · low crane up the crowd to the billboard · vise billboard
- 35.44 s · insert · 40 mm · push into the racing digits · vise counter digits
- 39.72 s · medium · 50 mm · orbit the crowd as the record trophy rises · vise crowd faces + trophy

**Actions** :

- **counter** (counter, images 997–1132) : the view counter races to 90,421,491 — *decal swap per frame range (the display is the action)*
  - micro : digits blur
  - réactions : the number changes on every beat and flashes at 90,421,491; the crowd raises phones; confetti cannons fire on the record
  - conséquences qui restent : the final number stays on screen: 90,421,491 + WORLD RECORD plaque
  - sons : digit ticking; crowd cheer
- **cheer** (gamer, images 1132–1192) : the crowd cheers, phones up, confetti — *m:cheer/A with offsets*
  - micro : random timing per person
  - réactions : fans stand up, arms up, flags wave, confetti
  - conséquences qui restent : confetti stays on the ground
  - sons : cheer; confetti pop
- **trophy** (counter, images 1147–1192) : a giant record trophy rises from the billboard base — *trophy keyed rise with a bounce*
  - micro : sparkle glints
  - réactions : spotlights swing onto it
  - conséquences qui restent : the trophy stays lit
  - sons : fanfare

**Entrées / sorties / changements d'état** : counter : 0 -> 90,421,491 (par counter)

**Effets** : confetti; billboard light on faces · **ambiance sonore** : square crowd, dusk city

### S08 — doctor_prison (39.72 → 44.88 s), grey prison

> Then this year, doctors decided he was fit for trial after all, and he was moved back to prison.

**Entrée** : counter blur · **sortie** : cell door slam · **type** : extreme_close

**Caméra** (jamais à l'arrêt, + dérive à l'épaule) :

- 39.72 s · insert · 40 mm · top-down on the file, the stamp comes in · vise file on desk
- 41.52 s · extreme_close · 40 mm · snap push to his shocked face · vise kid face
- 44.88 s · medium · 50 mm · pull back as the cell door slides shut · vise cell door

**Actions** :

- **stamp** (doctor, images 1201–1237) : the doctor stamps FIT FOR TRIAL — *m:hammer/B*
  - micro : glasses slide down
  - réactions : anticipation lift then a hard hit: ink splat, pen jumps
  - conséquences qui restent : the file stays stamped FIT FOR TRIAL, ink mark
  - sons : stamp thump
- **shock** (kid, images 1246–1288) : his eyes pop out, sweat drop — *m:idle/B k:shocked*
  - micro : tremble
  - réactions : the face changes on 'fit' to an exaggerated drawing (eyes pop) with a head pop; a world effect answers: the lamp flickers, papers fly off the desk
  - conséquences qui restent : the effect fades but marks stay: papers on the floor, sweat drop until the end of the shot
  - sons : sting
- **cell** (kid, images 1294–1346) : the cell door slides shut on him — *door keys*
  - micro : bars rattle
  - réactions : the barred door slides on its rail (ease out, small overshoot); light changes through the bars, bar shadows sweep across him, dust swirl
  - conséquences qui restent : the door stays shut, he is inside the cell
  - sons : metal slam

**Entrées / sorties / changements d'état** : kid : hospital -> cell (par cell)

**Effets** : sweat drop; bar shadows · **ambiance sonore** : office tick, prison echo

### S09 — shop_street (44.88 → 48.82 s), neon night

> And just three days before GTA 6 finally came out, he pleaded guilty.

**Entrée** : cell door slam -> calendar flip · **sortie** : the queue's phones -> the cell · **type** : insert

**Caméra** (jamais à l'arrêt, + dérive à l'épaule) :

- 44.88 s · insert · 40 mm · insert on the calendar pages tearing NOV 16 -> NOV 19 · vise calendar
- 46.48 s · wide · 68 mm · low tracking along the queue in the rain · vise queue + shop window '6'
- 48.82 s · insert · 40 mm · push into a phone showing the headline 'PLEADS GUILTY' · vise gamer's phone: headline

**Actions** :

- **calendar** (calendar, images 1346–1394) : calendar pages tear off from NOV 16 to NOV 19 — *page meshes peel off (keyed)*
  - micro : pages flutter
  - réactions : the number changes on each tear 16 -> 17 -> 18 -> 19 and the page flashes; torn pages drift down
  - conséquences qui restent : the final number stays on screen: NOV 19; pages stay on the floor
  - sons : paper rips
- **umbrella** (gamer, images 1436–1466) : a gust flips a gamer's umbrella inside out — *umbrella keyed flip*
  - micro : he clings to it
  - réactions : rain sprays on the queue
  - conséquences qui restent : the broken umbrella stays inside out
  - sons : whoosh; snap
- **queue** (gamer, images 1394–1465) : gamers queue in the rain for the game; one reads the guilty plea headline on his phone — *m:wait/A, m:phone/A*
  - micro : breath steam; shiver
  - réactions : rain splashes on hoods; puddles ripple
  - conséquences qui restent : wet hoodies, puddles
  - sons : rain; chatter

**Entrées / sorties / changements d'état** : calendar : NOV 16 -> NOV 19 (par calendar)

**Effets** : rain; neon reflections · **ambiance sonore** : rain, street

### S10 — doctor_prison (48.82 → 54.38 s), grey prison

> So the guy who showed the world GTA 6 first will probably be the last one to play it.

**Entrée** : the queue's phones -> the cell · **sortie** : loop: the switched-off cell TV -> the hotel TV of frame 1 · **type** : close

**Caméra** (jamais à l'arrêt, + dérive à l'épaule) :

- 48.82 s · medium · 50 mm · slow push in · vise kid on the bunk
- 51.82 s · close · 42 mm · push into the black screen: his reflection · vise the small TV, off
- 54.38 s · extreme_close · 40 mm · the reflection becomes the hotel TV of frame 1 (loop) · vise black screen

**Actions** :

- **sigh** (kid, images 1465–1555) : sits on the bunk, sighs at the dead little TV — *m:react/sigh*
  - micro : shoulders drop
  - réactions : the face changes ON the word 'last' with a head pop; the body answers the face: he slumps, shoulders down; dust lifts from the mattress
  - conséquences qui restent : the emotion stays: he stays slumped
  - sons : sigh; springs creak
- **tv_dead** (cell_tv, images 1555–1631) : he presses the TV button: nothing, just his reflection — *m:button/A + TV stays off*
  - micro : button clicks twice
  - réactions : the button dips under the finger, a tiny spark, then nothing
  - conséquences qui restent : the device stays stubbornly off: the TV stays black with his reflection
  - sons : click click; tiny fizz
- **neighbour** (gamer, images 1510–1555) : from the next cell, game sounds and a cheer: someone else is already playing — *off-screen sound + light flicker on the wall*
  - micro : light flickers
  - réactions : coloured TV light from the next cell dances on his wall
  - conséquences qui restent : the light keeps flickering
  - sons : game music muffled; cheer

**Entrées / sorties / changements d'état** : kid : already in the cell (S08 cell action) (par cell)

**Effets** : dust motes; reflection · **ambiance sonore** : prison echo, distant TV from another cell (game sounds)

## Son

- Musique : light, mischievous bed (pizzicato + synth bass), -7.6 dB under the voice, a drop on the twist (line 7) and a sting on the punchline
- Mixage : -14 LUFS ; un bruitage par action et par réaction (listés ci-dessus)

## Leçons appliquées

- PI-016
- PI-017
- PI-018
- PI-019

## Risques

- the game must never look like Rockstar's assets: generic blurred screens only
- the sentence on 23/11 may change the last line: re-check before publishing
- many interiors at night: watch noise at 12 samples -> denoise on, check key frames
- cards in small rooms: keep one view per character, anchors for held props (phone, keyboard, stick)

## Avertissements du contrôle gardés (avec leur raison)

- **recipe vs plan wording** : the matcher compares the first words of each recipe line; the remaining 'maybe forgotten' lines were read one by one: either covered in other words (fall, gust, gesture, LED) or not relevant to this action (a TV that stays OFF does not light up; typing is not a door)
- **no recipe for clips_fly / pigeon / trophy / neighbour** : new actions of this film: their recipes are written to library/reactions/reactions.json after they are built (rule: every new action becomes a recipe)

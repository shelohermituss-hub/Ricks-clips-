# L'ARMÉE FANTÔME — story bible v1 (cast, places, hero objects, light, camera, sound)

## Camera idea (one idea for the whole film)
**"Le faux qui se révèle" (the reveal pull-back).** Each chapter opens on something that looks real and powerful (a tank barrel, a rumbling column, a Morse key, a whisper), framed tight and heroic, then the camera slides or pulls back to show the trick behind it (the air pump, the speaker, the copying operator, the fake patch). The audience is fooled first, exactly like the enemy.
Signature move: line 14, a single long crane rises above the river: south, the inflated decoy field under shell bursts; it keeps rising and swings north to the real army crossing in silence on pontoons. One take, about 4 s.

## Cast (2D vector puppets, kit cast; outfits from the 1940s library)
| Role | Look and costume (period check 1944) | Personality and signature |
|---|---|---|
| **Lou, the hero** (young artist-soldier, the face of the unit) | M1 helmet with a paint smear, olive-drab field jacket, rolled sleeves, sketchbook in the thigh pocket, pencil behind the ear | playful, proud of every fake; signature: wink + pencil twirl |
| The three carriers | same uniform, one tall, one stocky, one tiny | effortless lifting, bored like movers |
| Two French cyclists | old farmer in a beret and blue work jacket; a boy of about 10 in shorts and a flat cap | jaws drop; the boy salutes, the old man crosses himself |
| **The sergeant (the mocker)** | real armored-division tanker: tanker helmet, goggles, cigar, grease on his cheek | gruff, laughs at the artists; payoff: open-mouthed at the river |
| Sound operator | headphones, sleeves up, beside a big disc turntable on the half-track | concentration, a finger raised for silence |
| Radio operator | headphones, Morse key, a card pinned up with the "fist" pattern of the real operator | copies the rhythm with his tongue out |
| Café spy | civilian in a raincoat, hat low, pretends to read a newspaper with a hole in it | sly, scribbles notes |
| Waitress | apron, tray of coffees | rolls her eyes |
| Enemy photo interpreter | grey uniform, magnifying loupe over aerial photos | smug as he counts tanks, then orders fire |
| The grandchild (last scene) | child of today in a hoodie | wonder, lifts the rubber skin |
| The old veteran (last scene) | Lou at about 75, cardigan, same wink | finger to the lips: "chut" |

## Places (one connected world where possible; at least 5 kinds of light, see the gate "share of the most used light <= 75 %")
| # | Place | Light | Story job | Dressing (real models first: Asset Hub) |
|---|---|---|---|---|
| P1 | Normandy hedgerow field (bocage) | dawn, gold, low mist | hook: the tank lifted like a suitcase | hedgerows, apple trees, stone farm, dirt road, cows far away, telegraph poles |
| P2 | The ghost camp in a meadow | overcast day | the world: painters inflate an army | rows of half-inflated tanks, air compressors, paint pots, stencils, a bulldozer drawing tracks |
| P3 | Country road at night | moonlit night, blue | one half-track = a hundred tanks | half-track with a giant speaker, 16-inch discs, poplars, tank silhouettes |
| P4 | Radio tent | interior, warm lamp | copying the Morse "fist" | field radio, Morse key, maps, cigarette smoke |
| P5 | Village café | interior, warm tungsten | fake patches and fake secrets | zinc bar, posters, bicycles outside, accordion on a chair |
| P6 | Enemy photo-interpretation room | cold interior, light table | the enemy counts the fakes | light table, aerial photos, pins, a map of the river |
| P7 | The great river (Rhine) | night, storm of shell flashes (south) / quiet moon (north) | the big trick and the payoff | decoy field, shell bursts, pontoons, real tanks crossing, river mist |
| P8 | A child's bedroom (the analogy) | moonlight through a window | the pillow-under-the-blanket picture | bed, pillow under the blanket, open window, rope of sheets |
| P9 | An attic today | warm afternoon, dust motes | the last-line twist and the loop | trunk, medal box (Congressional Gold Medal), the folded rubber skin, old photos |

## Hero objects (built first, story marks)
1. **The inflatable Sherman**: rubberized canvas over air tubes, a visible valve and patch repair, slight sag and wrinkles, a stenciled false unit number. From 400 m: perfect. Up close: it dents when a hand presses it.
2. **The sound half-track (M3)**: a huge speaker cone on a turret, cables, a 16-inch transcription disc turntable, "SONIC" crate.
3. **The fake shoulder patch**: embroidered, needle and thread, a box full of different patches.
4. **The Morse key + the "fist" card**: the real operator's rhythm drawn as dots and dashes like a fingerprint.
5. **The aerial photo**: grain, tank shapes, fake track marks drawn by the bulldozer.
6. **The trunk in the attic**: the deflated tank skin, an old sketchbook, the medal.

## Look (colour from day one, CB_RULES 11c)
Saturation of the ungraded frames >= 0.36; a clearly different colour world per light kind; night never darker than mean 0.31; ONE red in the whole film: the café's red awning (or the sergeant's cigar ember); faces white by day.
**Sharpness: wide and medium shots fully sharp; only close-ups get a mild soft background; characters never blur (CB_RULES line 82).** `film.json "post": { "dof": 0 }`, `"dof"` only on close-up stations.

## Sound (sound designer, from sound_events.json)
Dawn birds and a distant cow (P1); compressor hiss and rubber squeaks (P2); the half-track speaker: tank engines, tracks, shouted orders, recorded-disc crackle (P3); Morse beeps (P4); café chatter, cups, accordion (P5); shell whistles, far explosions vs river silence and paddle splashes (P7); creaking attic floor, a music box (P9). Music: a playful 1940s swing (clarinet, brushes) that turns into a quiet piano for the last line.

# Frame checks: le-dernier-phare/film.json

0 FAIL, 0 WARN, 17 PASS. 137 of 240 frames checked (camera rests: f0-9, f109-129), cast lina, 8.8 s.
Numbers: head_cut = % of head+hat inside the frame (100 = whole). body_side = % of the figure's width inside the frame. face_covered = face rays (head centre, two eyes) blocked by set geometry. feet = cm between the foot and the surface below (+ floats, - inside). body_in_mesh = % of the body (neck to sole) inside a solid set part (counter, table, tub, chair, cart).

| result | who | rest | check | number | worst at | bad frames | what | crop |
|---|---|---|---|---|---|---|---|---|
| PASS | lina | f0-9 | body_in_mesh | 0 % | f0 | 0/10 |  |  |
| PASS | lina | f0-9 | body_side | 100 % | f0 | 0/10 |  |  |
| PASS | lina | f0-9 | head_cut | 100 % | f0 | 0/10 |  |  |
| PASS | lina | f0-9 | face_covered | 0 rays | f0 | 0/10 |  |  |
| PASS | lina | f0-9 | feet | 0 cm | f0 | 0/10 | on ledge |  |
| PASS | lina | f10-108 move | body_in_mesh | 0 % | f10 | 0/50 |  |  |
| PASS | lina | f109-129 | body_in_mesh | 0 % | f109 | 0/21 |  |  |
| PASS | lina | f109-129 | body_side | 100 % | f109 | 0/21 |  |  |
| PASS | lina | f109-129 | head_cut | 100 % | f109 | 0/21 |  |  |
| PASS | lina | f109-129 | face_covered | 0 rays | f109 | 0/21 |  |  |
| PASS | lina | f109-129 | feet | 0 cm | f113 | 0/21 | on ledge |  |
| PASS | lina | f130-238 move | body_in_mesh | 0 % | f130 | 0/55 |  |  |
| PASS | lina | f239 (last) | body_in_mesh | 0 % | f239 | 0/1 |  |  |
| PASS | lina | f239 (last) | body_side | 100 % | f239 | 0/1 |  |  |
| PASS | lina | f239 (last) | head_cut | 100 % | f239 | 0/1 |  |  |
| PASS | lina | f239 (last) | face_covered | 0 rays | f239 | 0/1 |  |  |
| PASS | lina | f239 (last) | feet | 0 cm | f239 | 0/1 | on ledge |  |

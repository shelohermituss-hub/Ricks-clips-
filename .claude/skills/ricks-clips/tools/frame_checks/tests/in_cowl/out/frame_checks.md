# Frame checks: in_cowl/film.json

12 FAIL, 2 WARN, 57 PASS. 267 of 356 frames checked (camera rests: f47-62, f96-127, f184-205, f222-283, f298-331), cast mathematician, chief, rivets, 60.9 s.
Numbers: head_cut = % of head+hat inside the frame (100 = whole). body_side = % of the figure's width inside the frame. face_covered = face rays (head centre, two eyes) blocked by set geometry. feet = cm between the foot and the surface below (+ floats, - inside). body_in_mesh = % of the body (neck to sole) inside a solid set part (counter, table, tub, chair, cart).

| result | who | rest | check | number | worst at | bad frames | what | crop |
|---|---|---|---|---|---|---|---|---|
| FAIL | mathematician | f96-127 | body_in_mesh | 16 % | f97 | 32/32 | inside bomber_old_faithful/bomber_airframe/engine_cylinder_23: torso-hips-thighs 18 %, legs 0 %, 9 cm of it in front of the card, 7 cm behind; cuts 70 % of the body width with 9 cm of engine_cylinder_22 running on behind the body (+3 more parts) | [crop](frame_checks/FAIL_body_in_mesh_mathematician_f00097.jpg) |
| FAIL | mathematician | f96-127 | face_covered | 3 rays | f107 | 32/32 | head centre INSIDE bomber_old_faithful/bomber_airframe/engine_push_rod_21; in front: bomber_old_faithful/bomber_airframe/engine_ignition_ring_03 | [crop](frame_checks/FAIL_face_covered_mathematician_f00107.jpg) |
| FAIL | mathematician | f96-127 | feet | -46.2 cm | f111 | 32/32 | 2 of 2 feet sunk, nearest bomber_old_faithful/bomber_airframe/cowl_rear_03 | [crop](frame_checks/FAIL_feet_mathematician_f00111.jpg) |
| FAIL | chief | f184-205 | body_side | 50 % | f184 | 22/22 | cut by the right edge | [crop](frame_checks/FAIL_body_side_chief_f00184.jpg) |
| FAIL | chief | f184-205 | head_cut | 30 % | f195 | 22/22 | cut by the right edge | [crop](frame_checks/FAIL_head_cut_chief_f00195.jpg) |
| FAIL | mathematician | f1-46 move | body_in_mesh | 59 % | f31 | 16/16 | inside bomber_old_faithful/bomber_airframe/cowl_rear_03: torso-hips-thighs 66 %, legs 0 %, 43 cm of it in front of the card, 109 cm behind; cuts 100 % of the body width with 102 cm of cowl_rear_03 running on behind the body (+2 more parts) | [crop](frame_checks/FAIL_body_in_mesh_mathematician_f00031.jpg) |
| FAIL | chief | f47-62 | body_side | 80 % | f57 | 12/16 | cut by the right edge | [crop](frame_checks/FAIL_body_side_chief_f00057.jpg) |
| FAIL | mathematician | f128-183 move | body_in_mesh | 82 % | f144 | 11/19 | inside bomber_old_faithful/bomber_airframe/cowl_rear_03: torso-hips-thighs 87 %, legs 0 %, 27 cm of it in front of the card, 104 cm behind; cuts 100 % of the body width with 113 cm of cowl_rear_03 running on behind the body | [crop](frame_checks/FAIL_body_in_mesh_mathematician_f00144.jpg) |
| FAIL | mathematician | f63-95 move | body_in_mesh | 100 % | f81 | 8/8 | inside bomber_old_faithful/bomber_airframe/cowl_rear_03: torso-hips-thighs 100 %, legs 0 %, 22 cm of it in front of the card, 128 cm behind; cuts 100 % of the body width with 122 cm of cowl_rear_03 running on behind the body | [crop](frame_checks/FAIL_body_in_mesh_mathematician_f00081.jpg) |
| FAIL | mathematician | f0 (first) | body_in_mesh | 33 % | f0 | 1/1 | inside bomber_old_faithful/bomber_airframe/cowl_rear_03: torso-hips-thighs 38 %, legs 0 %, 39 cm of it in front of the card, 123 cm behind; cuts 47 % of the body width with 114 cm of cowl_rear_03 running on behind the body (+3 more parts) | [crop](frame_checks/FAIL_body_in_mesh_mathematician_f00000.jpg) |
| FAIL | mathematician | f0 (first) | face_covered | 3 rays | f0 | 1/1 | head centre INSIDE bomber_old_faithful/bomber_airframe/engine_cylinder_21; in front: bomber_old_faithful/bomber_airframe/cowl_polished_band_03 | [crop](frame_checks/FAIL_face_covered_mathematician_f00000.jpg) |
| FAIL | mathematician | f0 (first) | feet | -46.3 cm | f0 | 1/1 | 2 of 2 feet sunk, nearest bomber_old_faithful/bomber_airframe/cowl_rear_03 | [crop](frame_checks/FAIL_feet_mathematician_f00000.jpg) |
| WARN | chief | f298-331 | body_side | 75 % | f331 | 3/34 | cut by the right edge (only 3 frames: WARN) |  |
| WARN | chief | f298-331 | head_cut | 92 % | f331 | 2/34 | cut by the right edge (only 2 frames: WARN) |  |
| PASS | mathematician | f0 (first) | body_side | 100 % | f0 | 0/1 |  |  |
| PASS | mathematician | f0 (first) | head_cut | 100 % | f0 | 0/1 |  |  |
| PASS | chief | f0 (first) | body_in_mesh | 0 % | f0 | 0/1 |  |  |
| PASS | chief | f0 (first) | body_side | 100 % | f0 | 0/1 |  |  |
| PASS | chief | f0 (first) | head_cut | 100 % | f0 | 0/1 |  |  |
| PASS | chief | f0 (first) | face_covered | 0 rays | f0 | 0/1 |  |  |
| PASS | chief | f0 (first) | feet | 0 cm | f0 | 0/1 | on apron_concrete |  |
| PASS | rivets | f0 (first) | body_in_mesh | 0 % | f0 | 0/1 |  |  |
| PASS | rivets | f0 (first) | body_side | 99 % | f0 | 0/1 |  |  |
| PASS | rivets | f0 (first) | head_cut | 100 % | f0 | 0/1 |  |  |
| PASS | rivets | f0 (first) | face_covered | 0 rays | f0 | 0/1 |  |  |
| PASS | rivets | f0 (first) | feet | 0 cm | f0 | 0/1 | on apron_concrete |  |
| PASS | chief | f1-46 move | body_in_mesh | 0 % | f1 | 0/24 |  |  |
| PASS | rivets | f1-46 move | body_in_mesh | 0 % | f1 | 0/18 |  |  |
| PASS | chief | f47-62 | body_in_mesh | 0 % | f47 | 0/16 |  |  |
| PASS | chief | f47-62 | head_cut | 100 % | f47 | 0/16 |  |  |
| PASS | chief | f47-62 | face_covered | 0 rays | f47 | 0/16 |  |  |
| PASS | rivets | f47-62 | body_side | 2 % | f47 | 0/6 | cut by the right edge |  |
| PASS | chief | f63-95 move | body_in_mesh | 0 % | f63 | 0/10 |  |  |
| PASS | mathematician | f96-127 | body_side | 100 % | f96 | 0/32 |  |  |
| PASS | mathematician | f96-127 | head_cut | 100 % | f96 | 0/32 |  |  |
| PASS | chief | f128-183 move | body_in_mesh | 0 % | f138 | 0/24 |  |  |
| PASS | rivets | f128-183 move | body_in_mesh | 0 % | f142 | 0/10 |  |  |
| PASS | chief | f184-205 | body_in_mesh | 0 % | f184 | 0/22 |  |  |
| PASS | chief | f184-205 | face_covered | 0 rays | f184 | 0/22 |  |  |
| PASS | chief | f206-221 move | body_in_mesh | 0 % | f206 | 0/9 |  |  |
| PASS | mathematician | f206-221 move | body_in_mesh | 0 % | f216 | 0/4 |  |  |
| PASS | rivets | f206-221 move | body_in_mesh | 0 % | f218 | 0/3 |  |  |
| PASS | mathematician | f222-283 | body_in_mesh | 0 % | f222 | 0/62 |  |  |
| PASS | mathematician | f222-283 | body_side | 100 % | f222 | 0/62 |  |  |
| PASS | mathematician | f222-283 | head_cut | 100 % | f222 | 0/62 |  |  |
| PASS | mathematician | f222-283 | face_covered | 0 rays | f222 | 0/62 |  |  |
| PASS | mathematician | f222-283 | feet | 0 cm | f222 | 0/62 | on apron_concrete |  |
| PASS | chief | f222-283 | body_in_mesh | 0 % | f222 | 0/62 |  |  |
| PASS | chief | f222-283 | body_side | 100 % | f222 | 0/62 |  |  |
| PASS | chief | f222-283 | head_cut | 100 % | f222 | 0/62 |  |  |
| PASS | chief | f222-283 | face_covered | 0 rays | f222 | 0/62 |  |  |
| PASS | rivets | f222-283 | body_in_mesh | 0 % | f222 | 0/62 |  |  |
| PASS | rivets | f222-283 | body_side | 100 % | f222 | 0/62 |  |  |
| PASS | rivets | f222-283 | head_cut | 100 % | f222 | 0/62 |  |  |
| PASS | rivets | f222-283 | face_covered | 0 rays | f222 | 0/62 |  |  |
| PASS | rivets | f222-283 | feet | 0 cm | f222 | 0/62 | on apron_concrete |  |
| PASS | chief | f222-283 | feet | 0 cm | f270 | 0/62 | on apron_concrete |  |
| PASS | mathematician | f284-297 move | body_in_mesh | 0 % | f284 | 0/8 |  |  |
| PASS | chief | f284-297 move | body_in_mesh | 0 % | f284 | 0/8 |  |  |
| PASS | rivets | f284-297 move | body_in_mesh | 0 % | f284 | 0/5 |  |  |
| PASS | mathematician | f298-331 | body_in_mesh | 0 % | f298 | 0/34 |  |  |
| PASS | mathematician | f298-331 | body_side | 100 % | f298 | 0/34 |  |  |
| PASS | mathematician | f298-331 | head_cut | 100 % | f298 | 0/34 |  |  |
| PASS | mathematician | f298-331 | face_covered | 0 rays | f298 | 0/34 |  |  |
| PASS | chief | f298-331 | body_in_mesh | 0 % | f298 | 0/34 |  |  |
| PASS | chief | f298-331 | face_covered | 0 rays | f298 | 0/34 |  |  |
| PASS | mathematician | f298-331 | feet | 0 cm | f301 | 0/34 | on apron_concrete |  |
| PASS | chief | f298-331 | feet | 0 cm | f330 | 0/34 | on apron_concrete |  |
| PASS | mathematician | f332-354 move | body_in_mesh | 0 % | f332 | 0/4 |  |  |
| PASS | chief | f332-354 move | body_in_mesh | 0 % | f332 | 0/5 |  |  |
| PASS | rivets | f332-354 move | body_in_mesh | 0 % | f340 | 0/1 |  |  |

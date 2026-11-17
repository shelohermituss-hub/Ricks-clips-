# Film check: final.mp4

19 gates: 15 pass, 2 warn, 2 fail. 8.0 s.

| | Gate | Value | Target | Fix |
|-|-|-|-|-|
| PASS | camera: camera at rest (< 2 px/f), % of frames | 80.26 | >= 30 (Rick median 32) [Rick 5.65-58.02] |  |
| PASS | camera: rests per 10 s | 3.77 | 2.2-3.8, aim 3 (Rick median 3.1; Railroads 2.5, Roller Coasters 2.7) [Rick 0.87-4.74] |  |
| PASS | camera: rest length median, s | 2.23 | >= 0.6 (Rick 0.62) [Rick 0.37-1.28] |  |
| FAIL | camera: travel length p90, s | 0.81 | 2.1-6.3 (Rick median 3.0; Railroads and Roller Coasters 4.7). CB 2026-11-10: the scene decides, but some moves must flow [Rick 1.73-9.52] | under 2.1: every move is a short hop, let one or two moves follow something through the set for 4-5 s; over 6.3: insert a rest inside the longest moves |
| FAIL | camera: speed median, px/f | 1.21 | about 4 (Rick 4.1) [Rick 1.55-14.11] | too high: slow down, rest more; too low: add creep to the rests |
| PASS | camera: speed p90, px/f | 16.65 | <= 25 (Rick 23) [Rick 9.80-33.84] |  |
| PASS | camera: cuts per 10 s | 0.0 | <= 0.9, aim 0.4 [Rick 0.00-2.50] |  |
| WARN | camera: roll rate p99, deg/f | 1.81 | <= 1.1 (Rick 1.08) [Rick 0.26-3.02] | smaller or slower dutch moves |
| PASS | camera: whips per minute | 0.0 | <= 10 (Rick 5.8) [Rick 0.00-11.77] |  |
| PASS | camera: camera at rest on long words, % | 62.5 | >= 30 (Rick 33; CB: nouns land at rest) [Rick 2.38-52.87] |  |
| PASS | camera: voice pace, words per second | 3.95 | 3.5-4.5 (Rick 3.7) [Rick 3.36-4.06] |  |
| PASS | camera: camera dead still (< 0.3 px/f), % of frames | 11.59 | <= 21, aim 9 (Rick 9.3) [Rick 1.16-28.76] |  |
| PASS | scan: frozen spans (camera and picture still 12+ f) | 0 | 0: every long hold has a creep or something moving |  |
| PASS | scan: travels longer than 7 s | 0 | 0 (a flowing move of 3-7 s is wanted since 2026-11-10; Rick's long travels reach 4.8-9.5 s) |  |
| PASS | scan: one-frame flashes or A-B-A flickers | 0 | 0 unplanned (planned flashes and washes are fine: confirm each) |  |
| PASS | scan: picture jumps the plan does not explain (not a planned cut, mood change, effect or kick) | 0 | 0 |  |
| PASS | plan: rest share: plan 70 % vs picture 80 % | 9.8 | within 12 points |  |
| PASS | plan: plan gates failing (tools/film_plan.py check) | 0 | 0 |  |
| WARN | faces: visibility.json | missing | render with the three.js kit: node render.mjs film.json --visibility | face and caption gates were skipped |

Manual, every draft: sound-off test (does each face tell the story muted?); three-point shot check (face changes on its word, key event and its sound land on their word, nothing blocks the face); judge agent score 8.5+ per storyboard panel.

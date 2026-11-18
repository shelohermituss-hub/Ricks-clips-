# Reference comparison — ghost-army vs the fortress standard (2026-11-18)

Video: `episodes/ghost-army/v3/ghost_army_preview_v3_graded.mp4` (71.23 s). Standard: `production/config/reference_standard.json`, bible `references/REFERENCE_LOOK_BIBLE.md`.

| metric | film | target | reference | status |
|---|---|---|---|---|
| edge_detail | 0.0595 | >= 0.075 (ref 0.095) | 0.095 | **FAIL** |
| luma_day | 0.417 | 0.36-0.5 | 0.433 | **PASS** |
| luma_night | 0.283 | >= 0.25 | - | **PASS** |
| crushed | 0.0005 | <= 0.01 | 0.0007 | **PASS** |
| burned | 0.0001 | <= 0.015 | 0.0055 | **PASS** |
| saturation | 0.505 | 0.32-0.52 (ref 0.4) | 0.4 | **PASS** |
| saturation_seconds_over_max | 8 | 0 s above 0.6 (seconds: [0, 1, 2, 4, 9, 28, 29, 30]) | - | **FAIL** |
| still_frames_pct | 0.3 | <= 2.0 | 0.0 | **PASS** |
| motion_median_x1000 | 12.91 | >= 18.0 (ref 35.8) | 35.8 | **FAIL** |
| peaks_per_10s | 5.47 | >= 6.0 (ref 10.47) | 10.47 | **FAIL** |
| hard_cuts | 3 | 0 unless listed as deliberate in DECISIONS.md (at [42.8, 55.67, 66.43] s) | 0 | **WARN** |

Hard cuts at (s): [42.8, 55.67, 66.43]

Per second: see REFERENCE_COMPARE.json (luma, sat, crushed, burned, motion, edge).

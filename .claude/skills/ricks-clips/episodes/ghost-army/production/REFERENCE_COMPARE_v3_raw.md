# Reference comparison — ghost-army vs the fortress standard (2026-11-18)

Video: `episodes/ghost-army/v3/ghost_army_preview_v3_raw.mp4` (71.23 s). Standard: `production/config/reference_standard.json`, bible `references/REFERENCE_LOOK_BIBLE.md`.

| metric | film | target | reference | status |
|---|---|---|---|---|
| edge_detail | 0.0572 | >= 0.075 (ref 0.095) | 0.095 | **FAIL** |
| luma_day | 0.323 | 0.36-0.5 | 0.433 | **FAIL** |
| luma_night | 0.192 | >= 0.25 | - | **FAIL** |
| crushed | 0.0129 | <= 0.01 | 0.0007 | **FAIL** |
| burned | 0.0008 | <= 0.015 | 0.0055 | **PASS** |
| saturation | 0.685 | 0.32-0.52 (ref 0.4) | 0.4 | **FAIL** |
| saturation_seconds_over_max | 60 | 0 s above 0.6 (seconds: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]) | - | **FAIL** |
| still_frames_pct | 0.6 | <= 2.0 | 0.0 | **PASS** |
| motion_median_x1000 | 10.56 | >= 18.0 (ref 35.8) | 35.8 | **FAIL** |
| peaks_per_10s | 5.33 | >= 6.0 (ref 10.47) | 10.47 | **FAIL** |
| hard_cuts | 2 | 0 unless listed as deliberate in DECISIONS.md (at [42.8, 55.67] s) | 0 | **WARN** |

Hard cuts at (s): [42.8, 55.67]

Per second: see REFERENCE_COMPARE.json (luma, sat, crushed, burned, motion, edge).

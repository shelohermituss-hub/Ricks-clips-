# Reference comparison — ghost-army vs the fortress standard (2026-11-18)

Video: `episodes/ghost-army/v1/ghost_army_preview_v1.mp4` (71.23 s). Standard: `production/config/reference_standard.json`, bible `references/REFERENCE_LOOK_BIBLE.md`.

| metric | film | target | reference | status |
|---|---|---|---|---|
| edge_detail | 0.0465 | >= 0.075 (ref 0.095) | 0.095 | **FAIL** |
| luma_day | 0.292 | 0.36-0.5 | 0.433 | **FAIL** |
| luma_night | 0.104 | >= 0.25 | - | **FAIL** |
| crushed | 0.0647 | <= 0.01 | 0.0007 | **FAIL** |
| burned | 0.001 | <= 0.015 | 0.0055 | **PASS** |
| saturation | 0.717 | 0.32-0.52 (ref 0.4) | 0.4 | **FAIL** |
| saturation_seconds_over_max | 69 | 0 s above 0.6 (seconds: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]) | - | **FAIL** |
| still_frames_pct | 5.3 | <= 2.0 | 0.0 | **FAIL** |
| motion_median_x1000 | 8.11 | >= 18.0 (ref 35.8) | 35.8 | **FAIL** |
| peaks_per_10s | 5.05 | >= 6.0 (ref 10.47) | 10.47 | **FAIL** |
| hard_cuts | 9 | 0 unless listed as deliberate in DECISIONS.md (at [10.6, 26.43, 34.0, 38.7, 46.67, 52.7, 55.67, 61.5, 66.43] s) | 0 | **WARN** |

Hard cuts at (s): [10.6, 26.43, 34.0, 38.7, 46.67, 52.7, 55.67, 61.5, 66.43]

Per second: see REFERENCE_COMPARE.json (luma, sat, crushed, burned, motion, edge).

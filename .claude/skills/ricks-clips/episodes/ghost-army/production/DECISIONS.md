# Decisions — ghost-army

| date | decision | why | who approved |
|---|---|---|---|

## 2026-11-18 — V3 joins between takes (step 8)
- 8 of the 10 joins are now push-throughs and/or 3-6 frame dissolves (film.json "joins", edit/joins.py).
- Two hard cuts are kept ON PURPOSE:
  - **t_sergeant (42.8 s)**: comic cut landing on "sergeant" in the same room; it replaced a travel that cut Lou by the frame edge (v1 note 3).
  - **t_strike (55.7 s)**: shock cut, "every gun" lands on the shelling.
- Camera: the kit's Rick plan gates (>= 30 % of frames at rest, key words landing at rest) and the fortress standard (camera never rests) pull in opposite directions. V3 keeps the kit gates at 0 FAIL (camera_life rest_mult 1.0) and adds life through push-through joins, macro inserts and environment motion (wind grass, rain, pennants). Which standard wins for the rest speed is the user's decision.

## 2026-11-18 — CB: fortress camera rhythm
- CB chose the fortress rhythm (camera never parked) over the Rick rhythm. `film.json` "camera_standard": "fortress" makes `tools/film_plan.py` judge the rest gates on that standard (not switched off: at rest <= 15 %, dead still <= 5 %, rest median <= 1.2 s, key words readable < 12 px/f, faces calm >= 8 %). camera_life rest_mult 2.8, push .0022; push-through strength .22; valve and Morse travels lengthened (peak speed under 60 px/f). Plan: 0 FAIL, 5 WARN.

## 2026-11-18 — CB: restructuring (Mission 0 approved: "Oui vas y")
- Blender is the single engine for worlds and final render; three.js stops building sets and keeps the character drawings (SVG -> PNG card service).
- film.json + film_plan.py stay the timing/camera/performance plan; Blender reads the baked camera and performance.
- Every animated value is baked into the .blend (frame-order independent); every costly step goes through a content cache.
- Render engine (EEVEE vs Cycles) decided by a measured benchmark on the Mission 2 prototype, not by reputation.
- The three.js set code is frozen (no new set work in JS); it stays runnable until the Blender pipeline replaces it.

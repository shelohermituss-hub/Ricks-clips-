# Decisions — ghost-army

| date | decision | why | who approved |
|---|---|---|---|

## 2026-11-18 — V3 joins between takes (step 8)
- 8 of the 10 joins are now push-throughs and/or 3-6 frame dissolves (film.json "joins", edit/joins.py).
- Two hard cuts are kept ON PURPOSE:
  - **t_sergeant (42.8 s)**: comic cut landing on "sergeant" in the same room; it replaced a travel that cut Lou by the frame edge (v1 note 3).
  - **t_strike (55.7 s)**: shock cut, "every gun" lands on the shelling.
- Camera: the kit's Rick plan gates (>= 30 % of frames at rest, key words landing at rest) and the fortress standard (camera never rests) pull in opposite directions. V3 keeps the kit gates at 0 FAIL (camera_life rest_mult 1.0) and adds life through push-through joins, macro inserts and environment motion (wind grass, rain, pennants). Which standard wins for the rest speed is the user's decision.

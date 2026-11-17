# episodes/

One folder per film: `episodes/<name>/film.json`, `voice/`, `sets/`, `cast/`, `out/` (see `FILE_GUIDE.md`).
Example made in the cloud: `episodes/le-dernier-phare/` (validation test, 2026-11-17).

## Source sheets required by `tools/check_views.mjs`

`templates/vector2d_characters/views_golden/rows.json` locks 7 approved characters whose source sheets were not in the
V1.3 archive. They are hand-written cast sheets (custom signature pieces, exact colours) approved by CB and cannot be
rebuilt from the approved pictures. Copy them from the Windows PC to these exact paths, then run `node tools/check_views.mjs`:

| Path | Characters |
|---|---|
| `episodes/baboon-signalman/cast/sheets/jack.mjs` | jack |
| `episodes/goldrush/cast/sheets/goldrush.mjs` | goldrush_shopkeeper |
| `episodes/goldrush/cast/sheets/goldrush2.mjs` | goldrush_clerk, goldrush_miner, goldrush_rival |
| `episodes/goldrush/cast/sheets/goldrush_today.mjs` | goldrush_chipseller, goldrush_customer |

Until then `check_views.mjs` reports FAIL for these 7 rows (on purpose: a missing source is never a pass).

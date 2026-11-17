# RicksClips V1.2 Asset Hub (provider integration shipped with V1.1 maintenance line)

The Asset Hub lets the crew search several sources, cache legally acquired files, retain provenance, validate local packages, and stage resources into an episode. The story remains the authority: the skill must choose environments from the script, not force a stored place into an unrelated story.

## Scope and content boundaries

This helper is intended for environment art and ordinary non-restricted set dressing (architecture, terrain, vegetation, furniture, vehicles, surfaces and atmospheric resources). Its search/import layer blocks weapon and self-defence asset categories. The story-first rule never overrides provider access controls, age/safety rules or licence requirements.

## Provider capability matrix

| Provider | Search | Automated download | Requirements / limits |
|---|---|---|---|
| Sketchfab | Public Data API model search | Yes, for models marked downloadable | User supplies their own OAuth access token as `SKETCHFAB_OAUTH_TOKEN`; automatic downloads are restricted by default to CC0 and CC-BY. No NC, ND, or unknown licence downloads. Preserve author/source/licence metadata. |
| Fab | Official listing search hand-off | No automatic marketplace acquisition | The owner signs into Fab/Fab Launcher, obtains the product under its applicable licence, exports/downloads the local files, then registers the acquired file with `import-local`. Official Fab docs show that free products require accepting the applicable EULA and priced items require purchase; no scraping, account automation, payment, or library bypass. |
| Poly Haven | Public API | Yes | Public API requires a distinct User-Agent and a visible “Powered by Poly Haven” credit when using the live API. Assets are CC0. Textures download as a set of maps where the API exposes them. |
| ambientCG | Public API v3 | Yes | API v3 is used; API v2 is not used for new work. Public downloadable assets are CC0. The API is maintained as a creator-run service and can change; errors are reported without breaking story creation. |
| BlenderKit | Existing logged-in Blender add-on bridge | Yes, through the existing BlenderKit tool | Requires Blender and the user’s logged-in add-on; the existing tool keeps its Royalty Free / CC0 filter. The Asset Hub does not store the add-on's secret. |

## Commands (run from the skill root)

Search across sources (Fab is returned as a manual acquisition link; BlenderKit is included when Blender is on PATH):

```powershell
python tools/asset_hub.py search all "medieval harbor warehouse" --kind model --limit 12
python tools/asset_hub.py search sketchfab "stone lighthouse" --kind model
python tools/asset_hub.py search polyhaven "wet stone" --kind material
python tools/asset_hub.py search ambientcg "weathered stone" --kind material
python tools/asset_hub.py search fab "medieval harbor environment"
```

Download public assets (the asset ID comes from the search result):

```powershell
python tools/asset_hub.py download polyhaven concrete_floor_01 --resolution 2k
python tools/asset_hub.py download ambientcg PavingStones036 --resolution 2K --format zip
```

Sketchfab requires the user's own OAuth token. In the current PowerShell session only:

```powershell
$env:SKETCHFAB_OAUTH_TOKEN = "<YOUR_OWN_OAUTH_ACCESS_TOKEN>"
python tools/asset_hub.py download sketchfab <MODEL_UID>
```

Do not put tokens in the skill, episode files, source control, prompts, manifests, or reports. Clear the variable after work with `Remove-Item Env:SKETCHFAB_OAUTH_TOKEN`.

### Fab local acquisition

Search returns the official Fab listing search URL. Open a listing in Fab, review the exact product licence and formats, add/acquire it through the Epic account, download/export it with Fab or Fab Launcher, then import the local file:

```powershell
python tools/asset_hub.py import-local fab "C:\Assets\my_environment_pack.zip" `
  --name "my_environment_pack" `
  --license "Fab Standard License" `
  --source-url "https://www.fab.com/listings/<LISTING_ID>" `
  --license-url "https://www.fab.com/eula" `
  --creator "<PUBLISHER>" `
  --evidence "Product is in my Fab Library; acquired under the listing's stated licence" `
  --commercial-use "per the applicable Fab licence"
```

The evidence field is a provenance note, not an automated entitlement check. The owner is responsible for verifying that the acquisition and selected licence are valid for the project. Reference-only products are not treated as source assets. Never redistribute a raw asset as a standalone file.

## Cache, provenance and staging

- Cache root: `library/assets/<provider>/<asset_id>/`.
- Every ingested asset gets `ASSET_MANIFEST.json`; the index is `library/assets/catalog.json`.
- Manifest stores provider ID, asset name, creator, exact licence label, source URL, licence URL, acquisition method, file hashes, and download timestamp when available.
- `python tools/asset_hub.py validate library/assets/<provider>/<asset_id>` checks local package structure and basic GLB/glTF validity.
- `python tools/asset_hub.py stage <provider> <asset_id> --episode episodes/<episode>` copies an asset into `episodes/<episode>/assets/asset_hub/`.
- Raw paid/CC assets remain in the local cache; the episode receives only a project copy required for rendering. Keep attribution/provenance in the manifest and include any required credits in project documentation.
- Before delivery, run `python tools/build_asset_credits.py episodes/<episode>`. It writes `ASSET_CREDITS.md` from every staged manifest; use it to put the required Sketchfab attribution and visible Poly Haven credit in the final end credits/player or publication description.

## Reusable places

A reusable location is a recipe, not a hard-coded film. See `templates/place_library/PLACE_MANIFEST.schema.json` and `templates/place_library/abandoned_port.place.json`.

```powershell
python tools/place_library.py register templates/place_library/abandoned_port.place.json
python tools/place_library.py list
python tools/place_library.py stage abandoned_port --episode episodes/<episode>
```

The stage command creates `episodes/<episode>/place_manifests/<place>.film-place-assets.json`. Copy the returned `assets` array into that place's object under `film.json` `places.<place>.assets`. Example:

```json
{
  "places": {
    "harbor": {
      "set": "harbor",
      "light": "golden",
      "assets": [
        {
          "id": "stone_warehouse",
          "provider": "sketchfab",
          "file": "assets/asset_hub/sketchfab/<uid>/gltf/scene.gltf",
          "position": [0, 12, 0],
          "rotationY": 0,
          "scale": 1,
          "required": true
        }
      ]
    }
  }
}
```

Coordinates are film-plan metres `[x, y-forward, z-up]`; rotation is degrees about the plan's vertical axis; scale may be a number or `[x,y,z]`. The renderer applies the plan-to-Three coordinate conversion. Only `.glb` and `.gltf` load at runtime. `.blend`, `.fbx`, `.obj`, USD and texture-only packages must be converted/used in Blender or in the material pipeline first. Missing optional models are logged as warnings; missing required models fail setup.

## Quality gates before approving a place

1. Confirm the listing is relevant to the story and visual bible; do not use a photoreal model if it breaks the intended art direction.
2. Read the complete licence; metadata tags are not legal proof. Exclude non-commercial, no-derivatives, unknown, and reference-only assets from automatic production ingestion.
3. Inspect scale, orientation, origin, normals, UVs, material channels, texture resolution, polycount, LOD and animation.
4. Optimise large models for the target camera; use LOD or separate foreground / midground / background assets.
5. Check GLB/glTF loads under Three.js r165, all textures resolve locally, shadows work, and no hidden dependencies remain.
6. Capture one approved still and a short motion test per new place before using it in a full episode.

### PBR material snippet

A material role in a place manifest must include the exact set material names to change. After `place_library.py stage`, the generated snippet contains the file paths for the maps it can use:

```json
{
  "materials": [
    {
      "id": "weathered_stone",
      "provider": "ambientcg",
      "asset_id": "Concrete001",
      "license": "CC0",
      "maps": {
        "color": "assets/asset_hub/ambientcg/Concrete001/Concrete001_2K_Color.jpg",
        "normal": "assets/asset_hub/ambientcg/Concrete001/Concrete001_2K_NormalGL.jpg",
        "roughness": "assets/asset_hub/ambientcg/Concrete001/Concrete001_2K_Roughness.jpg"
      },
      "target_materials": ["wet_stone"],
      "repeat": [2, 2],
      "normalScale": [1, 1],
      "required": false
    }
  ]
}
```

Place this array under `film.json` `places.<place>.materials`. The loader only changes exact named materials; a missing map/material is logged and a required entry fails place setup. Image formats unsupported by the browser loader (for example EXR/TIFF) are not applied automatically and must be converted first.

## Official provider references

- Sketchfab [Data API v3](https://sketchfab.com/developers/data-api/v3), [Download API](https://sketchfab.com/developers/download-api), [download workflow](https://sketchfab.com/developers/download-api/downloading-models), and [API guidelines](https://sketchfab.com/developers/guidelines).
- Fab [Purchasing and Downloading Assets](https://dev.epicgames.com/documentation/fab/purchasing-and-downloading-assets) and [Licenses and Pricing](https://dev.epicgames.com/documentation/fab/licenses-and-pricing).
- Poly Haven [API documentation and conditions](https://polyhaven.com/our-api).
- ambientCG [API overview](https://docs.ambientcg.com/api/) and [API v3 assets endpoint](https://docs.ambientcg.com/api/v3/assets/).

## Operational limits

- The downloader needs network access in the user's Windows environment. This sandbox build did not have outbound DNS, so tests use mocked provider responses; no real provider downloads were made during packaging.
- Sketchfab download needs an authorized account token. No token is included.
- Fab acquisition requires the owner to download the acquired product locally. No purchase or login is automated.
- BlenderKit download still runs through the existing Blender add-on; no add-on credential is exported by this package.
- The Three.js loader imports `GLTFLoader` from the pinned `three@0.165.0` npm package, matching the vendored `THREE.REVISION=165`. Run `npm install` in `templates/threejs_film` (not `npm ci` against the pre-existing lock file) once, so npm updates `package-lock.json` and installs the loader dependency.
- This sandbox could not fetch npm packages or call live provider APIs (outbound DNS is unavailable here). Run the sample searches on the Windows workstation after installing dependencies to verify network/account access.
- Runtime smoke test (offline): `node tools/test_asset_loader.mjs` checks texture application, exact material targeting, local episode path resolution and format/path guards.

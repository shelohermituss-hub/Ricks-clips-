"""rc — RicksClips production package (Mission 0 architecture, 2026-11-18). Blender is the single engine for worlds and final render.

Modules (letters = the architecture in docs/MISSION_0_ARCHITECTURE_RICKSCLIPS.md):
  cache      (shared) content-addressed persistent cache                       pure Python
  library    B  Asset Library: asset.json metadata, catalogue, build + ingest     index/validate pure Python; ingest/link need Blender
  qa         K  scene statistics: objects, instances, triangles, primitives, textures   Blender
  assemble   D  place.json + baked camera -> scene .blend                          Blender
  render     J  Render Manager: engines, frame ranges, GPU proof, determinism      Blender (+ CLI side)
Entry point inside Blender:  blender -b --python blender/rc/cli.py -- <command> [args]   (see cli.py)
Pure-Python modules import without bpy; Blender-only modules import bpy lazily."""
import os
SKILL = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
VERSION = "0.1.0"

#!/usr/bin/env python3
"""Offline unit/safety tests for RicksClips Asset Hub."""
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

import asset_hub as hub


class AssetHubTests(unittest.TestCase):
    def test_sketchfab_license_allowlist(self):
        self.assertEqual(hub.license_slug({"slug": "by", "label": "CC Attribution"}), "by")
        self.assertIn("cc0", hub.ALLOWED_SKETCHFAB)
        self.assertNotIn("by-nc", hub.ALLOWED_SKETCHFAB)
        self.assertNotIn("by-nd", hub.ALLOWED_SKETCHFAB)

    def test_polyhaven_search_normalizes_and_filters(self):
        data = {
            "old_port": {"name": "Old Port Crane", "description": "weathered dock", "category": "Industrial", "tags": ["port", "crane"], "type": 2, "authors": {"A": "All"}},
            "storm_hdr": {"name": "Storm Harbor", "description": "hdr", "category": "Sky", "tags": ["port"], "type": 0, "authors": {}}
        }
        with patch.object(hub, "api_json", return_value=data):
            rows = hub.search_polyhaven("port", "model", 10)
        self.assertEqual([x["asset_id"] for x in rows], ["old_port"])
        self.assertEqual(rows[0]["license"], "CC0")

    def test_ambientcg_response_normalization(self):
        sample = {"foundAssets": [{"assetId": "Concrete001", "displayName": "Concrete 001", "url": "https://ambientcg.com/view?id=Concrete001"}]}
        with patch.object(hub, "api_json", return_value=sample):
            rows = hub.search_ambientcg("concrete", "material", 5)
        self.assertEqual(rows[0]["asset_id"], "Concrete001")
        self.assertEqual(rows[0]["license"], "CC0")

    def test_recurse_download_entries(self):
        sample = {"2k": {"Color": {"url": "https://cdn.example.test/a.png", "size": 12, "md5": "abc"}}}
        rows = hub.recurse_download_entries(sample)
        self.assertEqual(len(rows), 1)
        self.assertIn("2k", rows[0]["path"])

    def test_model_download_prefers_runtime_gltf(self):
        entries = [
            {"url": "https://cdn.example.test/model.blend", "path": ("blend",), "size": 100},
            {"url": "https://cdn.example.test/model.gltf", "path": ("gltf",), "size": 200},
            {"url": "https://cdn.example.test/model.glb", "path": ("glb",), "size": 300},
        ]
        self.assertTrue(hub.pick_download(entries, "model", "2k", "auto")["url"].endswith("model.glb"))

    def test_archive_path_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            z = Path(td) / "bad.zip"
            with zipfile.ZipFile(z, "w") as f:
                f.writestr("../escape.txt", "no")
            with self.assertRaises(hub.AssetHubError):
                hub.safe_extract(z, Path(td) / "out")

    def test_glb_header_validation(self):
        with tempfile.TemporaryDirectory() as td:
            folder = Path(td)
            (folder / "bad.glb").write_bytes(b"BAD!" + b"\x00" * 12)
            result = hub.validate_directory(folder)
            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(any("invalid GLB" in x for x in result["issues"]))

    def test_place_manifest_rules(self):
        import importlib.util
        path = Path(__file__).with_name("place_library.py")
        spec = importlib.util.spec_from_file_location("place_library_module", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        good = {"schema_version": 1, "place_id": "test_place", "name": "Test", "coordinate_system": "film-plan-metres-x-y-forward-z-up", "visual_direction": {}, "assets": []}
        self.assertEqual(module.validate(good), [])
        bad = dict(good); bad["coordinate_system"] = "unknown"
        self.assertTrue(module.validate(bad))



# Additional integration tests for the provider and reusable-place layer.
class AssetHubIntegrationTests(unittest.TestCase):
    def test_fab_search_is_official_hand_off_not_fake_download(self):
        row = hub.search_fab("old medieval port")[0]
        self.assertTrue(row["source_url"].startswith("https://www.fab.com/search?"))
        self.assertFalse(row["license_allowed_by_default"])
        self.assertEqual(row["acquisition"], "manual_via_epic_account")

    def test_ambientcg_v3_kind_and_search_fields(self):
        sample = {"foundAssets": [{"assetId": "Rock001", "title": "Rock", "type": "3d-model", "downloads": {"zip": "https://cdn.example.test/a.zip"}}]}
        with patch.object(hub, "api_json", return_value=sample) as mocked:
            rows = hub.search_ambientcg("rock", "model", 5)
        self.assertEqual(rows[0]["kind"], "3d-model")
        self.assertTrue(rows[0]["download_metadata_available"])
        self.assertIn("/api/v3/assets?", mocked.call_args.args[0])
        parsed = __import__("urllib.parse", fromlist=["parse_qs"]).parse_qs(__import__("urllib.parse", fromlist=["urlparse"]).urlparse(mocked.call_args.args[0]).query)
        self.assertIn("type", parsed["include"][0].split(","))

    def test_windows_drive_zip_path_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            z = Path(td) / "drive.zip"
            with zipfile.ZipFile(z, "w") as f:
                f.writestr("C:/outside.txt", "no")
            with self.assertRaises(hub.AssetHubError):
                hub.safe_extract(z, Path(td) / "out")

    def test_fab_import_requires_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            source = Path(td) / "test.glb"
            source.write_bytes(b"glTF" + (2).to_bytes(4, "little") + (12).to_bytes(4, "little"))
            with self.assertRaises(hub.AssetHubError):
                hub.import_local("fab", source, "sample", "Fab Standard", "https://www.fab.com/listings/test")

    def test_place_stage_emits_named_pbr_materials(self):
        import importlib.util
        from argparse import Namespace
        from contextlib import redirect_stdout
        import io
        path = Path(__file__).with_name("place_library.py")
        spec = importlib.util.spec_from_file_location("place_library_stage_test", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as td:
            temp = Path(td)
            module.PLACES = temp / "places"
            module.ASSETS = temp / "assets"
            place_dir = module.PLACES / "wet_harbor"
            place_dir.mkdir(parents=True)
            asset_dir = module.ASSETS / "ambientcg" / "Concrete001"
            asset_dir.mkdir(parents=True)
            color = asset_dir / "Concrete001_2K_Color.jpg"; color.write_bytes(b"color")
            normal = asset_dir / "Concrete001_2K_NormalGL.jpg"; normal.write_bytes(b"normal")
            rough = asset_dir / "Concrete001_2K_Roughness.jpg"; rough.write_bytes(b"rough")
            manifest = {"status": "ingested", "provider": "ambientcg", "asset_id": "Concrete001", "kind": "material", "files": [
                {"path": str(color)}, {"path": str(normal)}, {"path": str(rough)}]}
            (asset_dir / "ASSET_MANIFEST.json").write_text(json.dumps(manifest), encoding="utf-8")
            place = {"schema_version": 1, "place_id": "wet_harbor", "name": "Wet harbor", "coordinate_system": "film-plan-metres-x-y-forward-z-up", "visual_direction": {},
                     "assets": [{"provider": "ambientcg", "asset_id": "Concrete001", "role": "material", "license": "CC0", "target_materials": ["wet_stone"], "repeat": [2, 2]}]}
            (place_dir / "place.json").write_text(json.dumps(place), encoding="utf-8")
            episode = temp / "episode"
            with redirect_stdout(io.StringIO()):
                module.cmd_stage(Namespace(place_id="wet_harbor", episode=episode))
            snippet = json.loads((episode / "place_manifests" / "wet_harbor.film-place-assets.json").read_text(encoding="utf-8"))
            self.assertEqual(len(snippet["materials"]), 1)
            self.assertEqual(snippet["materials"][0]["target_materials"], ["wet_stone"])
            self.assertEqual(set(snippet["materials"][0]["maps"]), {"color", "normal", "roughness"})

    def test_restricted_asset_topic_is_blocked(self):
        with self.assertRaises(hub.AssetHubError):
            hub.do_search("all", "restricted weapon asset", "model", 10)

    def test_episode_credits_include_provider_attributions(self):
        import importlib.util
        path = Path(__file__).with_name("build_asset_credits.py")
        spec = importlib.util.spec_from_file_location("asset_credits_test", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as td:
            episode = Path(td)
            asset = episode / "assets" / "asset_hub" / "sketchfab" / "test_uid"
            asset.mkdir(parents=True)
            (asset / "ASSET_MANIFEST.json").write_text(json.dumps({
                "provider": "sketchfab", "asset_id": "test_uid", "name": "Stone warehouse",
                "creator": "Example creator", "license": "CC-BY-4.0",
                "source_url": "https://sketchfab.com/3d-models/test_uid",
                "license_url": "https://creativecommons.org/licenses/by/4.0/"
            }), encoding="utf-8")
            output = module.build_credits(episode)
            content = output.read_text(encoding="utf-8")
            self.assertIn("Sketchfab", content)
            self.assertIn("Example creator", content)
            self.assertIn("CC-BY-4.0", content)
            self.assertIn("test_uid", content)

    def test_material_manifest_requires_named_targets(self):
        import importlib.util
        path = Path(__file__).with_name("place_library.py")
        spec = importlib.util.spec_from_file_location("place_library_validate_test", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        place = {"schema_version": 1, "place_id": "wet_harbor", "name": "Wet harbor", "coordinate_system": "film-plan-metres-x-y-forward-z-up", "visual_direction": {},
                 "assets": [{"provider": "ambientcg", "asset_id": "Concrete001", "role": "material", "license": "CC0"}]}
        self.assertTrue(any("target_materials" in x for x in module.validate(place)))

if __name__ == "__main__":
    unittest.main(verbosity=2)

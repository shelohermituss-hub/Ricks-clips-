#!/usr/bin/env python3
"""Pre-render and final-delivery quality gate for RicksClips.

Examples:
  python tools/check_cinematic_quality.py episodes/my-film/film.json
  python tools/check_cinematic_quality.py episodes/my-film/film.json --video episodes/my-film/final.mp4
  python tools/check_cinematic_quality.py episodes/my-film/film.json --video episodes/my-film/final.mp4 --film-analysis --render-geometry

The gate combines configuration, camera-bake, motion-library and delivery checks.
Visual style, acting quality, reference matching and final sound remain human review tasks.
"""
from __future__ import annotations
import argparse
import json
import math
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"


def finite_vec(value, length=3):
    return isinstance(value, list) and len(value) >= length and all(isinstance(x, (int, float)) and math.isfinite(x) for x in value[:length])


def run_command(label: str, cmd: list[str], cwd: Path | None = None) -> tuple[str, str]:
    try:
        result = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=False)
    except OSError as exc:
        return "NOT_RUN", f"{label}: could not start ({exc})"
    tail = "\n".join((result.stdout + "\n" + result.stderr).splitlines()[-18:]).strip()
    if result.returncode == 0:
        return "PASS", tail or f"{label}: completed"
    return "FAIL", tail or f"{label}: exit code {result.returncode}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("film", type=Path, help="film.json for this episode")
    ap.add_argument("--video", type=Path, help="final MP4 to validate (optional during preflight)")
    ap.add_argument("--require-audio", action="store_true", help="fail delivery if no audio track")
    ap.add_argument("--film-analysis", action="store_true", help="run pixel-based camera and continuity analysis (needs Python dependencies)")
    ap.add_argument("--render-geometry", action="store_true", help="run the real Three.js/GPU frame checks (needs a working Chromium WebGL renderer)")
    ap.add_argument("--strict", action="store_true", help="promote configuration and missing-bake warnings to failures")
    ap.add_argument("--out", type=Path, help="report folder; default: <episode>/out/quality")
    args = ap.parse_args()

    film_path = args.film.resolve()
    if not film_path.is_file():
        print(f"FAIL: film file not found: {film_path}", file=sys.stderr)
        return 2
    ep = film_path.parent
    out = (args.out.resolve() if args.out else ep / "out" / "quality")
    out.mkdir(parents=True, exist_ok=True)
    checks: list[dict] = []

    def add(group: str, name: str, status: str, detail: str, fix: str = ""):
        checks.append({"group": group, "name": name, "status": status, "detail": detail, "fix": fix})

    try:
        film = json.loads(film_path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        add("film", "film.json parses", "FAIL", str(exc))
        film = {}

    fps = film.get("fps")
    size = film.get("size")
    add("film", "vertical delivery profile", "PASS" if fps == 30 and size == [1080, 1920] else ("FAIL" if args.strict else "WARN"),
        f"fps={fps!r}; size={size!r}; target=30 fps, [1080, 1920]",
        "Set film.json fps to 30 and size to [1080, 1920] for the standard vertical master.")
    kit3d = film.get("kit3d")
    add("environment", "kit3d look kit enabled", "PASS" if kit3d is True or isinstance(kit3d, dict) else ("FAIL" if args.strict else "WARN"),
        f"film.json kit3d={kit3d!r}", "Enable kit3d for the PBR relief/sky/tree look; individual places can opt out deliberately.")
    polish = film.get("motion_polish", {})
    polish_on = isinstance(polish, dict) and polish.get("enabled") is True
    add("motion", "secondary motion polish", "PASS" if polish_on else ("FAIL" if args.strict else "WARN"),
        f"motion_polish={polish!r}", "Set motion_polish.enabled=true to enable subtle head follow-through, breathing and safe hand follow-through.")
    for key in ("cast", "places", "takes"):
        ok = isinstance(film.get(key), (dict, list)) and len(film.get(key)) > 0
        add("film", f"{key} present", "PASS" if ok else "FAIL", f"{key} entries={len(film.get(key, [])) if hasattr(film.get(key, []), '__len__') else 'n/a'}")

    # Validate camera bake when it exists. Missing bake is expected before the plan step, so WARN, not false PASS.
    cam_path = ep / "out" / "plan" / "camera_baked.json"
    if not cam_path.is_file():
        add("camera", "camera bake exists", "FAIL" if args.strict else "WARN", "out/plan/camera_baked.json is not present yet.", f"Run: python tools/film_plan.py check {film_path}")
    else:
        try:
            cam_obj = json.loads(cam_path.read_text(encoding="utf-8-sig"))
            frames = cam_obj.get("frames", cam_obj) if isinstance(cam_obj, dict) else cam_obj
            if not isinstance(frames, list) or not frames:
                add("camera", "camera bake structure", "FAIL", "camera_baked.json has no non-empty frames list")
            else:
                bad = []
                places = set((film.get("places") or {}).keys())
                for idx, frame in enumerate(frames):
                    if not isinstance(frame, dict) or not finite_vec(frame.get("pos")) or not finite_vec(frame.get("aim")):
                        bad.append(f"frame {idx}: missing/invalid pos or aim")
                        continue
                    fov = frame.get("fov_v")
                    if not isinstance(fov, (int, float)) or not math.isfinite(fov) or not (1 < fov < 179):
                        bad.append(f"frame {idx}: invalid fov_v {fov!r}")
                    place = frame.get("place")
                    if place is not None and places and place not in places:
                        bad.append(f"frame {idx}: unknown place {place!r}")
                add("camera", "camera bake frames", "FAIL" if bad else "PASS", f"{len(frames)} frames; {len(bad)} malformed entries" + ("; " + "; ".join(bad[:5]) if bad else ""), "Re-bake the plan and fix missing positions, aims, fov or place names.")
        except (OSError, json.JSONDecodeError, TypeError, AttributeError) as exc:
            add("camera", "camera bake parses", "FAIL", str(exc))

    # Always test the motion library and store its full machine-readable report.
    node = shutil.which("node")
    motion_json = out / "motion_quality.json"
    if not node:
        add("motion", "motion-library QA", "NOT_RUN", "Node.js was not found on PATH.")
    else:
        status, detail = run_command("motion QA", [node, str(TOOLS / "check_motion_quality.mjs"), "--json", str(motion_json)], cwd=ROOT)
        add("motion", "motion-library QA", status, detail, "Repair missing motion modules/references or invalid pose results shown in motion_quality.json.")

    if args.video:
        video = args.video.resolve()
        status, detail = run_command("delivery metadata", [sys.executable, str(TOOLS / "check_delivery.py"), str(video), *( ["--require-audio"] if args.require_audio else [])])
        add("delivery", "MP4 metadata", status, detail, "Correct resolution, frame rate, duration and the required audio stream.")
        if args.film_analysis:
            status, detail = run_command("pixel film analysis", [sys.executable, str(TOOLS / "check_film.py"), str(video), "--film", str(film_path), "--out", str(out / "film_analysis")], cwd=ROOT)
            add("delivery", "pixel camera/continuity analysis", status, detail, "Review film_check.md and repair the measured camera/freeze/flicker/face gates.")
        else:
            add("delivery", "pixel camera/continuity analysis", "NOT_RUN", "Use --film-analysis to run the rendered-video image analysis.")
    else:
        add("delivery", "final MP4 metadata", "NOT_RUN", "No --video was supplied; expected during a pre-render check.")

    if args.render_geometry:
        node = shutil.which("node")
        if not node:
            add("render", "geometry-aware GPU frame checks", "NOT_RUN", "Node.js was not found on PATH.")
        else:
            status, detail = run_command("geometry frame checks", [node, str(TOOLS / "frame_checks" / "check.mjs"), str(film_path)], cwd=ROOT)
            add("render", "geometry-aware GPU frame checks", status, detail, "Inspect frame_checks.md and FAIL crops; this gate requires the actual Three.js/WebGL renderer.")
    else:
        add("render", "geometry-aware GPU frame checks", "NOT_RUN", "Use --render-geometry on the target GPU workstation; this is not simulated by static checks.")

    # Explicit manual gates: the code can never honestly replace a human visual/audio review.
    manual = [
        "Compare representative full-resolution frames side-by-side with the approved visual reference (camera, world detail, materials, light, atmosphere, silhouette).",
        "Watch all key actions at speed: planted feet, limb intersections, hand-object contact, expressions, blinks, follow-through and transitions.",
        "Inspect at least 16 evenly spaced final-video frames for character/prop drift, background jumps, floating or clipping.",
        "Listen to the complete film: voice, music and effects sync, balance, clipping, silence and ending.",
    ]
    failures = sum(c["status"] == "FAIL" for c in checks)
    warnings = sum(c["status"] == "WARN" for c in checks)
    not_run = sum(c["status"] == "NOT_RUN" for c in checks)
    if args.strict and warnings:
        failures += warnings
    status = "FAIL" if failures else "PASS_WITH_WARNINGS" if warnings or not_run else "PASS"
    report = {
        "schema": "ricksclips.cinematic-quality.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "film": str(film_path), "video": str(args.video.resolve()) if args.video else None,
        "status": status, "summary": {"pass": sum(c["status"] == "PASS" for c in checks), "warn": warnings, "fail": sum(c["status"] == "FAIL" for c in checks), "not_run": not_run},
        "checks": checks, "manual_review_required": manual,
    }
    (out / "cinematic_quality.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [f"# Cinematic Quality Gate — {film_path.parent.name}", "", f"**Result: {status}** — {report['summary']['pass']} PASS / {warnings} WARN / {report['summary']['fail']} FAIL / {not_run} NOT RUN", "", "| Status | Group | Check | Detail | Action |", "|---|---|---|---|---|"]
    for check in checks:
        detail = check["detail"].replace("|", "\\|").replace("\n", " ")
        fix = check["fix"].replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {check['status']} | {check['group']} | {check['name']} | {detail} | {fix} |")
    lines += ["", "## Human review still required", ""] + [f"- [ ] {item}" for item in manual] + ["", "This report does not claim aesthetic approval unless the rendered frames and final sound have actually been reviewed."]
    (out / "cinematic_quality.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Cinematic QA: {status} | {report['summary']['pass']} PASS / {warnings} WARN / {report['summary']['fail']} FAIL / {not_run} NOT RUN")
    print(f"Report: {out / 'cinematic_quality.md'}")
    for c in checks:
        if c["status"] != "PASS": print(f"{c['status']:8} {c['group']}: {c['name']} — {c['detail']}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

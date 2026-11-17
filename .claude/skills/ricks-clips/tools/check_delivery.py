#!/usr/bin/env python3
"""Validate a finished MP4's delivery properties with ffprobe.
Default contract: vertical 1080x1920, 30 fps, positive duration.
This checks file metadata only; it does not judge visual continuity or sound quality.
"""
from __future__ import annotations
import argparse
import json
import shutil
import subprocess
import sys
from fractions import Fraction
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("video", type=Path, help="Finished MP4 to inspect")
    ap.add_argument("--width", type=int, default=1080)
    ap.add_argument("--height", type=int, default=1920)
    ap.add_argument("--fps", type=float, default=30.0)
    ap.add_argument("--require-audio", action="store_true", help="Fail if no audio stream is present")
    args = ap.parse_args()

    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        print("FAIL: ffprobe is not on PATH (install ffmpeg and reopen the terminal).", file=sys.stderr)
        return 2
    if not args.video.is_file():
        print(f"FAIL: video file not found: {args.video}", file=sys.stderr)
        return 2
    cmd = [ffprobe, "-v", "error", "-show_streams", "-show_format", "-of", "json", str(args.video)]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    except OSError as exc:
        print(f"FAIL: could not run ffprobe: {exc}", file=sys.stderr)
        return 2
    if result.returncode:
        print("FAIL: ffprobe could not read the file: " + (result.stderr.strip() or f"exit {result.returncode}"), file=sys.stderr)
        return 2
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        print(f"FAIL: ffprobe returned invalid JSON: {exc}", file=sys.stderr)
        return 2

    streams = data.get("streams") or []
    video = next((s for s in streams if s.get("codec_type") == "video"), None)
    audio = next((s for s in streams if s.get("codec_type") == "audio"), None)
    failures: list[str] = []
    duration = 0.0
    if video is None:
        failures.append("no video stream")
    else:
        w, h = video.get("width"), video.get("height")
        if (w, h) != (args.width, args.height):
            failures.append(f"resolution is {w}x{h}, expected {args.width}x{args.height}")
        def as_rate(value: str | None) -> float:
            try:
                return float(Fraction(value or "0/1"))
            except (ValueError, ZeroDivisionError):
                return 0.0
        avg_fps = as_rate(video.get("avg_frame_rate"))
        nominal_fps = as_rate(video.get("r_frame_rate"))
        fps = avg_fps or nominal_fps
        if abs(fps - args.fps) > 0.01:
            failures.append(f"average frame rate is {fps:g} fps, expected {args.fps:g} fps")
        if avg_fps and nominal_fps and abs(avg_fps - nominal_fps) > 0.01:
            failures.append(f"variable/inconsistent frame rate detected (avg {avg_fps:g}, nominal {nominal_fps:g})")
        try:
            duration = float(video.get("duration") or (data.get("format") or {}).get("duration") or 0)
        except (TypeError, ValueError):
            duration = 0.0
        if duration <= 0:
            failures.append("duration is missing or not positive")
        frames = video.get("nb_read_frames") or video.get("nb_frames")
        if frames not in (None, "N/A"):
            try:
                if int(frames) <= 0:
                    failures.append("video frame count is not positive")
            except (TypeError, ValueError):
                failures.append(f"invalid video frame count: {frames!r}")
        print(f"Video: {w}x{h} | avg {avg_fps:g} fps (nominal {nominal_fps:g}) | {duration:.3f} s | codec {video.get('codec_name', 'unknown')}")
    print(f"Audio stream: {'present' if audio else 'not found'}")
    if args.require_audio and not audio:
        failures.append("audio stream is required but missing")
    if audio:
        sample_rate = int(audio.get("sample_rate") or 0)
        channels = int(audio.get("channels") or 0)
        try:
            audio_duration = float(audio.get("duration") or 0)
        except (TypeError, ValueError):
            audio_duration = 0.0
        print(f"Audio: {audio.get('codec_name', 'unknown')} | {sample_rate or 'unknown'} Hz | {channels or 'unknown'} channel(s)")
        if args.require_audio and sample_rate and sample_rate < 44100:
            failures.append(f"audio sample rate is {sample_rate} Hz, expected at least 44100 Hz")
        if args.require_audio and channels <= 0:
            failures.append("audio channel count is missing or invalid")
        if args.require_audio and audio_duration > 0 and duration > 0 and audio_duration < duration - 0.25:
            failures.append(f"audio ends {duration - audio_duration:.3f} s before the video")

    if failures:
        print("RESULT: FAIL")
        for item in failures:
            print(" - " + item)
        return 1
    print("RESULT: PASS — delivery metadata meets the requested contract.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

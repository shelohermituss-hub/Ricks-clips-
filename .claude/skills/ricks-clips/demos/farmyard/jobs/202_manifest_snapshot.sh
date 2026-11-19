#!/usr/bin/env bash
# Rebuilds nothing: its only effect is that blender_pod.sh writes a new manifest.json with the current manifest.py,
# which lists live files (gpu_usage.csv, setup.log) as frozen copies so pod.py fetch can verify them (2026-11-19).
echo "snapshot job: manifest refreshed after this job"

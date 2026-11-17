"""Refresh the installed Ricks Clips V1.1 skill and agents.
Run from any directory: python tools/refresh_installed_skill.py
This delegates to install.py so install and refresh always use the same destination,
placeholder handling, rule mirror and generated department slices.
"""
from pathlib import Path
import subprocess, sys
ROOT = Path(__file__).resolve().parent.parent
result = subprocess.run([sys.executable, str(ROOT / "install.py")], check=False)
raise SystemExit(result.returncode)

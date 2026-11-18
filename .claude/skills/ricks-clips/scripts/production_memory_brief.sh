#!/usr/bin/env bash
# SessionStart hook (Production Intelligence v1.0, 2026-11-18): tells Claude, at the start of every session, that the
# production memory exists and what it holds. Read-only; never blocks startup; prints a few lines.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="$ROOT/.venv/bin/python"; [ -x "$PY" ] || PY=python3
"$PY" - "$ROOT" <<'PYEOF' 2>/dev/null || true
import json, os, sys, glob
root = sys.argv[1]
L = json.load(open(os.path.join(root, "memory", "lessons_learned.json")))["lessons"]
v = [x for x in L if x.get("status") == "validated"]
print("[RicksClips] rc pipeline (Blender): docs/ARCHITECTURE.md, docs/GUIDE_UTILISATEUR_FR.md; demo: demos/farmyard.")
print("[RicksClips] Production Intelligence: %d validated global lessons (%d total) in memory/LESSONS.md. For a film: tools/production_controller.py init/gates/review (CB_RULES 11g)." % (len(v), len(L)))
for p in sorted(glob.glob(os.path.join(root, "episodes", "*", "production", "GATES.json"))):
    if os.path.exists(os.path.join(os.path.dirname(os.path.dirname(p)), "ARCHIVED.md")): continue   # archived films are not briefed
    g = json.load(open(p)); r = g.get("results", []); t = {s: sum(x["status"] == s for x in r) for s in ("PASS", "WARN", "FAIL", "NOT_RUN")}
    oi = os.path.join(os.path.dirname(p), "QA_LOG.json"); q = json.load(open(oi)) if os.path.exists(oi) else {"issues": []}
    op = sum(1 for i in q.get("issues", []) if i.get("status") == "open")
    print("[RicksClips]   %s: last gates (%s, %s) %s; %d open QA issues" % (g.get("episode"), g.get("phase"), g.get("date"), t, op))
PYEOF
exit 0

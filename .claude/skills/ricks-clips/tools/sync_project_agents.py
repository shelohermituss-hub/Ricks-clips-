"""Mirror the skill's agents (agents/*.md, the master copies) into the project's .claude/agents/ for Claude Code Web.
The project copies are the same files with repository-relative paths, because the session runs from the project root.
    .venv/bin/python tools/sync_project_agents.py [--check]     (--check: report differences, change nothing; exit 1 if stale)
Added 2026-11-18 with the Production Intelligence layer, so a rule change in an agent reaches the agents Claude Code Web runs."""
import glob, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJ = os.path.dirname(os.path.dirname(os.path.dirname(ROOT)))          # <repo>/.claude/skills/ricks-clips -> <repo>
PREFIX = ".claude/skills/ricks-clips/"
FRONT = re.compile(r"\A---\n(.*?)\n---\n", re.S)
REL = r"(?<![\w/\.:-])(templates|tools|references|library|examples|agents|rules|production|memory|episodes|docs|demos|blender|scripts)/"
ROOTFILES = r"(?<![\w/\.:-])(CB_RULES|SKILL|START_HERE|WORKFLOW|CLOUD_MODE|DENSITY_RULES|CINEMATOGRAPHY)\.md"
def project_copy(text):
    m = FRONT.match(text); head, body = (m.group(0), text[m.end():]) if m else ("", text)
    body = re.sub(REL, PREFIX + r"\1/", body)
    body = re.sub(ROOTFILES, lambda k: PREFIX + k.group(1) + ".md", body)
    return head + body
if __name__ == "__main__":
    check = "--check" in sys.argv; dst = os.path.join(PROJ, ".claude", "agents"); stale = []
    for p in sorted(glob.glob(os.path.join(ROOT, "agents", "*.md"))):
        out = project_copy(open(p, encoding="utf-8").read()); q = os.path.join(dst, os.path.basename(p))
        cur = open(q, encoding="utf-8").read() if os.path.exists(q) else None
        if cur != out:
            stale.append(os.path.basename(p))
            if not check: os.makedirs(dst, exist_ok=True); open(q, "w", encoding="utf-8", newline="\n").write(out)
    print(("stale: " if check else "synced: ") + (", ".join(stale) or "none"), "(%s)" % os.path.relpath(dst, PROJ))
    sys.exit(1 if (check and stale) else 0)

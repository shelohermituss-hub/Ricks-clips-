"""Lint set modules for comments that swallow code (lesson PI-002, Ghost Army 2026-11-17).

Set modules are written as long one-line statements. A `// note` placed in the MIDDLE of such a line turns everything
after it into a comment: `node --check` still passes when the braces happen to balance, the film renders, and an effect
silently disappears (on Ghost Army: the shell bursts, the river moonlight and a wave fade were all switched off this way).

    .venv/bin/python tools/lint_set_modules.py episodes/<name>/sets/*.js [templates/...]
    exit 0 = clean, 1 = suspicious comments found (each printed as file:line and the swallowed text)

Rule: a `//` comment that FOLLOWS code on the same line is suspicious when the text after it contains code: a statement separator followed by an identifier
call/assignment, or a known kit call (box(, cyl(, add(, ups.push, scene.add, const/let/for/if). Use /* ... */ for inline notes.
"""
import re, sys

CODE_AFTER = re.compile(r"(;\s*[A-Za-z_$][\w$.\[\]]*\s*(\(|=[^=]|\+\+))"          # "; foo(" / "; x = "
                        r"|\b(const|let|var)\s+[\w$\[{]+\s*="                       # declarations
                        r"|\b(for|if|while)\s*\("                                     # control flow
                        r"|[A-Za-z_$][\w$]*(\.[\w$]+)+\s*(\(|=[^=])"                  # a.b.c( / a.b = (method calls, property writes)
                        r"|\b(box|cyl|add|glow|tree|hedge|sherman|act)\(")             # the set kit's own calls

def comment_start(line):
    """index of a // that starts a comment (not inside a string, template, or a URL), else -1"""
    q = None; i = 0; n = len(line)
    while i < n:
        c = line[i]
        if q:
            if c == "\\": i += 2; continue
            if c == q: q = None
        elif c in "'\"`": q = c
        elif c == "/" and i + 1 < n and line[i + 1] == "/":
            if i > 0 and line[i - 1] == ":": i += 2; continue          # http://
            return i
        elif c == "/" and i + 1 < n and line[i + 1] == "*":
            j = line.find("*/", i + 2); i = (j + 2) if j >= 0 else n; continue
        i += 1
    return -1

def lint(path):
    bad = []
    for k, line in enumerate(open(path, encoding="utf-8", errors="replace"), 1):
        s = comment_start(line)
        if s < 0 or not line[:s].strip(): continue          # a whole-line comment cannot swallow code that precedes it
        tail = line[s + 2:]
        if CODE_AFTER.search(tail): bad.append((k, tail.strip()[:140]))
    return bad

if __name__ == "__main__":
    files = sys.argv[1:]
    if not files: print(__doc__); sys.exit(2)
    total = 0
    for f in files:
        for k, t in lint(f): print("%s:%d: comment swallows code: // %s" % (f, k, t)); total += 1
    print("lint_set_modules: %d suspicious comment(s) in %d file(s)" % (total, len(files)))
    sys.exit(1 if total else 0)

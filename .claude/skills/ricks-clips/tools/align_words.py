"""Put the SCRIPT's own words on the timings that faster-whisper heard (cloud 2026-11-17).
    python tools/align_words.py <voice/words.json> <script.txt>        (rewrites words.json; keeps a copy as words_heard.json)
Whisper mishears names and rare words ("foudre" -> "foutre"); words.json drives the captions and every act "at" word, so the
captions must show the script. The two texts are matched letter by letter (difflib on lower-case letters only); each script word
takes the start of the first heard word and the end of the last heard word that its letters land in. Unmatched words are
interpolated between their neighbours. Prints how many script words were matched directly."""
import json, re, sys, difflib, shutil, unicodedata
wp, sp = sys.argv[1], sys.argv[2]
heard = json.load(open(wp, encoding="utf-8")); script = open(sp, encoding="utf-8").read().split()
norm = lambda s: "".join(c for c in unicodedata.normalize("NFC", s.lower()) if c.isalnum())
H, hidx = "", []
for i, w in enumerate(heard):
    t = norm(w["w"]); H += t; hidx += [i] * len(t)
S, sidx = "", []
for j, w in enumerate(script):
    t = norm(w); S += t; sidx += [j] * len(t)
hit = [set() for _ in script]
for a, b, n in difflib.SequenceMatcher(None, S, H, autojunk=False).get_matching_blocks():
    for k in range(n): hit[sidx[a + k]].add(hidx[b + k])
out = []
for j, w in enumerate(script):
    out.append({"w": w, "s": heard[min(hit[j])]["s"], "e": heard[max(hit[j])]["e"]} if hit[j] else {"w": w, "s": None, "e": None})
ok = sum(1 for o in out if o["s"] is not None)
for j, o in enumerate(out):                      # interpolate the few words with no letter match
    if o["s"] is None:
        p = next((out[k]["e"] for k in range(j - 1, -1, -1) if out[k]["s"] is not None), 0.0)
        q = next((out[k]["s"] for k in range(j + 1, len(out)) if out[k]["s"] is not None), p + 0.3)
        o["s"], o["e"] = round(p, 3), round(max(p, q), 3)
for a, b in zip(out, out[1:]):                   # keep time order
    if b["s"] < a["s"]: b["s"] = a["s"]
shutil.copy(wp, wp.replace(".json", "_heard.json")); json.dump(out, open(wp, "w", encoding="utf-8"), indent=0, ensure_ascii=False)
print(json.dumps({"script_words": len(script), "heard_words": len(heard), "matched": ok, "interpolated": len(script) - ok}))

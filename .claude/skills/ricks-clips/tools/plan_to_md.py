"""plan.json -> PLAN.md (the readable plan CB reviews before anything is built; generated, so it never drifts from the data).
    python3 tools/plan_to_md.py <plan.json> [<PLAN.md>]"""
import json, os, sys

def md(P):
    o = ["# Plan — %s" % P["title"], "", "Généré depuis `plan.json` par `tools/plan_to_md.py`. %s" % P.get("notes", ""), "",
         "**Durée** %.1f s · **voix** %d mots · **format** %s, %s i/s · **style** `%s` · **sous-titres** %s" % (P["duration_s"], P["voice"]["words"], P["format"], P["fps"], P["style"], P.get("captions", {}).get("style", "-")),
         "", "**Crochet** : action `%s` à %.1f s · **boucle** : %s" % (P.get("hook", {}).get("action"), P.get("hook", {}).get("t", -1), P.get("loop", "aucune")), ""]
    o += ["## Faits écrits dans le décor", "", "| Fait | Plan | Objet du décor |", "|---|---|---|"] + ["| %s | %s | %s |" % (f["fact"], f.get("shot", ""), f["prop"]) for f in P.get("facts", [])] + [""]
    o += ["## Besoins (téléchargés ou construits avant le premier plan)", "", "| Quoi | Source | État |", "|---|---|---|"] + ["| %s | %s | %s |" % (n["id"], n["source"], n["state"]) for n in P.get("needs", [])] + [""]
    o += ["## Lieux", ""]
    for p in P["places"]:
        L = p.get("light", {}); s = L.get("sun", {})
        o += ["### %s — %s" % (p["id"], L.get("mood", "")), "", p.get("description", ""), "",
              "- **Sol** : %s · **surfaces** : %s" % (p["ground"].get("texture"), ", ".join("%s (%s)" % (x["name"], x["texture"]) for x in p.get("surfaces", []))),
              "- **Ciel** : %s" % p.get("sky", ""),
              "- **Lumière** : soleil élév. %s°, azimut %s°, énergie %s, angle %s° ; appoint %s%s" % (s.get("elevation"), s.get("azimuth"), s.get("energy"), s.get("angle"), L.get("fill"), ("; " + "; ".join(L["practicals"])) if L.get("practicals") else ""),
              "- **Ombres** : %s" % p.get("shadows", ""), "- **Accessoires** : %s" % ", ".join("%s (%s)" % (x["id"], x["source"]) for x in p.get("props", [])), ""]
    o += ["## Personnages (une carte, une vue chacun)", "", "| Rôle | Distribution | Costume | Vue | Tient |", "|---|---|---|---|---|"] + \
         ["| %s | %s | %s | %s | %s |" % (c["id"], c["puppet"], c.get("costume", ""), c.get("view", ""), ", ".join(c.get("held", []))) for c in P["characters"]] + [""]
    o += ["## Objets et leurs états", "", "| Objet | Matière | États |", "|---|---|---|"] + ["| %s | %s | %s |" % (x["id"], x.get("material", ""), " → ".join(x.get("states", []))) for x in P["objects"]] + [""]
    o += ["## Plans", ""]
    for s in P["shots"]:
        o += ["### %s — %s (%.2f → %.2f s), %s" % (s["id"], s["place"], s["t0"], s["t1"], s.get("mood", "")), "", "> %s" % s["narration"], "",
              "**Entrée** : %s · **sortie** : %s · **type** : %s" % (s["transition_in"], s["transition_out"], s.get("shot_type", "")), "", "**Caméra** (jamais à l'arrêt, + dérive à l'épaule) :", ""]
        o += ["- %.2f s · %s · %s mm · %s · vise %s" % (k["t"], k.get("framing", ""), k.get("lens"), k.get("move"), k.get("aim")) for k in s["camera"]] + ["", "**Actions** :", ""]
        for a in s["actions"]:
            o += ["- **%s** (%s, images %d–%d) : %s — *%s*" % (a["id"], a["who"], a["f"][0], a["f"][1], a["what"], a["anim"]),
                  "  - micro : %s" % "; ".join(a["micro"]), "  - réactions : %s" % "; ".join(a["reactions"]),
                  "  - conséquences qui restent : %s" % "; ".join(a["consequences"]), "  - sons : %s" % "; ".join(a["sfx"])]
        o += ["", "**Entrées / sorties / changements d'état** : %s" % "; ".join("%s : %s (par %s)" % (c["who"], c["change"], c["by_action"]) for c in s.get("state_changes", [])),
              "", "**Effets** : %s · **ambiance sonore** : %s" % ("; ".join(s.get("fx", [])), s.get("sound", {}).get("ambience", "")), ""]
    o += ["## Son", "", "- Musique : %s" % P["sound"].get("music"), "- Mixage : %s LUFS ; un bruitage par action et par réaction (listés ci-dessus)" % P["sound"].get("lufs"), ""]
    o += ["## Leçons appliquées", ""] + ["- %s" % l for l in P.get("lessons_planned", [])] + ["", "## Risques", ""] + ["- %s" % r for r in P.get("risks", [])] + [""]
    if P.get("warn_reasons"): o += ["## Avertissements du contrôle gardés (avec leur raison)", ""] + ["- **%s** : %s" % kv for kv in P["warn_reasons"].items()] + [""]
    return "\n".join(o)

if __name__ == "__main__":
    a = sys.argv[1:]; P = json.load(open(a[0])); out = a[1] if len(a) > 1 else os.path.join(os.path.dirname(a[0]), "PLAN.md")
    open(out, "w").write(md(P)); print("wrote", out)

# Son et synchronisation

**Limite principale** : les pistes n'ont pas pu être écoutées dans cet environnement. Tout ce qui suit vient de **mesures** (loudness EBU R128, enveloppe RMS 50 ms, attaques, corrélation stéréo) et des **mots minutés** par transcription automatique. Les constats sur la musique et les bruitages sont INFÉRÉS ou INCONNUS.

## 1. Mesures (MESURÉ, `data/cross_video_measures.json`)
| Vidéo | LUFS intégré | Plage (LU) | Crête (dBTP) | Corr. L/R | Attaques | Mots | Mots/s | Pause max |
|---|---|---|---|---|---|---|---|---|
| V01 | −14,2 | 2,2 | −1,9 | 0,994 | 104 | 237 | 3,65 | 0,46 s |
| V02 | −14,1 | 2,2 | −1,9 | 0,996 | 89 | 237 | 3,83 | 0,36 s |
| V03 | −13,9 | 3,9 | −0,9 | 0,969 | 109 | 264 | 3,21 | 0,64 s |
| V04 | −14,0 | 2,5 | −2,1 | 0,995 | 65 | 217 | 3,67 | 0,36 s |
| V05 | −14,1 | 2,9 | −2,0 | 0,984 | 86 | 235 | 3,53 | 0,42 s |

## 2. Constats
- **Niveau normalisé à −14 LUFS** dans les cinq vidéos (norme des plateformes courtes, INFÉRÉ).
- **Quasi mono** (corrélation ≥ 0,97) : pas de spatialisation marquée.
- **Voix ininterrompue** du début (0,00 s) à la fin ; aucun silence de plus de 0,2 s sous −45 dB dans aucune vidéo.
- **Plage dynamique faible** (2,2-2,9 LU), sauf V03 (3,9 LU, crête −0,9 dBTP) : INFÉRÉ, des explosions et des chocs qui dépassent la voix.
- **Synchronisation** : des attaques coïncident avec les impacts vérifiés à l'image (V01 25,4 s ; V02 2,8 s ; V05 25,9 et 60,7 s). INFÉRÉ : bruitages calés à l'image près.
- **Débit** : 3,2 à 3,8 mots/s, soit un récit rapide sans respiration audible longue.

## 3. Rôle des sons (INFÉRÉ à partir de l'image et des mesures)
- La **voix** porte tout le récit, avec une phrase courte par idée.
- La **musique** est probablement continue sous la voix (aucun silence) : nature INCONNUE.
- Les **bruitages** marquent chaque action (choc, gifle, tampon, explosion, décollage) : identité INCONNUE.

## 4. Recommandations pour RicksClips
- Mix final à −14 LUFS, crête ≤ −1 dBTP, quasi mono.
- Voix continue (pause maximale ≤ 0,6 s), 3,2-3,8 mots/s.
- Un bruitage sur chaque action visible, calé sur l'image du contact ; les effets peuvent dépasser la voix de 1-2 dB sur les gros impacts (cas V03).
- Faire une écoute réelle des références dans un environnement qui le permet, pour compléter ce document (tâche non exécutée).

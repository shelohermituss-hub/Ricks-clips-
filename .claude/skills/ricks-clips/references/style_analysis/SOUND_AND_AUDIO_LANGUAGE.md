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
- Faire une écoute réelle des références dans un environnement qui le permet (toujours non exécutée ; voir §5 pour ce qui a pu être mesuré à la place).

## 5. Couches du son mesurées (priorité 3, 20/11) — `tools/audio_layers.py`, `data/V0x/audio_layers.json`
Toujours sans écoute. Méthode : le signal est séparé en **pendant les mots** (voix + fond) et **entre les mots** (trous ≥ 120 ms, à 40 ms des bords des mots : fond seul), d'après les mots minutés ; puis niveau RMS, répartition par bandes de fréquence, platitude spectrale ; et les attaques (> 9 dB en 50 ms) qui ne tombent **pas** sur un début de mot (candidats bruitages).

| Vidéo | Voix (dBFS RMS) | Fond entre les mots | Voix − fond | Trous avec fond > −50 dBFS | Platitude fond / voix | Attaques hors mots |
|---|---|---|---|---|---|---|
| V01 | −16,8 | −23,7 | 6,9 dB | 100 % (20 trous) | 0,082 / 0,020 | 62 |
| V02 | −16,7 | −22,3 | 5,6 dB | 100 % (26) | 0,052 / 0,018 | 52 |
| V03 | −16,9 | −23,6 | 6,7 dB | 100 % (27) | 0,021 / 0,011 | 79 |
| V04 | −16,9 | −23,9 | 7,0 dB | 100 % (16) | 0,117 / 0,026 | 35 |
| V05 | −17,0 | −23,9 | 6,9 dB | 100 % (16) | 0,104 / 0,024 | 55 |

Ce qu'on peut en dire :
- **MESURÉ** : un **fond sonore est présent dans 100 % des trous entre les mots**, environ **6-7 dB sous la voix** dans les cinq vidéos (V02 un peu plus fort, 5,6 dB). Il n'y a jamais de silence.
- **MESURÉ** : le fond a plus de **graves (< 120 Hz : 9-13 % contre 3-7 % pour la voix)** et plus d'**aigus (> 8 kHz : 8-15 % contre 2 %)** que la voix (sauf V03, dont la piste coupe les aigus). Sa platitude spectrale reste basse (0,02-0,12) : contenu **tonal**, compatible avec une musique plutôt qu'avec un bruit d'ambiance (INFÉRÉ).
- **MESURÉ** : 35 à 79 attaques **hors des débuts de mots** par vidéo, soit 0,6 à 1 par seconde : des bruitages fréquents (INFÉRÉ). Plusieurs tombent **à l'image près** sur un événement vérifié image par image :
  - V03 3,70 s = flash de la porte (image 110), +6,5 dB au-dessus du fond local ;
  - V04 3,10 s = début du nuage de poussière (image 91-93), +7,4 dB ;
  - V02 30,90 s = contact de la voiture de sport (image 927), +4,8 dB ;
  - V03 60,15-60,9 s = apparition du camion dans le canyon (images 1805-1830, vues à 2 i/s seulement), jusqu’à +10,7 dB.
- **Limite** : 50 des 53 événements catalogués contiennent une attaque dans leur intervalle, mais les attaques sont si fréquentes (environ 1,4/s) que ce chiffre est proche du hasard. Seules les coïncidences **à l'image près** ci-dessus sont des preuves.
- **INCONNU** toujours : instruments, genre, tempo de la musique, nature exacte de chaque bruitage. Une écoute humaine reste nécessaire.

**Recommandation mise à jour** : fond musical continu à −6/−7 dB sous la voix (RMS), riche en graves et en aigus pour ne pas masquer la voix (qui occupe 120-500 Hz) ; environ 1 bruitage par seconde, calé à l'image près sur les contacts, +5 à +10 dB au-dessus du fond.

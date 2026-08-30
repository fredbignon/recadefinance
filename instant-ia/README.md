# L'Instant IA — format des billets

L'idée de cette rubrique : prendre **une notion ou une thématique liée à
l'IA** (appliquée à la finance, à l'économie, ou plus généralement) souvent
trop technique, et l'expliquer simplement pour un public large — pas une
analyse complète comme celles du dossier `/posts`, plutôt un éclairage court
et pédagogique sur un seul concept à la fois.

Ce n'est **pas nécessairement un contenu de contributeur invité** — ça peut
être toi (Récade Finance), un partenaire ponctuel, ou un expert régulier.
Les champs `author_name` / `author_title` restent donc optionnels : laisse-les
vides si c'est toi qui écris.

**Le format peut être écrit OU vidéo** (ou les deux à la fois).

## Créer un nouveau billet

Fichier : `AAAA-MM-JJ-titre-court.md` dans ce dossier.

```yaml
---
title: "Titre du billet — ex. « C'est quoi un LLM, concrètement ? »"
date: 2026-09-01
author_name: ""          # optionnel — laisse vide si c'est toi qui écris
author_title: ""         # optionnel
video_url: ""            # optionnel — lien YouTube, ou chemin vers un .mp4 dans /assets
excerpt: "Une phrase d'accroche."
---

Le texte du billet, en Markdown, 2-4 paragraphes maximum — c'est un
"instant", pas un article complet. Si `video_url` est renseigné, la vidéo
s'affiche automatiquement au-dessus de ce texte (qui peut alors servir de
résumé ou de transcription courte).
```

### Exemple avec vidéo YouTube
```yaml
video_url: "https://www.youtube.com/watch?v=XXXXXXXXXXX"
```

### Exemple avec vidéo locale
Place le fichier `.mp4` dans `/assets`, puis :
```yaml
video_url: "assets/ma-video.mp4"
```

Puis : `python3 scripts/build.py` et `git push` (ou laisser l'automatisation
GitHub Actions s'en charger si le fichier est ajouté directement sur GitHub).

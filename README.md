# Récade Finance — site statique

Générateur statique simple : Markdown → HTML, aucune dépendance lourde.

## Structure

```
posts/          → articles sources en Markdown (frontmatter + contenu)
scripts/build.py → génère le site dans /docs
assets/style.css → feuille de style (copiée dans docs/assets/ au build)
docs/            → le site généré — c'est CE dossier que GitHub Pages sert
docs/CNAME       → contient "recade-finance.com" (domaine personnalisé)
```

## Écrire un nouvel article

1. Crée un fichier dans `posts/`, nommé `AAAA-MM-JJ-titre-court.md`
2. En-tête obligatoire (frontmatter) :

```yaml
---
title: "Titre de l'article"
date: 2026-08-24
category: analyses        # ou : focus-benin
excerpt: "Une phrase d'accroche, affichée sur la page d'accueil."
---
```

3. Écris le contenu en Markdown en dessous (titres `##`, gras `**texte**`, listes `-`, etc.)
4. Lance `python3 scripts/build.py` — le site se régénère dans `/docs`
5. `git add . && git commit -m "Nouvel article : ..." && git push`

GitHub Pages republie automatiquement après chaque push, en général en moins d'une minute.

## Mise en place initiale sur GitHub (à faire une seule fois)

1. Crée un dépôt GitHub (public ou privé, les deux fonctionnent avec Pages sur un compte payant ; public suffit et gratuit sinon)
2. Pousse ce dossier entier dedans :
   ```
   git init
   git add .
   git commit -m "Premier commit — Récade Finance"
   git branch -M main
   git remote add origin https://github.com/TON-COMPTE/recade-finance-site.git
   git push -u origin main
   ```
3. Sur GitHub : Settings → Pages → Source : sélectionne la branche `main` et le dossier `/docs`
4. Toujours sur Settings → Pages : dans « Custom domain », renseigne `recade-finance.com`, coche « Enforce HTTPS » une fois le certificat généré (peut prendre jusqu'à 24h)

## Configuration DNS chez ton registrar (Gandi, OVH, etc.)

Pour un domaine racine (`recade-finance.com`, sans www), ajoute 4 enregistrements A pointant vers GitHub Pages :

```
185.199.108.153
185.199.109.153
185.199.110.153
185.199.111.153
```

Et si tu veux aussi que `www.recade-finance.com` fonctionne, ajoute un enregistrement CNAME :
```
www → TON-COMPTE.github.io
```

La propagation DNS peut prendre de quelques minutes à 24h.

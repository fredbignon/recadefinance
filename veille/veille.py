#!/usr/bin/env python3
"""
Récade Finance — Outil de veille automatisée
================================================
Lit des flux RSS (voir veille/sources_veille.yaml), filtre les
articles par mots-clés, et ajoute les nouveaux résultats dans
veille/digest.md — sans jamais dupliquer un article déjà vu
(état conservé dans veille/deja_vus.json).

Conçu pour tourner régulièrement via GitHub Actions (voir
.github/workflows/veille.yml), mais peut aussi se lancer à la main :

    pip install feedparser pyyaml
    python3 veille/veille.py

AVERTISSEMENT : les URL de flux RSS dans sources_veille.yaml sont
des candidats à vérifier — voir les commentaires de ce fichier.
"""

import os
import re
import json
import yaml
import feedparser
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VEILLE_DIR = os.path.join(ROOT, "veille")
SOURCES_FILE = os.path.join(VEILLE_DIR, "sources_veille.yaml")
DIGEST_FILE = os.path.join(VEILLE_DIR, "digest.md")
SEEN_FILE = os.path.join(VEILLE_DIR, "deja_vus.json")


def charger_config():
    with open(SOURCES_FILE, encoding="utf-8") as f:
        return yaml.safe_load(f)


def charger_deja_vus():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, encoding="utf-8") as f:
            return set(json.load(f))
    return set()


def sauver_deja_vus(vus):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(vus), f, ensure_ascii=False, indent=2)


def correspond_aux_mots_cles(titre, resume, mots_cles):
    texte = f"{titre} {resume}".lower()
    trouves = [m for m in mots_cles if m.lower() in texte]
    return trouves


def nettoyer_html(texte):
    return re.sub(r"<[^>]+>", "", texte or "").strip()


def collecter_nouveaux_articles(config, deja_vus):
    nouveaux = []
    for source in config["sources"]:
        nom = source["name"]
        url = source["rss_url"]
        try:
            flux = feedparser.parse(url)
        except Exception as e:
            print(f"  ⚠️  Erreur sur {nom} ({url}) : {e}")
            continue

        if flux.bozo and not flux.entries:
            print(f"  ⚠️  Flux invalide ou inaccessible pour {nom} ({url}) — à vérifier manuellement")
            continue

        for entry in flux.entries:
            uid = entry.get("id") or entry.get("link")
            if not uid or uid in deja_vus:
                continue

            titre = entry.get("title", "")
            resume = nettoyer_html(entry.get("summary", ""))
            mots_trouves = correspond_aux_mots_cles(titre, resume, config["mots_cles"])

            if mots_trouves:
                nouveaux.append({
                    "source": nom,
                    "titre": titre,
                    "lien": entry.get("link", ""),
                    "resume": resume[:280],
                    "mots_cles": mots_trouves,
                    "uid": uid,
                    "date": entry.get("published", ""),
                })
            deja_vus.add(uid)  # marqué comme vu même si pas retenu, pour ne pas le retraiter

    return nouveaux, deja_vus


def ajouter_au_digest(nouveaux):
    os.makedirs(VEILLE_DIR, exist_ok=True)
    entete = not os.path.exists(DIGEST_FILE)

    with open(DIGEST_FILE, "a", encoding="utf-8") as f:
        if entete:
            f.write("# Digest de veille — Récade Finance\n\n")
            f.write("Généré automatiquement. Chaque entrée est à trier : ")
            f.write("celles qui valent la peine deviennent un post (visuel + texte), ")
            f.write("les autres restent ici en archive.\n\n---\n\n")

        if not nouveaux:
            return

        date_du_jour = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        f.write(f"\n## Veille du {date_du_jour}\n\n")
        for item in nouveaux:
            f.write(f"### {item['titre']}\n")
            f.write(f"- **Source** : {item['source']}\n")
            f.write(f"- **Lien** : {item['lien']}\n")
            f.write(f"- **Mots-clés déclencheurs** : {', '.join(item['mots_cles'])}\n")
            if item["resume"]:
                f.write(f"- **Résumé (extrait automatique)** : {item['resume']}...\n")
            f.write("- **Statut** : [ ] à trier\n\n")


def main():
    print("=" * 60)
    print("Récade Finance — Veille automatisée")
    print("=" * 60)

    config = charger_config()
    deja_vus = charger_deja_vus()

    nouveaux, deja_vus_maj = collecter_nouveaux_articles(config, deja_vus)

    print(f"\n{len(nouveaux)} nouvel(aux) article(s) pertinent(s) trouvé(s)")
    for item in nouveaux:
        print(f"  → [{item['source']}] {item['titre']}")

    ajouter_au_digest(nouveaux)
    sauver_deja_vus(deja_vus_maj)

    print(f"\nDigest mis à jour : {DIGEST_FILE}")


if __name__ == "__main__":
    main()

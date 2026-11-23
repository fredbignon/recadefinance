#!/usr/bin/env python3
"""
Récade Finance : outil de veille automatisée
================================================
Lit des flux RSS (voir veille/sources_veille.yaml), filtre les
articles par thèmes (économie, finance, finance climatique et
durabilité, data et IA), écarte la politique, repère les événements
possibles, et ajoute les nouveaux résultats dans veille/digest.md,
sans jamais dupliquer un article déjà vu (état conservé dans
veille/deja_vus.json).

Conçu pour tourner chaque jour via GitHub Actions (voir
.github/workflows/veille.yml), mais peut aussi se lancer à la main :

    pip install feedparser pyyaml
    python3 veille/veille.py
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
AGENT = "Mozilla/5.0 (compatible; veille-recade/1.0)"


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


def mot_present(mot, texte):
    """Recherche d'un mot ou d'une expression, sans tenir compte de la casse.
    Les mots de plus de 3 lettres peuvent être suivis d'une terminaison (banque, banques) ;
    les mots courts (IA, PIB, ESG) doivent apparaître entiers."""
    motif = re.escape(mot.lower())
    if len(mot) <= 3:
        motif = r"(?<!\w)" + motif + r"(?!\w)"
    else:
        motif = r"(?<!\w)" + motif
    return re.search(motif, texte.lower()) is not None


def trouver(mots, texte):
    return [m for m in mots if mot_present(m, texte)]


def nettoyer_html(texte):
    return re.sub(r"<[^>]+>", "", texte or "").strip()


def analyser_entree(entry, source, config):
    """Retourne un dictionnaire si l'entrée est retenue, sinon None."""
    titre = entry.get("title", "")
    resume = nettoyer_html(entry.get("summary", ""))
    texte = f"{titre} {resume}"
    est_agenda = source.get("type") == "agenda"

    if trouver(config.get("mots_exclus", []), titre):
        return None

    themes_trouves = {}
    for theme, mots in (config.get("themes") or {}).items():
        trouves = trouver(mots, texte)
        if trouves:
            themes_trouves[theme] = trouves

    if not themes_trouves and not est_agenda:
        return None
    if source.get("theme_dans_titre") and not est_agenda:
        if not any(trouver(mots, titre) for mots in (config.get("themes") or {}).values()):
            return None
    if source.get("exiger_zone") and not trouver(config.get("zone", []), texte):
        return None

    evenement = est_agenda or bool(trouver(config.get("mots_evenements", []), titre))
    return {
        "source": source["name"],
        "titre": titre,
        "lien": entry.get("link", ""),
        "resume": resume[:280],
        "themes": themes_trouves,
        "evenement": evenement,
        "agenda": est_agenda,
        "date": entry.get("published", ""),
    }


def collecter_nouveaux_articles(config, deja_vus):
    nouveaux = []
    for source in config["sources"]:
        nom = source["name"]
        url = source["rss_url"]
        try:
            flux = feedparser.parse(url, agent=AGENT)
        except Exception as e:
            print(f"  ATTENTION : erreur sur {nom} ({url}) : {e}")
            continue

        if not flux.entries:
            print(f"  ATTENTION : flux vide, invalide ou inaccessible pour {nom} ({url}), à vérifier")
            continue

        for entry in flux.entries:
            uid = entry.get("id") or entry.get("link")
            if not uid or uid in deja_vus:
                continue
            item = analyser_entree(entry, source, config)
            if item:
                item["uid"] = uid
                nouveaux.append(item)
            deja_vus.add(uid)  # marqué comme vu même si non retenu, pour ne pas le retraiter

    return nouveaux, deja_vus


def ajouter_au_digest(nouveaux):
    os.makedirs(VEILLE_DIR, exist_ok=True)
    entete = not os.path.exists(DIGEST_FILE)

    with open(DIGEST_FILE, "a", encoding="utf-8") as f:
        if entete:
            f.write("# Digest de veille, Récade Finance\n\n")
            f.write("Généré automatiquement. Chaque entrée est à trier : ")
            f.write("celles qui valent la peine deviennent une actualité, une analyse ")
            f.write("ou une fiche de la rubrique Événements, les autres restent ici en archive.\n\n---\n\n")

        if not nouveaux:
            return

        date_du_jour = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        f.write(f"\n## Veille du {date_du_jour}\n\n")
        for item in nouveaux:
            f.write(f"### {item['titre']}\n")
            f.write(f"- **Source** : {item['source']}\n")
            f.write(f"- **Lien** : {item['lien']}\n")
            if item["themes"]:
                themes = " ; ".join(f"{t} ({', '.join(m)})" for t, m in item["themes"].items())
                f.write(f"- **Thèmes** : {themes}\n")
            if item["evenement"]:
                f.write("- **Type** : événement possible. À vérifier avant de publier : dates, lieu, "
                        "organisateur, accès, tarif, site officiel.\n")
            if item["resume"]:
                f.write(f"- **Résumé (extrait automatique)** : {item['resume']}...\n")
            f.write("- **Statut** : [ ] à trier\n\n")


def main():
    print("=" * 60)
    print("Récade Finance : veille automatisée")
    print("=" * 60)

    config = charger_config()
    deja_vus = charger_deja_vus()

    nouveaux, deja_vus_maj = collecter_nouveaux_articles(config, deja_vus)

    print(f"\n{len(nouveaux)} nouvel(aux) article(s) pertinent(s) trouvé(s)")
    for item in nouveaux:
        marque = " [événement possible]" if item["evenement"] else ""
        print(f"  - [{item['source']}] {item['titre']}{marque}")

    ajouter_au_digest(nouveaux)
    sauver_deja_vus(deja_vus_maj)

    print(f"\nDigest mis à jour : {DIGEST_FILE}")


if __name__ == "__main__":
    main()

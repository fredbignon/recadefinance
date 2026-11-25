#!/usr/bin/env python3
"""
Générateur statique de Récade Finance
=====================================
Lit les fichiers Markdown (posts, actualités, billets courts) et les fichiers de
contenu (content/*.yaml), puis génère les pages HTML dans /docs, le dossier servi
par GitHub Pages. Dépendances : markdown et pyyaml.

Usage : python3 scripts/build.py
"""

import os
import re
import glob
import yaml
import markdown
import shutil
import html as html_lib
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS_DIR = os.path.join(ROOT, "posts")
ACTUALITES_DIR = os.path.join(ROOT, "actualites")
MINUTE_ECO_DIR = os.path.join(ROOT, "minute-eco")
INSTANT_IA_DIR = os.path.join(ROOT, "instant-ia")
EVENEMENTS_DIR = os.path.join(ROOT, "evenements")
DOCS_DIR = os.path.join(ROOT, "docs")
CONTENT_FILE = os.path.join(ROOT, "content", "site_content.yaml")
BRVM_FILE = os.path.join(ROOT, "content", "marche_brvm.yaml")
SITE_TITLE = "Récade Finance"
SITE_TAGLINE = "Finance, économie et IA : un regard africain"
SITE_URL = "https://recade-finance.com"

# Rubriques désaffichées du site. Leur contenu reste dans content/site_content.yaml :
# passer la valeur à True pour les réafficher (menu, pied de page et page d'accueil).
SECTIONS_ACTIVES = {
    "tribune": True,
    "brvm": False,   # tableau et analyse du marché BRVM (données dans content/marche_brvm.yaml)
}

with open(CONTENT_FILE, encoding="utf-8") as f:
    CONTENT = yaml.safe_load(f)

with open(BRVM_FILE, encoding="utf-8") as f:
    BRVM = yaml.safe_load(f)

CATEGORY_LABELS = {
    "analyses": "Analyses",
    "focus-benin": "Focus Bénin",
}

MOIS_FR = ["janvier", "février", "mars", "avril", "mai", "juin",
           "juillet", "août", "septembre", "octobre", "novembre", "décembre"]


def date_fr(d, with_day=False):
    if with_day:
        return f"{d.day} {MOIS_FR[d.month - 1]} {d.year}"
    return f"{MOIS_FR[d.month - 1]} {d.year}"


def titre_page(titre):
    return f"{titre} | {SITE_TITLE}"


# ---------------------------------------------------------------------------
# Lecture des articles Markdown (en-tête YAML + corps)
# ---------------------------------------------------------------------------

def parse_post(filepath):
    with open(filepath, encoding="utf-8") as f:
        raw = f.read()
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", raw, re.DOTALL)
    if not m:
        raise ValueError(f"En-tête manquant dans {filepath}")
    meta = yaml.safe_load(m.group(1))
    html_body = markdown.markdown(m.group(2), extensions=["extra"])
    slug = os.path.splitext(os.path.basename(filepath))[0]
    slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", slug)  # retire la date du nom de fichier
    meta["slug"] = slug
    meta["html_body"] = html_body
    if isinstance(meta["date"], str):
        meta["date"] = datetime.strptime(meta["date"], "%Y-%m-%d").date()
    return meta


def load_markdown_folder(folder):
    """Chargeur commun aux articles, actualités, La Minute Éco et L'Instant IA.
    Exclut README.md (documentation du format, pas un billet)."""
    files = sorted(glob.glob(os.path.join(folder, "*.md")), reverse=True)
    files = [f for f in files if os.path.basename(f).upper() != "README.MD"]
    items = [parse_post(f) for f in files]
    items.sort(key=lambda p: p["date"], reverse=True)
    return items


def load_all_posts():
    return load_markdown_folder(POSTS_DIR)


def _en_date(valeur):
    if isinstance(valeur, str):
        return datetime.strptime(valeur, "%Y-%m-%d").date()
    return valeur


def load_evenements():
    """Événements triés du plus proche au plus lointain."""
    items = load_markdown_folder(EVENEMENTS_DIR)
    for e in items:
        e["date"] = _en_date(e["date"])
        e["date_fin"] = _en_date(e.get("date_fin") or e["date"])
        if e.get("verifie_le"):
            e["verifie_le"] = _en_date(e["verifie_le"])
    items.sort(key=lambda e: e["date"])
    return items


def load_all_actualites():
    return load_markdown_folder(ACTUALITES_DIR)


# ---------------------------------------------------------------------------
# Gabarits HTML (chaînes Python, sans moteur de gabarits externe)
# ---------------------------------------------------------------------------

HEAD = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="icon" type="image/png" sizes="32x32" href="{root}assets/favicon-32.png">
<link rel="icon" type="image/png" sizes="16x16" href="{root}assets/favicon-16.png">
<link rel="apple-touch-icon" sizes="180x180" href="{root}assets/apple-touch-icon.png">
<link rel="icon" type="image/png" sizes="192x192" href="{root}assets/favicon-192.png">
<meta name="theme-color" content="#3D171D">
<link rel="preload" href="{root}assets/fonts/source-serif-4.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{root}assets/fonts/source-sans-3.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{root}assets/style.css">
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Récade Finance",
  "url": "https://recade-finance.com",
  "logo": "https://recade-finance.com/assets/favicon-512.png",
  "description": "Finance, économie et IA : un regard africain.",
  "sameAs": [
    "https://instagram.com/recadefinance"
  ]
}}
</script>
</head>
<body>
"""

FOOTER_HTML = """
<footer class="site">
  <div class="footer-inner">
    <div class="footer-brand">
      <img src="{root}assets/logo-recade-finance-entete-clair.svg" alt="Récade Finance" class="footer-logo" width="188" height="56">
      <p class="footer-tagline">{footer_tagline}</p>
    </div>
    <div class="footer-cols">
      <div class="footer-col">
        <h4>Explorer</h4>
        <a href="{root}analyses.html">Analyses</a>
        <a href="{root}actualites.html">Actualités</a>
        <a href="{root}evenements.html">Événements</a>
        <a href="{root}minute-eco.html">La Minute Éco</a>
        <a href="{root}instant-ia.html">L'Instant IA</a>{footer_tribune}
        <a href="{root}assistant-umoa.html">Assistant UMOA</a>
        <a href="{root}a-propos.html">À propos</a>
      </div>
      <div class="footer-col">
        <h4>Contact</h4>
        <a href="https://{footer_website}">{footer_website}</a>
        <a href="https://instagram.com/recadefinance">{footer_instagram}</a>
        <a href="mailto:{footer_email}">{footer_email}</a>
      </div>
    </div>
  </div>
  <div class="footer-disclaimer">
    <p>{site_disclaimer}</p>
  </div>
  <div class="footer-bottom">
    <span>&copy; {year} Récade Finance</span>
    <span>{footer_website}</span>
  </div>
</footer>
</body>
</html>
"""

HEADER_HTML = """
<header class="site">
  <div class="header-inner">
    <a href="{root}index.html" class="brand" aria-label="Récade Finance, accueil">
      <img src="{root}assets/logo-recade-finance-entete.svg" alt="Récade Finance" class="brand-logo" width="174" height="52">
    </a>
    <nav class="main-nav" id="rf-main-nav">
      <a href="{root}index.html">Accueil</a>
      <a href="{root}analyses.html">Analyses</a>
      <a href="{root}actualites.html">Actualités</a>
      <a href="{root}evenements.html">Événements</a>
      <a href="{root}minute-eco.html">La Minute Éco</a>
      <a href="{root}instant-ia.html">L'Instant IA</a>{nav_tribune}
      <a href="{root}a-propos.html">À propos</a>
    </nav>
    <div class="header-actions">
      <a href="{root}index.html#newsletter" class="btn btn-petit">S'abonner</a>
      <button class="nav-toggle" id="rf-nav-toggle" aria-label="Ouvrir le menu" aria-expanded="false">&#9776;</button>
    </div>
  </div>
</header>
<script>
(function() {{
  var toggle = document.getElementById('rf-nav-toggle');
  var nav = document.getElementById('rf-main-nav');
  if (toggle && nav) {{
    toggle.addEventListener('click', function() {{
      var isOpen = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    }});
  }}
}})();
</script>
"""


def render_header(root=""):
    nav_tribune = f'\n      <a href="{root}index.html#tribune">Tribune</a>' if SECTIONS_ACTIVES.get("tribune") else ""
    return HEADER_HTML.format(root=root, nav_tribune=nav_tribune)


def render_footer(root=""):
    f = CONTENT["footer"]
    footer_tribune = f'\n        <a href="{root}index.html#tribune">Tribune</a>' if SECTIONS_ACTIVES.get("tribune") else ""
    return FOOTER_HTML.format(
        root=root, year=datetime.now().year,
        footer_tagline=f["tagline"], footer_email=f["email"], footer_instagram=f["instagram"],
        footer_website=f.get("website", "recade-finance.com"),
        footer_tribune=footer_tribune,
        site_disclaimer=CONTENT.get("site_disclaimer_short", ""),
    )


def render_entree(post, root=""):
    cat_label = CATEGORY_LABELS.get(post.get("category", "analyses"), post.get("category", ""))
    lien = f"{root}articles/{post['slug']}.html"
    return f"""
      <article class="entree">
        <p class="meta">{cat_label}, {date_fr(post['date'], with_day=True)}</p>
        <h3><a href="{lien}">{post['title']}</a></h3>
        <p>{post['excerpt']}</p>
        <a href="{lien}" class="lien">Lire l'analyse</a>
      </article>"""


def accroche_de(item):
    """Phrase d'accroche d'une tuile : champ accroche, sinon extrait, sinon début du texte."""
    if item.get("accroche"):
        return item["accroche"]
    if item.get("excerpt"):
        return item["excerpt"]
    texte = re.sub(r"<[^>]+>", " ", item.get("html_body", ""))
    texte = re.sub(r"\s+", " ", texte).strip()
    return (texte[:150].rsplit(" ", 1)[0] + "...") if len(texte) > 150 else texte


def render_couverture(item, root=""):
    """Visuel de couverture : image si elle est fournie, sinon visuel typographique à la charte."""
    if item.get("image"):
        alt = item.get("image_alt", "")
        return f'<div class="couverture"><img src="{root}{item["image"]}" alt="{alt}" loading="lazy"></div>'
    visuel = item.get("visuel")
    legende = item.get("visuel_legende", "")
    if visuel:
        leg = f'<span class="couv-legende">{legende}</span>' if legende else ""
        return f'<div class="couverture couv-texte" aria-hidden="true"><span class="couv-chiffre">{visuel}</span>{leg}</div>'
    return (f'<div class="couverture couv-defaut" aria-hidden="true">'
            f'<img src="{root}assets/monogramme-recade-finance.png" alt="" width="64" height="64"></div>')


def render_tuile(item, lien, etiquette, root=""):
    return f"""
      <li>
        <a class="tuile" href="{lien}">
          {render_couverture(item, root)}
          <p class="meta">{etiquette}, {date_fr(item['date'], with_day=True)}</p>
          <h3>{item['title']}</h3>
          <p class="accroche">{accroche_de(item)}</p>
        </a>
      </li>"""


def render_grille(items, lien_de, etiquette_de, root=""):
    return '<ul class="grille">' + "".join(render_tuile(i, lien_de(i), etiquette_de(i), root) for i in items) + "\n    </ul>"


def etiquette_analyse(post):
    return CATEGORY_LABELS.get(post.get("category", "analyses"), post.get("category", "Analyse"))


def render_brvm_widget():
    date = BRVM.get("date_cloture", "")
    lignes = ""
    for idx in BRVM.get("indices", []):
        lignes += f"""
        <tr><td>{idx['nom']}</td><td class="num">{idx['valeur']}</td><td class="num">{idx['variation']}</td></tr>"""
    details = ""
    for d in BRVM.get("indicateurs_desagreges", []):
        details += f"""
        <tr><td>{d['label']}</td><td>{d['valeur']}</td><td>{d['detail']}</td></tr>"""
    detail_html = f"""
    <table class="detail">
      <tbody>{details}
      </tbody>
    </table>""" if details else ""
    interpretation = BRVM.get("interpretation", "")
    interpretation_html = f'<p class="interpretation">{interpretation}</p>' if interpretation else ""
    return f"""
<section class="section marche" id="marche">
  <div class="wrap">
    <h2>Marché BRVM</h2>
    <p class="meta">Clôture du {date}</p>
    <table>
      <thead><tr><th>Indice</th><th class="num">Niveau</th><th class="num">Variation</th></tr></thead>
      <tbody>{lignes}
      </tbody>
    </table>{detail_html}
    {interpretation_html}
    <p class="source">{BRVM.get('source_label', '')}. <a href="https://www.brvm.org/fr/indices" target="_blank" rel="noopener">Voir en direct sur brvm.org</a></p>
  </div>
</section>
"""


def render_home_pilote():
    b = CONTENT.get("home_banner_pilote")
    if not b:
        return ""
    return f"""
<section class="section pilote-accueil">
  <div class="wrap">
    <h2>{_e(b['title'])}</h2>
    <p>{_e(b['text'])}</p>
    <a href="assistant-umoa.html" class="btn">{_e(b['cta_label'])}</a>
  </div>
</section>"""


def render_tribune_section():
    """Rubrique désaffichée (voir SECTIONS_ACTIVES). Le contenu reste dans site_content.yaml."""
    if not SECTIONS_ACTIVES.get("tribune"):
        return ""
    t = CONTENT["tribune"]
    return f"""
<section class="section" id="tribune">
  <div class="wrap">
    <h2>{t['title']}</h2>
    <h3>{t['card_title']}</h3>
    <p>{t['card_text']}</p>
  </div>
</section>"""


def render_homepage(posts, actualites=(), evenements=()):
    featured_project = next((p for p in posts if p.get("featured")), None)
    remaining = [p for p in posts if p is not featured_project]
    dernieres = remaining[:6]
    grille_html = render_grille(dernieres, lambda p: f"articles/{p['slug']}.html", etiquette_analyse)
    toutes_html = '<p><a href="analyses.html" class="lien">Toutes les analyses</a></p>' if len(remaining) > 6 else ""
    bande_events = ""
    prochains = [e for e in evenements if e["date_fin"] >= datetime.now().date()][:3]
    if prochains:
        lignes_ev = "".join(render_evenement_ligne(e) for e in prochains)
        bande_events = f"""
<section class="section" id="evenements">
  <div class="wrap">
    <h2>Prochains événements</h2>
    <ul class="agenda">{lignes_ev}
    </ul>
    <p><a href="evenements.html" class="lien">Tous les événements</a></p>
  </div>
</section>"""
    bande_actus = ""
    if actualites:
        grille_actus = render_grille(list(actualites)[:3], lambda a: f"actualites/{a['slug']}.html", lambda a: "Actualité")
        bande_actus = f"""
<section class="section" id="actualites">
  <div class="wrap">
    <h2>Dernières actualités</h2>
    {grille_actus}
    <p><a href="actualites.html" class="lien">Toutes les actualités</a></p>
  </div>
</section>"""

    featured_project_block = ""
    if featured_project:
        featured_project_block = f"""
<section class="section" id="souverain-ia">
  <div class="wrap">
    <h2>{featured_project['title']}</h2>
    <p>{featured_project['excerpt']}</p>
    <a href="articles/{featured_project['slug']}.html" class="btn">Lire le livre blanc</a>
  </div>
</section>"""

    html = HEAD.format(
        title=titre_page(SITE_TAGLINE),
        description=SITE_TAGLINE,
        root="",
    )
    html += render_header("")
    h = CONTENT["hero"]
    n = CONTENT["newsletter"]
    html += f"""
<section class="hero">
  <div class="wrap">
    <h1>{h['title']}</h1>
    <p class="lede">{h['lede']}</p>
    <a href="#articles" class="btn">{h['cta_label']}</a>
  </div>
</section>

<section class="section" id="articles">
  <div class="wrap">
    <h2>Dernières analyses</h2>
    {grille_html}
    {toutes_html}
  </div>
</section>

{bande_actus}

{bande_events}

{featured_project_block}

{render_home_pilote()}

{render_brvm_widget() if SECTIONS_ACTIVES.get('brvm') else ''}

{render_tribune_section()}

<section class="section abonnement" id="newsletter">
  <div class="wrap">
    <h2>{n.get('title', 'Recevoir les analyses')}</h2>
    <p>{n.get('text', '')}</p>
    <form id="abonnement-form" action="https://gmail.us6.list-manage.com/subscribe/post?u=0727619b3152a006e7015d1c8&amp;id=cd759a0ccc&amp;f_id=00e6c2e1f0" method="post" class="subscribe-form" target="_blank">
      <input type="email" name="EMAIL" placeholder="votre@email.com" aria-label="Adresse email" autocomplete="email" required>
      <div aria-hidden="true" style="position: absolute; left: -5000px;">
        <input type="text" name="b_0727619b3152a006e7015d1c8_cd759a0ccc" tabindex="-1" value="">
      </div>
      <!-- Piège anti-bot : champ invisible pour un humain, souvent rempli
           aveuglément par les robots qui scannent les formulaires publics. -->
      <div aria-hidden="true" style="position:absolute; left:-9999px; top:-9999px;">
        <label for="rf-site-web">Ne pas remplir ce champ</label>
        <input type="text" id="rf-site-web" name="site_web" tabindex="-1" autocomplete="off">
      </div>
      <button class="btn" type="submit">{n['cta_label']}</button>
    </form>
    <p class="statut" id="abonnement-statut" role="status" aria-live="polite"></p>
    <p class="mention">{n.get('mention', '')}</p>
  </div>
</section>
"""
    html += newsletter_script(n)
    html += render_footer(root="")
    return html



NEWSLETTER_SCRIPT = """
<script>
(function() {
  var form = document.getElementById('abonnement-form');
  var statut = document.getElementById('abonnement-statut');
  if (!form || !statut) { return; }
  var MESSAGE_SUCCES = __SUCCES__;
  var MESSAGE_ERREUR = __ERREUR__;
  var MESSAGE_DEJA = __DEJA__;
  form.addEventListener('submit', function(evt) {
    evt.preventDefault();
    if (form.querySelector('#rf-site-web').value !== '') { return; }
    var email = form.querySelector('input[name="EMAIL"]').value.trim();
    var piege = form.querySelector('input[name^="b_"]');
    var bouton = form.querySelector('button');
    var rappel = 'rfMc' + Date.now();
    var balise = document.createElement('script');
    var fini = false;
    var delai;
    function terminer(message, reussi) {
      if (fini) { return; }
      fini = true;
      clearTimeout(delai);
      window[rappel] = function() {};
      if (balise.parentNode) { balise.parentNode.removeChild(balise); }
      statut.textContent = message;
      bouton.disabled = false;
      if (reussi) { form.reset(); }
    }
    window[rappel] = function(reponse) {
      var msg = reponse && reponse.msg ? String(reponse.msg) : '';
      if (reponse && reponse.result === 'success') { terminer(MESSAGE_SUCCES, true); }
      else if (/already subscribed|déjà abonn/i.test(msg)) { terminer(MESSAGE_DEJA, false); }
      else { terminer(MESSAGE_ERREUR, false); }
    };
    bouton.disabled = true;
    statut.textContent = 'Envoi en cours…';
    delai = setTimeout(function() { terminer(MESSAGE_ERREUR, false); }, 12000);
    balise.onerror = function() { terminer(MESSAGE_ERREUR, false); };
    balise.src = form.action.replace('/subscribe/post?', '/subscribe/post-json?') +
      '&EMAIL=' + encodeURIComponent(email) + '&' + encodeURIComponent(piege.name) + '=&c=' + rappel;
    document.body.appendChild(balise);
  });
})();
</script>
"""


def newsletter_script(n):
    import json
    return (NEWSLETTER_SCRIPT
            .replace("__SUCCES__", json.dumps(n.get("success_message", "Merci pour votre inscription."), ensure_ascii=False))
            .replace("__ERREUR__", json.dumps(n.get("error_message", "L'inscription n'a pas abouti."), ensure_ascii=False))
            .replace("__DEJA__", json.dumps(n.get("already_message", "Cette adresse est déjà abonnée."), ensure_ascii=False)))


def render_abonnement_confirme():
    n = CONTENT["newsletter"]
    html = HEAD.format(title=titre_page(n["confirmed_title"]), description=SITE_TAGLINE, root="")
    html = html.replace("</head>", '<meta name="robots" content="noindex">' + chr(10) + "</head>", 1)
    html += render_header("")
    html += f"""
<section class="page-titre">
  <div class="wrap etroit">
    <h1>{n['confirmed_title']}</h1>
  </div>
</section>
<section class="section" style="border-top:0; padding-top:24px;">
  <div class="wrap etroit">
    <p>{n['confirmed_text']}</p>
    <p><a href="index.html">Retour à l'accueil</a></p>
  </div>
</section>
"""
    html += render_footer(root="")
    return html


def render_analyses_page(posts):
    description = "Analyses de fond sur la finance, l'économie, la dette souveraine et l'intelligence artificielle en Afrique."
    html = HEAD.format(title=titre_page("Analyses"), description=description, root="")
    html += render_header("")
    corps = render_grille(posts, lambda p: f"articles/{p['slug']}.html", etiquette_analyse) if posts else \
        '<p class="vide">Aucune analyse publiée pour le moment. Revenez bientôt.</p>'
    html += f"""
<section class="page-titre">
  <div class="wrap">
    <h1>Analyses</h1>
    <p class="page-intro">{description}</p>
  </div>
</section>
<section class="section" style="border-top:0; padding-top:24px;">
  <div class="wrap">
    {corps}
  </div>
</section>
"""
    html += render_footer(root="")
    return html


def render_article(post):
    html = HEAD.format(
        title=titre_page(post["title"]),
        description=post["excerpt"],
        root="../",
    )
    html += render_header("../")
    cat_label = CATEGORY_LABELS.get(post.get("category", "analyses"), post.get("category", ""))
    # La bannière (banner_image) reste dans les fichiers sources mais n'est plus affichée.
    html += f"""
<article class="section article-single" style="border-top:0;">
  <div class="wrap etroit">
    <p class="meta article-meta">{cat_label}, {date_fr(post['date'], with_day=True)}</p>
    <h1>{post['title']}</h1>
    <div class="article-body">
      {post['html_body']}
    </div>
  </div>
</article>
"""
    html += render_footer(root="../")
    return html


def render_video_embed(video_url):
    """Accepte soit un lien YouTube, soit un chemin vers un fichier vidéo
    local (mp4) placé dans /assets."""
    if not video_url:
        return ""
    if "youtube.com" in video_url or "youtu.be" in video_url:
        vid_id = ""
        if "youtu.be/" in video_url:
            vid_id = video_url.split("youtu.be/")[-1].split("?")[0]
        elif "watch?v=" in video_url:
            vid_id = video_url.split("watch?v=")[-1].split("&")[0]
        embed_src = f"https://www.youtube.com/embed/{vid_id}"
        return f"""
        <div class="video-embed-wrapper">
          <iframe src="{embed_src}" title="Vidéo" frameborder="0"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowfullscreen></iframe>
        </div>"""
    return f"""
        <div class="video-embed-wrapper">
          <video src="{video_url}" controls></video>
        </div>"""


def render_contributor_item(item, root=""):
    author_name = item.get("author_name", "")
    author_title = item.get("author_title", "")
    byline_html = ""
    if author_name:
        titre = f", {author_title}" if author_title else ""
        byline_html = f'<p class="byline"><strong>{author_name}</strong>{titre}</p>'

    video_url = item.get("video_url", "")
    video_html = render_video_embed(f"{root}{video_url}" if video_url and not video_url.startswith("http") else video_url)

    return f"""
      <article class="actu-item">
        <p class="meta">{date_fr(item['date'], with_day=True)}</p>
        <h3>{item['title']}</h3>
        {video_html}
        <div class="actu-body">{item['html_body']}</div>
        {byline_html}
      </article>"""


def render_contributor_page(items, page_title, intro_text, description):
    html = HEAD.format(title=titre_page(page_title), description=description, root="")
    html += render_header("")
    items_html = "\n".join(render_contributor_item(i) for i in items) if items else \
        '<p class="vide">Aucun billet publié pour le moment. Le premier arrive bientôt.</p>'
    html += f"""
<section class="page-titre">
  <div class="wrap etroit">
    <h1>{page_title}</h1>
    <p class="page-intro">{intro_text}</p>
  </div>
</section>
<section class="section" style="border-top:0; padding-top:24px;">
  <div class="wrap etroit">
    <div class="actu-list">
      {items_html}
    </div>
  </div>
</section>
"""
    html += render_footer(root="")
    return html


def render_actualite_page(item):
    sujets = ", ".join(item.get("tags", []))
    sujets_html = f'<span class="sujets">{sujets}</span>' if sujets else ""
    source = item.get("source", "")
    source_url = item.get("source_url", "")
    source_html = (f'<p class="actu-source"><a href="{source_url}" target="_blank" rel="noopener">Source : {source}</a></p>'
                   if source else "")
    html = HEAD.format(title=titre_page(item["title"]), description=accroche_de(item), root="../")
    if item.get("image_partage"):
        from html import escape as echapper
        og = (f'<meta property="og:type" content="article">\n'
              f'<meta property="og:title" content="{echapper(titre_page(item["title"]), quote=True)}">\n'
              f'<meta property="og:description" content="{echapper(accroche_de(item), quote=True)}">\n'
              f'<meta property="og:url" content="{SITE_URL}/actualites/{item["slug"]}.html">\n'
              f'<meta property="og:image" content="{SITE_URL}/{item["image_partage"]}">\n'
              f'<meta name="twitter:card" content="summary_large_image">\n')
        html = html.replace("</head>", og + "</head>", 1)
    html += render_header("../")
    html += f"""
<article class="section article-single" style="border-top:0;">
  <div class="wrap etroit">
    <p class="meta article-meta"><a href="../actualites.html" class="retour">Toutes les actualités</a></p>
    <p class="meta article-meta">Actualité, {date_fr(item['date'], with_day=True)}{sujets_html}</p>
    <h1>{item['title']}</h1>
    <div class="article-body">
      {item['html_body']}
    </div>
    {source_html}
  </div>
</article>
"""
    html += render_footer(root="../")
    return html


def render_actualites_page(actualites):
    description = "Veille régulière sur la finance, l'économie, et l'intelligence artificielle en Afrique."
    html = HEAD.format(title=titre_page("Actualités"), description=description, root="")
    html += render_header("")
    corps = render_grille(actualites, lambda a: f"actualites/{a['slug']}.html", lambda a: "Actualité") if actualites else \
        '<p class="vide">Aucune actualité publiée pour le moment. Revenez bientôt.</p>'
    html += f"""
<section class="page-titre">
  <div class="wrap">
    <h1>Actualités</h1>
    <p class="page-intro">{description}</p>
  </div>
</section>
<section class="section" style="border-top:0; padding-top:24px;">
  <div class="wrap">
    {corps}
  </div>
</section>
"""
    html += render_footer(root="")
    return html


def plage_dates(debut, fin):
    if fin == debut:
        return date_fr(debut, with_day=True)
    if (debut.year, debut.month) == (fin.year, fin.month):
        liaison = "et" if fin.day == debut.day + 1 else "au"
        return f"{debut.day} {liaison} {fin.day} {MOIS_FR[fin.month - 1]} {fin.year}"
    return f"{debut.day} {MOIS_FR[debut.month - 1]} au {fin.day} {MOIS_FR[fin.month - 1]} {fin.year}"


def lieu_evenement(ev, complet=False):
    morceaux = [ev.get("ville"), ev.get("pays")]
    texte = ", ".join(x for x in morceaux if x)
    if complet and ev.get("lieu"):
        texte = f"{ev['lieu']}, {texte}" if texte else ev["lieu"]
    return texte


def render_evenement_ligne(ev, root=""):
    lien = f"{root}evenements/{ev['slug']}.html"
    themes = ", ".join(ev.get("themes", []))
    themes_html = f'<p class="meta">{themes}</p>' if themes else ""
    a_confirmer = ' <span class="ev-statut">à confirmer</span>' if ev.get("statut") == "à confirmer" else ""
    return f"""
      <li class="evenement" data-fin="{ev['date_fin'].isoformat()}">
        <p class="ev-date">{plage_dates(ev['date'], ev['date_fin'])}</p>
        <div class="ev-corps">
          <h3><a href="{lien}">{ev['title']}</a>{a_confirmer}</h3>
          <p class="meta">{lieu_evenement(ev, complet=True)}</p>
          <p class="accroche">{accroche_de(ev)}</p>
          {themes_html}
        </div>
      </li>"""


AGENDA_SCRIPT = """
<script>
(function() {
  var auj = new Date().toISOString().slice(0, 10);
  var avenir = document.getElementById('agenda-avenir');
  var passe = document.getElementById('agenda-passe');
  if (!avenir || !passe) { return; }
  Array.prototype.slice.call(avenir.querySelectorAll('li[data-fin]')).forEach(function(li) {
    if (li.getAttribute('data-fin') < auj) { passe.insertBefore(li, passe.firstChild); }
  });
  var vide = document.getElementById('agenda-vide');
  if (vide) { vide.hidden = avenir.children.length > 0; }
  var bloc = document.getElementById('agenda-passe-bloc');
  if (bloc) { bloc.hidden = passe.children.length === 0; }
})();
</script>
"""


def render_evenements_page(evenements):
    description = "Les prochains événements majeurs en économie, finance et intelligence artificielle au Bénin et en Afrique de l'Ouest."
    aujourdhui = datetime.now().date()
    avenir = [e for e in evenements if e["date_fin"] >= aujourdhui]
    passes = [e for e in evenements if e["date_fin"] < aujourdhui][::-1]
    html = HEAD.format(title=titre_page("Événements"), description=description, root="")
    html += render_header("")
    lignes_avenir = "".join(render_evenement_ligne(e) for e in avenir)
    lignes_passes = "".join(render_evenement_ligne(e) for e in passes)
    vide_cache = " hidden" if avenir else ""
    passe_cache = "" if passes else " hidden"
    html += f"""
<section class="page-titre">
  <div class="wrap etroit">
    <h1>Événements</h1>
    <p class="page-intro">{description}</p>
  </div>
</section>
<section class="section" style="border-top:0; padding-top:24px;">
  <div class="wrap etroit">
    <h2>À venir</h2>
    <p class="vide" id="agenda-vide"{vide_cache}>Aucun événement à venir pour le moment. Revenez bientôt.</p>
    <ul class="agenda" id="agenda-avenir">{lignes_avenir}
    </ul>
    <div id="agenda-passe-bloc"{passe_cache}>
      <h2 class="agenda-titre-passe">Événements passés</h2>
      <ul class="agenda agenda-passe" id="agenda-passe">{lignes_passes}
      </ul>
    </div>
    <p class="ev-mention">Informations relevées auprès des organisateurs et vérifiées à la date indiquée sur chaque fiche. Vérifiez toujours les dates et les conditions d'accès sur le site officiel avant de vous déplacer.</p>
  </div>
</section>
"""
    html += AGENDA_SCRIPT
    html += render_footer(root="")
    return html


def render_evenement_page(ev):
    infos = [("Dates", plage_dates(ev["date"], ev["date_fin"])),
             ("Lieu", lieu_evenement(ev, complet=True)),
             ("Organisateur", ev.get("organisateur", "")),
             ("Thèmes", ", ".join(ev.get("themes", []))),
             ("Accès", ev.get("acces", "")),
             ("Tarif", ev.get("tarif", ""))]
    if ev.get("lien"):
        infos.append(("Site officiel", f'<a href="{ev["lien"]}" target="_blank" rel="noopener">{ev["lien"].replace("https://", "").rstrip("/")}</a>'))
    infos_html = "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in infos if v)
    note = ""
    if ev.get("statut") == "à confirmer":
        note = '<p class="ev-note">Les informations de cet événement sont à confirmer auprès des organisateurs.</p>'
    verif = ""
    if ev.get("verifie_le"):
        src = f", d'après {ev['source']}" if ev.get("source") else ""
        verif = f'<p class="meta">Informations vérifiées le {date_fr(ev["verifie_le"], with_day=True)}{src}.</p>'
    jsonld = {
        "@context": "https://schema.org", "@type": "Event", "name": ev["title"],
        "startDate": ev["date"].isoformat(), "endDate": ev["date_fin"].isoformat(),
        "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
        "location": {"@type": "Place", "name": ev.get("lieu", ""),
                     "address": {"@type": "PostalAddress", "addressLocality": ev.get("ville", ""), "addressCountry": ev.get("pays", "")}},
        "description": accroche_de(ev),
    }
    if ev.get("organisateur"):
        jsonld["organizer"] = {"@type": "Organization", "name": ev["organisateur"]}
    if ev.get("lien"):
        jsonld["url"] = ev["lien"]
    import json
    html = HEAD.format(title=titre_page(ev["title"]), description=accroche_de(ev), root="../")
    if ev.get("image_partage"):
        from html import escape as echapper
        og = (f'<meta property="og:type" content="website">\n'
              f'<meta property="og:title" content="{echapper(titre_page(ev["title"]), quote=True)}">\n'
              f'<meta property="og:description" content="{echapper(accroche_de(ev), quote=True)}">\n'
              f'<meta property="og:url" content="{SITE_URL}/evenements/{ev["slug"]}.html">\n'
              f'<meta property="og:image" content="{SITE_URL}/{ev["image_partage"]}">\n'
              f'<meta name="twitter:card" content="summary_large_image">\n')
        html = html.replace("</head>", og + "</head>", 1)
    html += render_header("../")
    html += f"""
<article class="section article-single" style="border-top:0;">
  <div class="wrap etroit">
    <p class="meta article-meta"><a href="../evenements.html" class="retour">Tous les événements</a></p>
    <p class="meta article-meta">Événement</p>
    <h1>{ev['title']}</h1>
    {note}
    <dl class="ev-infos">{infos_html}</dl>
    <div class="article-body">
      {ev['html_body']}
    </div>
    {verif}
  </div>
</article>
<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>
"""
    html += render_footer(root="../")
    return html


def render_about():
    a = CONTENT["about_page"]
    v = CONTENT["video_section"]
    html = HEAD.format(title=titre_page("À propos"), description=SITE_TAGLINE, root="")
    html += render_header("")
    disclaimer_html = f'<p class="petit">{a["disclaimer"]}</p>' if a.get("disclaimer") else ""
    html += f"""
<section class="page-titre">
  <div class="wrap etroit">
    <h1>Récade Finance</h1>
  </div>
</section>
<section class="section" style="border-top:0; padding-top:24px;">
  <div class="wrap etroit">
    <p class="citation">{a['intro_quote']}</p>
    <p>{a['paragraph_1']}</p>
    <p>{a['paragraph_2']}</p>
    {('<p>' + a['paragraph_3'] + '</p>') if a.get('paragraph_3') else ''}
    {disclaimer_html}
  </div>
</section>
<section class="section video-projet">
  <div class="wrap etroit">
    <h2>{v['title']}</h2>
    <p>{v['text']}</p>
    <video src="assets/recade_finance_teaser.mp4" controls preload="metadata" playsinline></video>
  </div>
</section>
"""
    html += render_footer(root="")
    return html


# ---------------------------------------------------------------------------
# Assistant réglementaire UMOA : page d'inscription au pilote
# ---------------------------------------------------------------------------

PILOTE_FONCTIONS = [
    "Risk manager",
    "Conformité, contrôle permanent",
    "Audit interne ou externe",
    "Consultant",
    "Direction financière, comptabilité",
    "Supervision, institution publique",
    "Enseignant, chercheur, étudiant",
    "Autre",
]
PILOTE_ETABLISSEMENTS = [
    "Banque",
    "Établissement financier à caractère bancaire",
    "Système financier décentralisé (SFD)",
    "Cabinet d'audit ou de conseil",
    "Institution publique ou régionale",
    "École, université",
    "Autre",
]
PILOTE_PAYS = [
    "Bénin", "Burkina Faso", "Côte d'Ivoire", "Guinée-Bissau",
    "Mali", "Niger", "Sénégal", "Togo", "Hors UEMOA",
]
PILOTE_THEMES = [
    "Fonds propres et solvabilité",
    "Risque de crédit (approche standard)",
    "Division des risques",
    "Créances en souffrance et provisionnement",
    "Plan comptable bancaire révisé",
    "Comparaison UE et UMOA (CRR, IFRS 9)",
]
PILOTE_FREQUENCES = ["Chaque jour", "Chaque semaine", "Ponctuellement"]


def _e(texte):
    """Échappe un texte pour l'insérer dans du HTML (contenu ou attribut)."""
    return html_lib.escape(str(texte), quote=True)


def _options(valeurs):
    return "\n".join(f'          <option value="{_e(v)}">{_e(v)}</option>' for v in valeurs)


def _cases(nom, valeurs, type_case):
    return "\n".join(
        f'        <label class="pf-check"><input type="{type_case}" name="{nom}" value="{_e(v)}"> {_e(v)}</label>'
        for v in valeurs
    )


PILOTE_SCRIPT = """
<script>
(function() {
  var form = document.getElementById('pilote-form');
  var statut = document.getElementById('pf-status');
  if (!form || !statut) { return; }
  var MESSAGE_SUCCES = form.getAttribute('data-succes');
  form.addEventListener('submit', function(evt) {
    evt.preventDefault();
    if (form.querySelector('#pf-gotcha').value !== '') { return; }
    if (form.action.indexOf('A_REMPLACER') !== -1) {
      statut.className = 'pf-status pf-erreur';
      statut.textContent = "Le formulaire n'est pas encore activé. Écrivez-nous à contact.recadefinance@gmail.com.";
      return;
    }
    var donnees = new FormData(form);
    var themes = donnees.getAll('themes');
    donnees.delete('themes');
    donnees.append('themes', themes.join(', '));
    var bouton = form.querySelector('.pf-submit');
    bouton.disabled = true;
    statut.className = 'pf-status';
    statut.textContent = 'Envoi en cours…';
    fetch(form.action, { method: 'POST', body: donnees, headers: { 'Accept': 'application/json' } })
      .then(function(reponse) {
        if (!reponse.ok) { throw new Error('envoi refusé'); }
        form.reset();
        statut.className = 'pf-status pf-succes';
        statut.textContent = MESSAGE_SUCCES;
      })
      .catch(function() {
        statut.className = 'pf-status pf-erreur';
        statut.textContent = "L'envoi n'a pas abouti. Réessayez ou écrivez-nous à contact.recadefinance@gmail.com.";
      })
      .then(function() { bouton.disabled = false; });
  });
})();
</script>
"""


def render_pilote_page():
    c = CONTENT["pilote_page"]
    html = HEAD.format(
        title=titre_page(f"{c['title']} (pilote)"),
        description=_e(c["lede"]),
        root="",
    )
    html += render_header("")
    html += f"""
<section class="hero">
  <div class="wrap">
    <h1>{_e(c['title'])}</h1>
    <p class="lede">{_e(c['lede'])}</p>
    <a href="#inscription" class="btn">{_e(c['cta_label'])}</a>
    <div class="stats">
      <div class="stat"><span class="num">{_e(c['stat_1'])}</span><span class="label">{_e(c['stat_1_label'])}</span></div>
      <div class="stat"><span class="num">{_e(c['stat_2'])}</span><span class="label">{_e(c['stat_2_label'])}</span></div>
      <div class="stat"><span class="num">{_e(c['stat_3'])}</span><span class="label">{_e(c['stat_3_label'])}</span></div>
    </div>
    <p class="stats-note">{_e(c['stats_note'])}</p>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <h2>Ce que l'assistant fait pour vous</h2>
    <div class="colonnes">
      <div><h3>Une réponse sourcée</h3><p>Chaque affirmation renvoie à un article ou un paragraphe précis du dispositif prudentiel, du PCB révisé ou des instructions de la BCEAO.</p></div>
      <div><h3>Des calculs exacts</h3><p>Pondérations, ratios de solvabilité, division des risques et provisions sont calculés par des fonctions testées, pas « de tête ».</p></div>
      <div><h3>Des limites annoncées</h3><p>Quand le texte ne répond pas, l'assistant le dit et indique ce qu'il faudrait vérifier, au lieu d'extrapoler.</p></div>
    </div>
    <div class="exemple">
      <p class="titre-exemple">Exemple de question</p>
      <p class="question">« Un crédit de 200 millions FCFA, impayé depuis 120 jours, est garanti par une hypothèque : quel classement, et quelle provision ? »</p>
      <p>L'assistant classe la créance en douteuse, distingue la part couverte et la part non couverte, donne les taux minimaux de dépréciation et cite l'instruction n° 026-11-2016 (art. 8 et 16).</p>
    </div>
  </div>
</section>

<section class="section" id="inscription">
  <div class="wrap form-wrap">
    <div>
      <h2>Rejoindre le pilote</h2>
      <p>{_e(c['form_intro'])}</p>
      <ol>
        <li>Vous remplissez ce formulaire (2 minutes).</li>
        <li>Nous vous envoyons un accès et un guide de prise en main.</li>
        <li>Vous posez vos vraies questions et signalez les erreurs en un clic.</li>
      </ol>
    </div>

    <form id="pilote-form" class="pilote-form" action="{_e(c['form_action'])}" method="POST" data-succes="{_e(c['success_message'])}">
      <input type="hidden" name="_subject" value="Inscription au pilote : Assistant réglementaire UMOA">
      <div class="pf-trap" aria-hidden="true">
        <label for="pf-gotcha">Ne pas remplir ce champ</label>
        <input type="text" id="pf-gotcha" name="_gotcha" tabindex="-1" autocomplete="off">
      </div>

      <div class="pf-row">
        <div class="pf-field">
          <label for="pf-nom">Prénom et nom <span class="pf-req">*</span></label>
          <input id="pf-nom" name="nom" type="text" autocomplete="name" required>
        </div>
        <div class="pf-field">
          <label for="pf-email">Email professionnel <span class="pf-req">*</span></label>
          <input id="pf-email" name="email" type="email" autocomplete="email" required>
        </div>
      </div>

      <div class="pf-row">
        <div class="pf-field">
          <label for="pf-fonction">Fonction <span class="pf-req">*</span></label>
          <select id="pf-fonction" name="fonction" required>
          <option value="">Choisir…</option>
{_options(PILOTE_FONCTIONS)}
          </select>
        </div>
        <div class="pf-field">
          <label for="pf-type">Type d'établissement <span class="pf-req">*</span></label>
          <select id="pf-type" name="type_etablissement" required>
          <option value="">Choisir…</option>
{_options(PILOTE_ETABLISSEMENTS)}
          </select>
        </div>
      </div>

      <div class="pf-row">
        <div class="pf-field">
          <label for="pf-etab">Établissement <span class="pf-req">*</span></label>
          <input id="pf-etab" name="etablissement" type="text" autocomplete="organization" required>
        </div>
        <div class="pf-field">
          <label for="pf-pays">Pays <span class="pf-req">*</span></label>
          <select id="pf-pays" name="pays" required>
          <option value="">Choisir…</option>
{_options(PILOTE_PAYS)}
          </select>
        </div>
      </div>

      <fieldset class="pf-group">
        <legend>Thèmes qui vous intéressent</legend>
        <div class="pf-checks">
{_cases("themes", PILOTE_THEMES, "checkbox")}
        </div>
      </fieldset>

      <fieldset class="pf-group">
        <legend>Fréquence d'usage envisagée</legend>
        <div class="pf-checks pf-inline">
{_cases("frequence", PILOTE_FREQUENCES, "radio")}
        </div>
      </fieldset>

      <div class="pf-field">
        <label for="pf-question">Une question que vous aimeriez poser à l'assistant</label>
        <textarea id="pf-question" name="question" rows="4" placeholder="Par exemple : quelle pondération pour un prêt à une PME non notée, garanti par un dépôt ?"></textarea>
        <span class="pf-hint">Facultatif. Les questions reçues servent à tester et améliorer l'outil.</span>
      </div>

      <label class="pf-check pf-consent"><input type="checkbox" name="consentement" value="oui" required> <span>J'accepte que Récade Finance utilise ces informations pour me contacter au sujet du pilote. Elles ne sont ni vendues ni partagées. <span class="pf-req">*</span></span></label>
      <label class="pf-check"><input type="checkbox" name="newsletter" value="oui"> <span>Je souhaite aussi recevoir la lettre de Récade Finance.</span></label>

      <button type="submit" class="btn pf-submit">Envoyer ma demande</button>
      <p class="pf-status" id="pf-status" role="status" aria-live="polite"></p>
    </form>
  </div>
</section>

<section class="section">
  <div class="wrap etroit">
    <p class="petit">{_e(c['disclaimer'])}</p>
  </div>
</section>
"""
    html += PILOTE_SCRIPT
    html += render_footer(root="")
    return html


# ---------------------------------------------------------------------------
# Écriture des fichiers
# ---------------------------------------------------------------------------

def render_sitemap(posts, actualites=(), evenements=()):
    urls = ["", "assistant-umoa.html", "a-propos.html", "analyses.html", "actualites.html", "evenements.html", "minute-eco.html", "instant-ia.html"]
    urls += [f"articles/{p['slug']}.html" for p in posts]
    urls += [f"actualites/{a['slug']}.html" for a in actualites]
    urls += [f"evenements/{e['slug']}.html" for e in evenements]
    entries = "\n".join(f"  <url><loc>{SITE_URL}/{u}</loc></url>" for u in urls)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{entries}
</urlset>
"""


def render_robots():
    return f"""User-agent: *
Allow: /

Sitemap: {SITE_URL}/sitemap.xml
"""


def copier_assets():
    """Copie /assets vers /docs/assets (fichiers et sous-dossiers, dont les polices)."""
    assets_src = os.path.join(ROOT, "assets")
    assets_dst = os.path.join(DOCS_DIR, "assets")
    os.makedirs(assets_dst, exist_ok=True)
    for nom in os.listdir(assets_src):
        src = os.path.join(assets_src, nom)
        dst = os.path.join(assets_dst, nom)
        if os.path.isdir(src):
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dst)
    print(f"Assets copiés vers {assets_dst}")


def main():
    os.makedirs(DOCS_DIR, exist_ok=True)
    os.makedirs(os.path.join(DOCS_DIR, "articles"), exist_ok=True)
    os.makedirs(os.path.join(DOCS_DIR, "actualites"), exist_ok=True)
    os.makedirs(os.path.join(DOCS_DIR, "evenements"), exist_ok=True)
    copier_assets()

    posts = load_all_posts()
    print(f"{len(posts)} article(s) trouvé(s) dans /posts")
    actualites = load_all_actualites()
    print(f"{len(actualites)} actualité(s) trouvée(s) dans /actualites")
    evenements = load_evenements()
    print(f"{len(evenements)} événement(s) trouvé(s) dans /evenements")
    minute_eco = load_markdown_folder(MINUTE_ECO_DIR)
    print(f"{len(minute_eco)} billet(s) trouvé(s) dans /minute-eco")
    instant_ia = load_markdown_folder(INSTANT_IA_DIR)
    print(f"{len(instant_ia)} billet(s) trouvé(s) dans /instant-ia")

    def ecrire(chemin, contenu):
        with open(os.path.join(DOCS_DIR, chemin), "w", encoding="utf-8") as f:
            f.write(contenu)

    ecrire("index.html", render_homepage(posts, actualites, evenements))
    ecrire("a-propos.html", render_about())
    ecrire("abonnement-confirme.html", render_abonnement_confirme())
    ecrire("assistant-umoa.html", render_pilote_page())
    ecrire("minute-eco.html", render_contributor_page(
        minute_eco, "La Minute Éco",
        "Une notion économique souvent technique, expliquée simplement en quelques minutes, à l'écrit ou en vidéo.",
        "La Minute Éco : une notion économique expliquée simplement, en quelques minutes.",
    ))
    ecrire("instant-ia.html", render_contributor_page(
        instant_ia, "L'Instant IA",
        "Une notion d'intelligence artificielle souvent technique, expliquée simplement en quelques minutes, à l'écrit ou en vidéo.",
        "L'Instant IA : une notion d'IA expliquée simplement, en quelques minutes.",
    ))
    ecrire("actualites.html", render_actualites_page(actualites))
    ecrire("analyses.html", render_analyses_page(posts))
    ecrire("evenements.html", render_evenements_page(evenements))
    for ev in evenements:
        ecrire(os.path.join("evenements", f"{ev['slug']}.html"), render_evenement_page(ev))
        print(f"  evenements/{ev['slug']}.html")
    for a in actualites:
        ecrire(os.path.join("actualites", f"{a['slug']}.html"), render_actualite_page(a))
        print(f"  actualites/{a['slug']}.html")

    for post in posts:
        ecrire(os.path.join("articles", f"{post['slug']}.html"), render_article(post))
        print(f"  articles/{post['slug']}.html")

    ecrire("sitemap.xml", render_sitemap(posts, actualites, evenements))
    ecrire("robots.txt", render_robots())
    print("Site généré dans /docs, prêt à être poussé sur GitHub.")


if __name__ == "__main__":
    main()

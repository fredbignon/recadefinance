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
DOCS_DIR = os.path.join(ROOT, "docs")
CONTENT_FILE = os.path.join(ROOT, "content", "site_content.yaml")
BRVM_FILE = os.path.join(ROOT, "content", "marche_brvm.yaml")
SITE_TITLE = "Récade Finance"
SITE_TAGLINE = "Économie, finance, dette souveraine et IA : un regard africain"
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
  "description": "Économie, finance, dette souveraine et IA : un regard africain.",
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
      <img src="{root}assets/logo-recade-finance-clair.svg" alt="Récade Finance" class="footer-logo" width="188" height="56">
      <p class="footer-tagline">{footer_tagline}</p>
    </div>
    <div class="footer-cols">
      <div class="footer-col">
        <h4>Explorer</h4>
        <a href="{root}index.html#articles">Analyses</a>
        <a href="{root}actualites.html">Actualités</a>
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
      <img src="{root}assets/logo-recade-finance.svg" alt="Récade Finance" class="brand-logo" width="134" height="40">
    </a>
    <nav class="main-nav" id="rf-main-nav">
      <a href="{root}index.html">Accueil</a>
      <a href="{root}index.html#articles">Analyses</a>
      <a href="{root}actualites.html">Actualités</a>
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


def render_homepage(posts):
    featured_project = next((p for p in posts if p.get("featured")), None)
    remaining = [p for p in posts if p is not featured_project]
    entrees_html = "\n".join(render_entree(p) for p in remaining)

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
    {entrees_html}
  </div>
</section>

{featured_project_block}

{render_home_pilote()}

{render_brvm_widget() if SECTIONS_ACTIVES.get('brvm') else ''}

{render_tribune_section()}

<section class="section abonnement" id="newsletter">
  <div class="wrap">
    <h2>{n.get('title', 'Recevoir les analyses')}</h2>
    <p>{n.get('text', '')}</p>
    <form action="https://gmail.us6.list-manage.com/subscribe/post?u=0727619b3152a006e7015d1c8&amp;id=cd759a0ccc&amp;f_id=00e6c2e1f0" method="post" class="subscribe-form" target="_blank" novalidate onsubmit="return rfCheckHoneypot(this)">
      <input type="email" name="EMAIL" placeholder="votre@email.com" aria-label="Adresse email" required>
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
  </div>
</section>
<script>
function rfCheckHoneypot(form) {{
  var trap = form.querySelector('#rf-site-web');
  if (trap && trap.value !== '') {{ return false; }}
  return true;
}}
</script>
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


def render_actualite_item(item):
    sujets = ", ".join(item.get("tags", []))
    sujets_html = f'<span class="sujets">{sujets}</span>' if sujets else ""
    source = item.get("source", "")
    source_url = item.get("source_url", "")
    source_html = f'<a href="{source_url}" target="_blank" rel="noopener">Source : {source}</a>' if source else ""
    return f"""
      <article class="actu-item">
        <p class="meta">{date_fr(item['date'], with_day=True)}{sujets_html}</p>
        <h3>{item['title']}</h3>
        <div class="actu-body">{item['html_body']}</div>
        <p class="actu-source">{source_html}</p>
      </article>"""


def render_actualites_page(actualites):
    description = "Veille régulière sur la finance, la dette souveraine et l'économie africaine."
    html = HEAD.format(title=titre_page("Actualités"), description=description, root="")
    html += render_header("")
    items_html = "\n".join(render_actualite_item(a) for a in actualites) if actualites else \
        '<p class="vide">Aucune actualité publiée pour le moment. Revenez bientôt.</p>'
    html += f"""
<section class="page-titre">
  <div class="wrap etroit">
    <h1>Actualités</h1>
    <p class="page-intro">{description}</p>
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
    <p>{a.get('paragraph_3', '')}</p>
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
      statut.textContent = "Le formulaire n'est pas encore activé. Écrivez-nous à contact@recade-finance.com.";
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
        statut.textContent = "L'envoi n'a pas abouti. Réessayez ou écrivez-nous à contact@recade-finance.com.";
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

def render_sitemap(posts):
    urls = ["", "assistant-umoa.html", "a-propos.html", "actualites.html", "minute-eco.html", "instant-ia.html"]
    urls += [f"articles/{p['slug']}.html" for p in posts]
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
    copier_assets()

    posts = load_all_posts()
    print(f"{len(posts)} article(s) trouvé(s) dans /posts")
    actualites = load_all_actualites()
    print(f"{len(actualites)} actualité(s) trouvée(s) dans /actualites")
    minute_eco = load_markdown_folder(MINUTE_ECO_DIR)
    print(f"{len(minute_eco)} billet(s) trouvé(s) dans /minute-eco")
    instant_ia = load_markdown_folder(INSTANT_IA_DIR)
    print(f"{len(instant_ia)} billet(s) trouvé(s) dans /instant-ia")

    def ecrire(chemin, contenu):
        with open(os.path.join(DOCS_DIR, chemin), "w", encoding="utf-8") as f:
            f.write(contenu)

    ecrire("index.html", render_homepage(posts))
    ecrire("a-propos.html", render_about())
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

    for post in posts:
        ecrire(os.path.join("articles", f"{post['slug']}.html"), render_article(post))
        print(f"  articles/{post['slug']}.html")

    ecrire("sitemap.xml", render_sitemap(posts))
    ecrire("robots.txt", render_robots())
    print("Site généré dans /docs, prêt à être poussé sur GitHub.")


if __name__ == "__main__":
    main()

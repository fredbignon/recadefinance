#!/usr/bin/env python3
"""
Générateur statique — Récade Finance
======================================
Lit les fichiers Markdown de /posts, génère les pages HTML dans /docs
(le dossier servi par GitHub Pages). Aucune dépendance lourde : juste
`markdown` et `pyyaml` (déjà présents dans la plupart des environnements
Python, sinon : pip install markdown pyyaml).

Usage : python3 scripts/build.py
"""

import os
import re
import glob
import yaml
import markdown
import shutil
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS_DIR = os.path.join(ROOT, "posts")
ACTUALITES_DIR = os.path.join(ROOT, "actualites")
MINUTE_ECO_DIR = os.path.join(ROOT, "minute-eco")
INSTANT_IA_DIR = os.path.join(ROOT, "instant-ia")
DOCS_DIR = os.path.join(ROOT, "docs")
CONTENT_FILE = os.path.join(ROOT, "content", "site_content.yaml")
SITE_TITLE = "Récade Finance"
SITE_TAGLINE = "Économie · Dette souveraine · IA — Un regard africain"
SITE_URL = "https://recade-finance.com"

with open(CONTENT_FILE, encoding="utf-8") as f:
    CONTENT = yaml.safe_load(f)

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

# ---------------------------------------------------------------------------
# Lecture des articles Markdown (frontmatter YAML + corps)
# ---------------------------------------------------------------------------

def parse_post(filepath):
    with open(filepath, encoding="utf-8") as f:
        raw = f.read()
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", raw, re.DOTALL)
    if not m:
        raise ValueError(f"Frontmatter manquant dans {filepath}")
    meta = yaml.safe_load(m.group(1))
    body_md = m.group(2)
    html_body = markdown.markdown(body_md, extensions=["extra"])
    slug = os.path.splitext(os.path.basename(filepath))[0]
    slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", slug)  # retire la date du nom de fichier
    meta["slug"] = slug
    meta["html_body"] = html_body
    if isinstance(meta["date"], str):
        meta["date"] = datetime.strptime(meta["date"], "%Y-%m-%d").date()
    return meta


def load_all_posts():
    files = sorted(glob.glob(os.path.join(POSTS_DIR, "*.md")), reverse=True)
    files = [f for f in files if os.path.basename(f).upper() != "README.MD"]
    posts = [parse_post(f) for f in files]
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts


def load_all_actualites():
    files = sorted(glob.glob(os.path.join(ACTUALITES_DIR, "*.md")), reverse=True)
    files = [f for f in files if os.path.basename(f).upper() != "README.MD"]
    items = [parse_post(f) for f in files]
    items.sort(key=lambda p: p["date"], reverse=True)
    return items


def load_markdown_folder(folder):
    """Chargeur générique réutilisé pour La Minute Éco et L'Instant IA —
    même structure que /actualites (titre, date, extrait, corps Markdown).
    Exclut README.md (documentation de format, pas un billet)."""
    files = sorted(glob.glob(os.path.join(folder, "*.md")), reverse=True)
    files = [f for f in files if os.path.basename(f).upper() != "README.MD"]
    items = [parse_post(f) for f in files]
    items.sort(key=lambda p: p["date"], reverse=True)
    return items


# ---------------------------------------------------------------------------
# Gabarits HTML (chaînes Python — volontairement simples, sans dépendance
# à un moteur de templating externe)
# ---------------------------------------------------------------------------

HEAD = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}assets/style.css">
</head>
<body>
"""

FOOTER_HTML = """
<footer class="site">
  <div class="footer-inner">
    <div class="footer-brand">
      <span class="brand-name">RÉCADE FINANCE</span>
      <p class="footer-tagline">{footer_tagline}</p>
    </div>
    <div class="footer-cols">
      <div class="footer-col">
        <h4>Explorer</h4>
        <a href="{root}index.html#articles">Analyses</a>
        <a href="{root}actualites.html">Actualités</a>
        <a href="{root}minute-eco.html">La Minute Éco</a>
        <a href="{root}instant-ia.html">L'Instant IA</a>
        <a href="{root}index.html#tribune">Tribune</a>
      </div>
      <div class="footer-col">
        <h4>Contact</h4>
        <a href="https://{footer_website}" class="contact-icon-row">
          <svg width="18" height="18" viewBox="0 0 40 40"><circle cx="20" cy="20" r="17" fill="none" stroke="currentColor" stroke-width="2.4"/><ellipse cx="20" cy="20" rx="7.5" ry="17" fill="none" stroke="currentColor" stroke-width="2.4"/><line x1="3" y1="20" x2="37" y2="20" stroke="currentColor" stroke-width="2.4"/></svg>
          {footer_website}
        </a>
        <a href="https://instagram.com/recadefinance" class="contact-icon-row">
          <svg width="18" height="18" viewBox="0 0 40 40"><rect x="3" y="3" width="34" height="34" rx="11" fill="none" stroke="currentColor" stroke-width="2.4"/><circle cx="20" cy="20" r="8.5" fill="none" stroke="currentColor" stroke-width="2.4"/><circle cx="29.5" cy="10.5" r="2.2" fill="currentColor"/></svg>
          {footer_instagram}
        </a>
        <a href="mailto:{footer_email}" class="contact-icon-row">
          <svg width="18" height="18" viewBox="0 0 40 40"><rect x="3" y="8" width="34" height="24" fill="none" stroke="currentColor" stroke-width="2.4"/><polyline points="3,8 20,23 37,8" fill="none" stroke="currentColor" stroke-width="2.4"/></svg>
          {footer_email}
        </a>
      </div>
    </div>
  </div>
  <div class="footer-disclaimer">
    <span>⚠️ {site_disclaimer}</span>
  </div>
  <div class="footer-bottom">
    <span>&copy; {year} Récade Finance.</span>
    <span>{footer_website}</span>
  </div>
</footer>
</body>
</html>
"""

HEADER_HTML = """
<header class="site">
  <div class="header-inner">
    <a href="{root}index.html" class="brand">
      <svg width="30" height="30" viewBox="0 0 100 100" fill="none">
        <path d="M35 30 A18 14 0 1 0 63 26" stroke="#B5622A" stroke-width="5" stroke-linecap="round"/>
        <line x1="47" y1="28" x2="47" y2="80" stroke="#B5622A" stroke-width="5" stroke-linecap="round"/>
        <circle cx="66" cy="20" r="6" fill="#D9A441"/>
      </svg>
      <span class="brand-name">RÉCADE FINANCE</span>
    </a>
    <nav class="main-nav" id="rf-main-nav">
      <a href="{root}index.html">Accueil</a>
      <a href="{root}index.html#articles">Analyses</a>
      <a href="{root}actualites.html">Actualités</a>
      <a href="{root}minute-eco.html">La Minute Éco</a>
      <a href="{root}instant-ia.html">L'Instant IA</a>
      <a href="{root}index.html#tribune">Tribune</a>
      <a href="{root}a-propos.html">À propos</a>
    </nav>
    <div class="header-actions">
      <a href="{root}index.html#newsletter" class="btn btn-primary" style="padding:10px 20px; font-size:0.85rem;">S'abonner</a>
      <button class="nav-toggle" id="rf-nav-toggle" aria-label="Ouvrir le menu" aria-expanded="false">☰</button>
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


def render_footer(root=""):
    f = CONTENT["footer"]
    disclaimer = CONTENT.get("site_disclaimer_short", "")
    return FOOTER_HTML.format(
        root=root, year=datetime.now().year,
        footer_tagline=f["tagline"], footer_email=f["email"], footer_instagram=f["instagram"],
        footer_website=f.get("website", "recade-finance.com"),
        site_disclaimer=disclaimer,
    )


def render_list_item(post, root=""):
    cat_key = post.get("category", "analyses")
    cat_label = CATEGORY_LABELS.get(cat_key, cat_key)
    date_str = date_fr(post["date"])
    return f"""
      <div class="article-list-item">
        <span class="card-date">{cat_label} — {date_str}</span>
        <h4><a href="{root}articles/{post['slug']}.html">{post['title']}</a></h4>
        <p>{post['excerpt']}</p>
      </div>"""


def render_homepage(posts):
    featured_project = next((p for p in posts if p.get("featured")), None)
    remaining = [p for p in posts if p is not featured_project]

    # Article vedette (le plus récent des "remaining") + liste pour le reste
    article_feature = remaining[0] if remaining else None
    article_list = remaining[1:] if len(remaining) > 1 else []

    featured_html = ""
    if article_feature:
        cat_key = article_feature.get("category", "analyses")
        cat_label = CATEGORY_LABELS.get(cat_key, cat_key)
        banner = article_feature.get("banner_image")
        banner_html = f'<img src="{banner}" alt="{article_feature["title"]}" class="feature-banner">' if banner else ""
        featured_html = f"""
        <article class="article-feature-card">
          {banner_html}
          <div class="card-body">
            <span class="tag {cat_key}">{cat_label}</span>
            <h3 style="margin-top:14px;"><a href="articles/{article_feature['slug']}.html">{article_feature['title']}</a></h3>
            <p>{article_feature['excerpt']}</p>
            <a href="articles/{article_feature['slug']}.html" class="read-more">Lire l'analyse →</a>
          </div>
        </article>"""

    list_html = "\n".join(render_list_item(p) for p in article_list)

    featured_project_block = ""
    if featured_project:
        featured_project_block = f"""
<section class="featured" id="souverain-ia">
  <div class="featured-inner">
    <div class="featured-text">
      <span class="badge">Projet phare</span>
      <h2>{featured_project['title']}</h2>
      <p>{featured_project['excerpt']}</p>
      <a href="articles/{featured_project['slug']}.html" class="btn btn-primary">Lire le livre blanc</a>
    </div>
  </div>
</section>"""

    html = HEAD.format(
        title=f"{SITE_TITLE} — {SITE_TAGLINE}",
        description=SITE_TAGLINE,
        root="",
    )
    html += HEADER_HTML.format(root="")
    h = CONTENT["hero"]
    v = CONTENT["video_section"]
    c = CONTENT["credibility"]
    t = CONTENT["tribune"]
    n = CONTENT["newsletter"]
    html += f"""
<section class="hero">
  <div class="staff-thread" aria-hidden="true"></div>
  <div class="hero-inner">
    <span class="launch-badge"><span class="dot"></span> {h['launch_badge']}</span>
    <span class="eyebrow">{h['eyebrow']}</span>
    <h1>{h['title']}</h1>
    <p class="lede">{h['lede']}</p>
    <div class="hero-actions">
      <a href="#articles" class="btn btn-primary">{h['cta_label']}</a>
    </div>
  </div>
</section>

<section class="video-section">
  <div class="video-inner">
    <div class="video-text">
      <span class="eyebrow">{v['eyebrow']}</span>
      <h2>{v['title']}</h2>
      <p>Un aperçu rapide de la démarche et du positionnement de Récade Finance, en une minute.</p>
    </div>
    <div class="video-frame">
      <video src="assets/recade_finance_teaser.mp4" autoplay muted loop playsinline controls></video>
    </div>
  </div>
</section>

<section class="credibility">
  <div class="credibility-inner">
    <div class="cred-item"><span class="num">{len(posts)}</span><span class="label">{c['label_1']}</span></div>
    <div class="cred-item"><span class="num">{c['stat_2']}</span><span class="label">{c['label_2']}</span></div>
    <div class="cred-item"><span class="num">{c['stat_3']}</span><span class="label">{c['label_3']}</span></div>
  </div>
</section>

{featured_project_block}

<section class="section" id="articles">
  <div class="wrap">
    <div class="section-head"><h2>Dernières analyses</h2></div>
    <div class="articles-diversified">
      <div>{featured_html}</div>
      <div>{list_html}</div>
    </div>
  </div>
</section>

<section class="tribune" id="tribune">
  <div class="tribune-inner">
    <div class="tribune-header">
      <span class="eyebrow">{t['eyebrow']}</span>
      <h2>{t['title']}</h2>
    </div>
    <div class="tribune-card">
      <div class="tribune-card-text">
        <h3>{t['card_title']}</h3>
        <p>{t['card_text']}</p>
      </div>
      <span class="coming-soon-tag">{t['tag']}</span>
    </div>
  </div>
</section>

<section class="newsletter" id="newsletter">
  <div class="newsletter-inner">
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
      <button class="btn btn-primary" type="submit">{n['cta_label']}</button>
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
        title=f"{post['title']} — {SITE_TITLE}",
        description=post["excerpt"],
        root="../",
    )
    html += HEADER_HTML.format(root="../")
    cat_key = post.get("category", "analyses")
    cat_label = CATEGORY_LABELS.get(cat_key, cat_key)
    banner = post.get("banner_image")
    banner_html = f'<img src="../{banner}" alt="{post["title"]}" class="article-banner">' if banner else ""
    html += f"""
<article class="section article-single">
  <div class="wrap" style="max-width:760px;">
    <span class="tag {cat_key}">{cat_label}</span>
    <span class="card-date" style="margin-left:10px;">{date_fr(post['date'], with_day=True)}</span>
    <h1 style="margin-top:18px;">{post['title']}</h1>
    {banner_html}
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
        # Extrait l'identifiant de la vidéo pour construire l'URL d'intégration
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
    # sinon on suppose un fichier vidéo local (mp4) référencé depuis /assets
    return f"""
        <div class="video-embed-wrapper">
          <video src="{video_url}" controls></video>
        </div>"""


def render_contributor_item(item, root=""):
    author_name = item.get("author_name", "")
    author_title = item.get("author_title", "")
    byline_html = ""
    if author_name:
        byline_html = f'<div class="contrib-byline"><span class="contrib-name">{author_name}</span>'
        if author_title:
            byline_html += f'<span class="contrib-title"> — {author_title}</span>'
        byline_html += '</div>'

    video_url = item.get("video_url", "")
    video_html = render_video_embed(f"{root}{video_url}" if video_url and not video_url.startswith("http") else video_url)

    return f"""
      <article class="actu-item">
        <div class="actu-meta">
          <span class="card-date">{date_fr(item['date'], with_day=True)}</span>
        </div>
        <h3>{item['title']}</h3>
        {video_html}
        <div class="actu-body">{item['html_body']}</div>
        {byline_html}
      </article>"""


def render_contributor_page(items, page_title, eyebrow, intro_text, description):
    html = HEAD.format(title=f"{page_title} — {SITE_TITLE}", description=description, root="")
    html += HEADER_HTML.format(root="")
    items_html = "\n".join(render_contributor_item(i) for i in items) if items else \
        '<p style="color:#8a7a6a;">Aucun billet publié pour le moment — le premier arrive bientôt.</p>'
    html += f"""
<section class="section">
  <div class="wrap" style="max-width:760px;">
    <div class="section-head">
      <span class="eyebrow">{eyebrow}</span>
      <h1>{page_title}</h1>
      <p style="margin-top:14px; color:#5a4f44;">{intro_text}</p>
    </div>
    <div class="actu-list" style="margin-top:36px;">
      {items_html}
    </div>
  </div>
</section>
"""
    html += render_footer(root="")
    return html


def render_actualite_item(item):
    tags = item.get("tags", [])
    tags_html = " ".join(f'<span class="actu-tag">{t}</span>' for t in tags)
    source = item.get("source", "")
    source_url = item.get("source_url", "")
    source_html = f'<a href="{source_url}" target="_blank" rel="noopener">Source : {source} ↗</a>' if source else ""
    return f"""
      <article class="actu-item">
        <div class="actu-meta">
          <span class="card-date">{date_fr(item['date'], with_day=True)}</span>
          {tags_html}
        </div>
        <h3>{item['title']}</h3>
        <div class="actu-body">{item['html_body']}</div>
        <div class="actu-source">{source_html}</div>
      </article>"""


def render_actualites_page(actualites):
    html = HEAD.format(
        title=f"Actualités — {SITE_TITLE}",
        description="Veille régulière sur la finance, la dette souveraine et l'économie africaine.",
        root="",
    )
    html += HEADER_HTML.format(root="")
    items_html = "\n".join(render_actualite_item(a) for a in actualites) if actualites else \
        '<p style="color:#8a7a6a;">Aucune actualité publiée pour le moment — revenez bientôt.</p>'
    html += f"""
<section class="section">
  <div class="wrap" style="max-width:760px;">
    <div class="section-head">
      <span class="eyebrow">Veille régulière</span>
      <h1>Actualités</h1>
    </div>
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
    html = HEAD.format(title=f"À propos — {SITE_TITLE}", description=SITE_TAGLINE, root="")
    html += HEADER_HTML.format(root="")
    disclaimer_html = f"<p><em>{a['disclaimer']}</em></p>" if a.get("disclaimer") else ""
    html += f"""
<section class="section">
  <div class="wrap" style="max-width:760px;">
    <h1>Récade Finance</h1>
    <p style="margin-top:20px; font-size:1.05rem;"><em>{a['intro_quote']}</em></p>
    <p>{a['paragraph_1']}</p>
    <p>{a['paragraph_2']}</p>
    <p>{a.get('paragraph_3', '')}</p>
    {disclaimer_html}
  </div>
</section>
"""
    html += render_footer(root="")
    return html


# ---------------------------------------------------------------------------
# Écriture des fichiers
# ---------------------------------------------------------------------------

def main():
    os.makedirs(DOCS_DIR, exist_ok=True)
    os.makedirs(os.path.join(DOCS_DIR, "articles"), exist_ok=True)

    # Copie systématique de /assets vers /docs/assets — garantit que tout
    # changement de style, image ou vidéo se propage sans étape manuelle.
    assets_src = os.path.join(ROOT, "assets")
    assets_dst = os.path.join(DOCS_DIR, "assets")
    os.makedirs(assets_dst, exist_ok=True)
    for filename in os.listdir(assets_src):
        src_path = os.path.join(assets_src, filename)
        if os.path.isfile(src_path):
            shutil.copy2(src_path, os.path.join(assets_dst, filename))
    print(f"Assets copiés vers {assets_dst}")

    posts = load_all_posts()
    print(f"{len(posts)} article(s) trouvé(s) dans /posts")

    actualites = load_all_actualites()
    print(f"{len(actualites)} actualité(s) trouvée(s) dans /actualites")

    minute_eco = load_markdown_folder(MINUTE_ECO_DIR)
    print(f"{len(minute_eco)} billet(s) trouvé(s) dans /minute-eco")

    instant_ia = load_markdown_folder(INSTANT_IA_DIR)
    print(f"{len(instant_ia)} billet(s) trouvé(s) dans /instant-ia")

    with open(os.path.join(DOCS_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(render_homepage(posts))

    with open(os.path.join(DOCS_DIR, "a-propos.html"), "w", encoding="utf-8") as f:
        f.write(render_about())

    with open(os.path.join(DOCS_DIR, "minute-eco.html"), "w", encoding="utf-8") as f:
        f.write(render_contributor_page(
            minute_eco, "La Minute Éco", "Format court, écrit ou vidéo",
            "Une notion ou une thématique économique, souvent trop technique, expliquée simplement — en quelques minutes, à l'écrit ou en vidéo.",
            "La Minute Éco — vulgariser une notion économique à la fois, en quelques minutes.",
        ))

    with open(os.path.join(DOCS_DIR, "instant-ia.html"), "w", encoding="utf-8") as f:
        f.write(render_contributor_page(
            instant_ia, "L'Instant IA", "Format court, écrit ou vidéo",
            "Une notion ou une thématique liée à l'intelligence artificielle, souvent trop technique, expliquée simplement — en quelques minutes, à l'écrit ou en vidéo.",
            "L'Instant IA — vulgariser une notion d'IA à la fois, en quelques minutes.",
        ))

    with open(os.path.join(DOCS_DIR, "actualites.html"), "w", encoding="utf-8") as f:
        f.write(render_actualites_page(actualites))

    for post in posts:
        out_path = os.path.join(DOCS_DIR, "articles", f"{post['slug']}.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(render_article(post))
        print(f"  → articles/{post['slug']}.html")

    print("Site généré dans /docs — prêt à être poussé sur GitHub.")


if __name__ == "__main__":
    main()

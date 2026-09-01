import subprocess

PALETTES = {
    "bleu_institutionnel": {
        "--sable": "#EEF1F5",
        "--sable-deep": "#DCE3EC",
        "--terracotta": "#2C4870",
        "--terracotta-dark": "#1F3552",
        "--terracotta-deep": "#16273D",
        "--ocre": "#C9A227",
    },
    "vert_sahel": {
        "--sable": "#F2F0E6",
        "--sable-deep": "#E4E0CE",
        "--terracotta": "#3F6B4F",
        "--terracotta-dark": "#2E4F3A",
        "--terracotta-deep": "#1F3527",
        "--ocre": "#C68A3D",
    },
    "bordeaux_editorial": {
        "--sable": "#F5EEE9",
        "--sable-deep": "#E8DAD1",
        "--terracotta": "#7A2E3A",
        "--terracotta-dark": "#5C222B",
        "--terracotta-deep": "#3D171D",
        "--ocre": "#C9A227",
    },
    "ardoise_moderne": {
        "--sable": "#ECEAE6",
        "--sable-deep": "#DCD9D3",
        "--terracotta": "#4A5A6A",
        "--terracotta-dark": "#37434F",
        "--terracotta-deep": "#232B33",
        "--ocre": "#D9A441",
    },
}

with open("palette_tests/index.html", encoding="utf-8") as f:
    base_html = f.read()

for name, colors in PALETTES.items():
    override_css = ":root{\n" + "\n".join(f"  {k}:{v} !important;" for k, v in colors.items()) + "\n}"
    style_block = f"<style>{override_css}</style>\n</head>"
    variant_html = base_html.replace("</head>", style_block)
    out_path = f"palette_tests/index_{name}.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(variant_html)
    print(f"Variante générée : {out_path}")

    # Rendu de l'aperçu (haut de page uniquement)
    subprocess.run(
        ["wkhtmltoimage", "--width", "1200", "--enable-local-file-access",
         out_path, f"palette_tests/preview_{name}.png"],
        capture_output=True
    )
    print(f"  → capture : palette_tests/preview_{name}.png")

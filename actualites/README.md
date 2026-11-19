# Format d'une actualité ou d'une analyse

Un fichier Markdown par article, nommé AAAA-MM-JJ-titre-court.md. L'en-tête entre deux lignes de tirets est lu par le générateur.

Champs communs :

- title : titre complet.
- date : AAAA-MM-JJ.
- accroche : une phrase d'environ 140 caractères, affichée sous le titre sur la grille.
- visuel : texte très court affiché en grand sur la tuile (par exemple "4 M FCFA", "Ba3", "2,2 Md$").
- visuel_legende : une ligne de précision sous le visuel.
- image et image_alt : facultatifs, chemin d'une image du dossier assets et sa description. Si une image est fournie, elle remplace le visuel typographique. N'utiliser que des images dont vous détenez les droits ou libres de droits.

Sans visuel ni image, la tuile affiche le monogramme de Récade Finance.

Champs propres aux actualités : source, source_url, tags.
Champs propres aux analyses : category (analyses ou focus-benin), excerpt.

Chaque actualité a sa propre page (actualites/nom-du-fichier.html), chaque analyse la sienne (articles/nom-du-fichier.html).

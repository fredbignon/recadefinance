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

## Règle de sourcing (décision du 25 novembre 2026)

La source principale d'une actualité ou d'une analyse est l'institution officielle concernée : BCEAO, AMF-UMOA, BRVM, Commission de l'UEMOA, FMI, Banque mondiale, BOAD, ministères et autres organismes publics. Le texte est rédigé à partir de leur communiqué ou de leur document, que l'on cite avec son numéro et sa date.

- Le champ source indique l'institution et la référence du document (par exemple « FMI, communiqué de presse n° 26/355 »). Le champ source_url renvoie vers ce document officiel.
- La presse peut être citée en complément, jamais comme source principale. Si seule la presse est disponible, le texte reste en brouillon (dossier actualites_brouillons) jusqu'à la vérification auprès de l'institution.
- Les conclusions préliminaires (déclarations de fin de mission, accords au niveau des services) sont présentées comme telles : elles n'engagent pas encore l'institution.

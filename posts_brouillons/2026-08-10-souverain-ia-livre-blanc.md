---
title: "SOUVERAIN-IA : livre blanc"
date: 2026-08-10
category: analyses
excerpt: "Un prototype d'outil de pilotage interne de la notation souveraine du Bénin — backtesting compris, résultats imparfaits assumés."
featured: true
---

## Résumé exécutif

SOUVERAIN-IA est un prototype d'outil de pilotage interne de la notation souveraine du Bénin — un « shadow rating » destiné à éclairer une direction de la dette publique entre deux publications des agences internationales, et à simuler l'impact de scénarios macro-fiscaux alternatifs.

Construit en cinq phases sur la base de sources primaires (FMI, Banque mondiale, CAGD, Moody's), le prototype aboutit à trois résultats principaux :

- Le moteur reconstruit sur le squelette du LIC-DSF classe correctement le Bénin en capacité d'endettement « forte » — cohérent avec le reclassement officiel du FMI de février 2026.
- Un backtesting élargi à la Côte d'Ivoire et au Togo (7 transitions de notation réelles) montre qu'un scorecard quantitatif seul ne prédit correctement que **29 %** des décisions réelles d'agence.
- L'ajout d'un facteur d'inertie des comités de notation corrige une partie de cet angle mort et permet de simuler des hypothèses internes de manière plus réaliste.

## Pourquoi le publier avec ses limites

Le résultat le plus significatif du projet n'est pas la performance du modèle — encore limitée à ce stade de prototype — mais la mise en évidence, par le backtesting, des mécanismes qui expliquent pourquoi un scorecard quantitatif seul échoue à prédire près des trois quarts des décisions réelles d'agence.

*L'ensemble du code source (moteur CI/DSA, scorecard, backtesting, couche qualitative) est disponible sur demande.*

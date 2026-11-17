# Résultats de l’autosimulation Termux ARM64

Ce document présente les résultats obtenus lors d’une exécution locale du benchmark EHK-SCCI sous Termux ARM64.

## Résultats obtenus localement

Les résultats suivants proviennent de l’exécution du script `run_autosim_termux.py` sur l’appareil local.

| Indicateur | Valeur |
|---|---:|
| AUROC global | 0.400625 |
| Taux d’alarme nominal ID | 0.1500 |
| Taux de détection OOD | 0.1250 |
| Seuil calibré sigma_c | 0.8902369219890172 |

Les artefacts générés sont :

- `ehkscci_termux_report/benchmark_results.csv`
- `ehkscci_termux_report/manifest.json`
- `ehkscci_termux_report/roc_curve.csv`

Les empreintes SHA-256 des artefacts sont enregistrées dans `manifest.json`.

## Hypothèses de simulation

Cette exécution est une autosimulation locale. Elle ne constitue pas une validation sur un système industriel réel, sur WAAFI ou sur un équipement critique.

Les hypothèses principales sont :

- Les partitions ID et OOD sont générées localement par le script.
- Le seuil `sigma_c` est calibré à partir des données simulées.
- Les scores ID et OOD sont produits par la logique implémentée dans le script.
- Les métriques sont calculées à partir de ces scores simulés.
- L’exécution ne repose pas sur des données de production, des identifiants réels ou des équipements critiques.

## Limites de l’AUROC actuel

L’AUROC global obtenu est de `0.400625`, inférieur à `0.5`.

Cela signifie que, dans cette configuration, le score ne sépare pas mieux que le hasard les échantillons ID des échantillons OOD. Un AUROC inférieur à `0.5` peut indiquer une inversion de la relation entre score et classe, une mauvaise calibration, une séparation insuffisante des distributions ou un problème dans la construction des caractéristiques.

Le taux de détection OOD de `0.1250` est également faible. Cela signifie que seulement 12,5 % des échantillons OOD sont détectés comme anormaux selon le seuil calibré.

Ces résultats ne permettent pas de conclure que le logiciel réel est défaillant. Ils indiquent seulement que la configuration actuelle de l’autosimulation ne produit pas une séparation ID/OOD satisfaisante.

## Prochaines vérifications

Les vérifications suivantes sont recommandées avant toute interprétation opérationnelle :

- Vérifier que les labels ID et OOD sont correctement assignés.
- Vérifier que les scores ID et OOD sont calculés avec la même définition.
- Vérifier le sens attendu du score : un score élevé doit correspondre à la classe positive.
- Vérifier la calibration du seuil `sigma_c`.
- Vérifier la distribution des scores ID et OOD.
- Vérifier la cohérence entre la courbe ROC et l’AUROC calculé.
- Vérifier que les données simulées ne rendent pas les classes ID et OOD indistinguables.
- Vérifier que les caractéristiques utilisées sont pertinentes pour la séparation ID/OOD.
- Comparer les résultats avec plusieurs graines aléatoires.
- Comparer les résultats avec plusieurs tailles d’échantillons.
- Vérifier la reproductibilité des empreintes SHA-256.

## Portée

Ces résultats sont locaux, reproductibles et traçables grâce aux empreintes SHA-256. Ils ne constituent pas une validation opérationnelle du système EHK-SCCI sur un environnement réel.

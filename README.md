# EHK-SCCI — Autosimulation Termux ARM64
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24302601.svg)](https://doi.org/10.5281/zenodo.24302601)
Archive Zenodo : https://doi.org/10.5281/zenodo.24302601

Ce dépôt contient les résultats d’une autosimulation locale du benchmark EHK-SCCI exécutée sous Termux ARM64.

## Résultat opérationnel prioritaire

Dans le benchmark de calibration EHK-SCCI, le seuil opérationnel candidat est :

X_op = 0.75

À ce seuil, le benchmark atteint :

- 96.15 % de détection OOD ;
- 2.20 % de fausse abstention ID.

Le seuil par défaut officiel reste :

X0 = 0.3

À X0 = 0.3, le benchmark détecte 3.50 % des OOD, avec 0 % de fausse abstention ID.

La calibration empirique montre qu’un seuil opérationnel plus élevé peut exploiter la séparation ID/OOD produite par la formule I_disc. Le point X_op = 0.75 constitue le meilleur compromis observé dans ce benchmark.

Ces résultats sont expérimentaux et issus d’une simulation synthétique. Ils ne constituent pas une validation opérationnelle sur un système réel.
## Contenu

- `run_autosim_termux.py` : script d’autosimulation local.
- `ehkscci_termux_report/benchmark_results.csv` : métriques principales.
- `ehkscci_termux_report/manifest.json` : métadonnées, paramètres et empreintes SHA-256.
- `ehkscci_termux_report/roc_curve.csv` : points de la courbe ROC.

## Résultats de l’exécution

| Indicateur | Valeur |
|---|---:|
| AUROC global | 0.400625 |
| Taux d’alarme nominal ID | 0.1500 |
| Taux de détection OOD | 0.1250 |
| Seuil calibré sigma_c | 0.8902369219890172 |

## Portée des résultats

Les résultats affichés proviennent d’une autosimulation locale sous Termux ARM64. Ils ne constituent pas une validation opérationnelle sur un système industriel réel, sur un équipement critique ou dans un environnement de production.

Les résultats sont sensibles aux hypothèses de simulation, à la calibration du seuil et à la construction des scores. L’AUROC actuel de `0.400625` est inférieur à `0.5`, ce qui indique une séparation ID/OOD insuffisante dans cette configuration.

Les détails, hypothèses, limites et prochaines vérifications sont décrits dans [`RESULTS.md`](RESULTS.md).

## Reproductibilité

Les empreintes SHA-256 des artefacts sont enregistrées dans `manifest.json`.

## Environnement

- Termux ARM64
- Python 3
- NumPy 2.5.4
- SciPy
- Exécution locale, sans connexion à un service externe ni accès à un équipement critique

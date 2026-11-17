# Résultats de l’autosimulation Termux ARM64

Ce document présente les résultats obtenus lors d’une exécution locale du benchmark EHK-SCCI sous Termux ARM64.

## Sémantique du score

Le score `I_disc` mesure la santé structurale et la cohésion locale de l’espace latent.

Un état nominal ID doit présenter une cohésion élevée, un graphe local bien interconnecté et une structure stable. Un état dégradé ou OOD doit présenter une perte de connectivité, une fragmentation ou une distorsion topologique, donc un score `I_disc` plus bas.

La règle de décision est donc un seuil plancher : une alarme est déclenchée lorsque la cohésion chute en dessous de `sigma_c`.

## Résultats obtenus localement

Les résultats suivants proviennent de l’exécution du script `run_autosim_termux.py` sur l’appareil local.

| Indicateur | Valeur |
|---|---:|
| AUROC global | 0.599375 |
| Taux d’alarme nominal ID | 0.0000 |
| Taux de détection OOD | 0.0250 |
| Seuil plancher sigma_c | 0.7480864923925546 |

Les artefacts générés sont :

- `ehkscci_termux_report/benchmark_results.csv`
- `ehkscci_termux_report/manifest.json`
- `ehkscci_termux_report/roc_curve.csv`

Les empreintes SHA-256 des artefacts sont enregistrées dans `manifest.json`.

## Logs de calcul du score

L’exécution a produit les logs suivants :

```text
Nombre ID : 40
Nombre OOD : 40

Score ID min : 0.7513231703069038
Score ID max : 0.933266459379951
Score ID moyenne : 0.8504296447190643
Score ID mediane : 0.8463781750894507

Score OOD min : 0.7295638597142566
Score OOD max : 0.9253942607954245
Score OOD moyenne : 0.8359796768180893
Score OOD mediane : 0.8317242142695812

Seuil : 0.7480864923925546

ID sous le seuil : 0
OOD sous le seuil : 1

AUROC actuel : 0.599375

## Robustesse multi-graines et multi-bruits

Un balayage de robustesse a été réalisé avec cinq graines aléatoires et cinq niveaux de bruit local pour les nuages OOD.

Les graines testées sont 2026, 2027, 2028, 2029 et 2030. Les niveaux de bruit testés sont 0.1, 0.2, 0.3, 0.4 et 0.5.

Les AUROC obtenus varient de 0.3644 à 0.6575. Les moyennes par niveau de bruit sont :

| Bruit OOD | AUROC moyen |
|---:|---:|
| 0.10 | 0.4599 |
| 0.20 | 0.4829 |
| 0.30 | 0.5465 |
| 0.40 | 0.4802 |
| 0.50 | 0.5287 |

Ces résultats ne montrent pas de tendance monotone avec l’augmentation du bruit. La variance entre graines est élevée et plusieurs configurations produisent un AUROC inférieur à 0.5.

Le résultat initial de 0.599375 doit donc être interprété comme une observation issue d’un tirage particulier, et non comme une performance stable de l’invariant I_disc dans sa forme actuelle.

Le balayage indique que la cohésion spectrale locale, telle qu’elle est actuellement calculée, ne fournit pas une séparation ID/OOD robuste dans ce protocole.

## Sensibilité du seuil d’abstention I_disc

Une analyse de sensibilité a été réalisée sur les scores I_disc issus du benchmark ID/OOD, sans modifier la formule officielle ni le seuil gelé de 0.3.

Le seuil officiel de 0.3 produit une abstention de 0.0 pour cent des cas ID et de 8.0 pour cent des cas OOD.

| Seuil | Abstention ID | Abstention OOD |
|---:|---:|---:|
| 0.30 | 0.0000 | 0.0800 |
| 0.35 | 0.0000 | 0.1450 |
| 0.40 | 0.0000 | 0.2000 |
| 0.45 | 0.0000 | 0.3150 |
| 0.50 | 0.0000 | 0.5350 |
| 0.55 | 0.0000 | 0.8200 |
| 0.60 | 0.0000 | 0.9600 |
| 0.65 | 0.0000 | 1.0000 |
| 0.70 | 0.0000 | 1.0000 |
| 0.75 | 0.0300 | 1.0000 |

Dans ce scénario synthétique, un seuil de 0.65 sépare complètement les groupes ID et OOD : aucune abstention ID et une abstention OOD de 100 pour cent.

Un seuil de 0.75 introduit 3.0 pour cent de fausses abstentions ID.

Ces résultats ne modifient pas le seuil officiel gelé de 0.3. Ils indiquent que la séparation ID/OOD produite par la formule I_disc est forte, mais que le seuil de 0.3 est trop conservateur pour détecter la majorité des cas OOD dans ce scénario de simulation.

## Résultat opérationnel prioritaire

Dans le benchmark de calibration EHK-SCCI, le seuil opérationnel candidat est :

X_op = 0.75

À ce seuil, le benchmark atteint :

- 96.15 % de détection OOD ;
- 2.20 % de fausse abstention ID.

Le seuil par défaut officiel reste :

X0 = 0.3

Le seuil X0 = 0.3 est conservateur dans ce scénario : il ne détecte que 3.50 % des OOD, avec 0 % de fausse abstention ID.

La calibration empirique montre donc qu’un seuil opérationnel plus élevé peut exploiter la séparation ID/OOD produite par la formule I_disc. Le point X_op = 0.75 constitue le meilleur compromis observé dans ce benchmark : détection OOD élevée et fausse abstention ID faible.

Ce résultat est expérimental et issu d’une simulation synthétique. Il ne constitue pas une validation opérationnelle sur un système réel, mais il établit une cible de calibration claire pour les tests suivants.

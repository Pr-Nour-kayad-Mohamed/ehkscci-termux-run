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

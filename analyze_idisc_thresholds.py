import csv
from pathlib import Path

import numpy as np

CSV_PATH = Path("idisc_benchmark_results/idisc_benchmark_results.csv")
OUTPUT_PATH = Path("idisc_benchmark_results/threshold_sensitivity.csv")

THRESHOLDS = [
    0.30, 0.35, 0.40, 0.45,
    0.50, 0.55, 0.60, 0.65,
    0.70, 0.75,
]


def load_rows():
    with CSV_PATH.open("r", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def analyze_threshold(rows, threshold):
    id_scores = np.array(
        [float(row["i_disc"]) for row in rows if row["group"] == "ID"],
        dtype=float,
    )

    ood_scores = np.array(
        [float(row["i_disc"]) for row in rows if row["group"] == "OOD"],
        dtype=float,
    )

    id_abstain_rate = float(np.mean(id_scores < threshold))
    ood_abstain_rate = float(np.mean(ood_scores < threshold))

    return {
        "threshold": threshold,
        "id_abstain_rate": id_abstain_rate,
        "ood_abstain_rate": ood_abstain_rate,
        "id_mean_i_disc": float(np.mean(id_scores)),
        "ood_mean_i_disc": float(np.mean(ood_scores)),
        "id_min_i_disc": float(np.min(id_scores)),
        "ood_min_i_disc": float(np.min(ood_scores)),
    }


def main():
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"Fichier introuvable : {CSV_PATH}")

    rows = load_rows()
    results = [analyze_threshold(rows, threshold) for threshold in THRESHOLDS]

    fieldnames = list(results[0].keys())

    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print("=== EHK-SCCI : Sensibilite du seuil d'abstention I_disc ===")
    print("Seuil | Abstention ID | Abstention OOD | I_disc ID moyen | I_disc OOD moyen")
    print("-" * 85)

    for result in results:
        print(
            f"{result['threshold']:.2f} | "
            f"{result['id_abstain_rate']:.4f} | "
            f"{result['ood_abstain_rate']:.4f} | "
            f"{result['id_mean_i_disc']:.4f} | "
            f"{result['ood_mean_i_disc']:.4f}"
        )

    print(f"Resultats exportes dans : {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

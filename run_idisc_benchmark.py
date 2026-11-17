import csv
import hashlib
import json
from pathlib import Path

import numpy as np

from ehkscci_idisc import compute_Idisc

SEEDS = [2026, 2027, 2028, 2029, 2030]
N_PER_GROUP = 40
DIMENSION = 8
OUTPUT_DIR = Path("idisc_benchmark_results")
OUTPUT_DIR.mkdir(exist_ok=True)


def make_operator(rng, retained_fraction):
    full = rng.normal(size=(DIMENSION, DIMENSION))
    u, s, vt = np.linalg.svd(full)
    keep = max(1, int(round(retained_fraction * DIMENSION)))
    s[keep:] = 0.0
    return (u * s) @ vt


def reconstruct(rng, x, noise_level):
    noisy = x + rng.normal(scale=noise_level, size=x.shape)
    return noisy


def run_seed(seed):
    rng = np.random.default_rng(seed)

    rows = []

    for group in ["ID", "OOD"]:
        for _ in range(N_PER_GROUP):
            x = rng.normal(size=DIMENSION)

            if group == "ID":
                retained_fraction = 0.75
                readout_snr_linear = 15.0
                reconstruction_noise = 0.05
            else:
                retained_fraction = 0.45
                readout_snr_linear = 5.0
                reconstruction_noise = 0.35

            a_d = make_operator(rng, retained_fraction)
            x_hat = reconstruct(rng, x, reconstruction_noise)

            y = a_d @ x + rng.normal(scale=0.05, size=DIMENSION)

            result = compute_Idisc(
                y=y,
                A_D=a_d,
                x_hat=x_hat,
                readout_SNR_linear=readout_snr_linear,
                retained_fraction=retained_fraction,
            )

            rows.append(
                {
                    "seed": seed,
                    "group": group,
                    "retained_fraction": retained_fraction,
                    "readout_snr_linear": readout_snr_linear,
                    "reconstruction_noise": reconstruction_noise,
                    "residual": result["residual"],
                    "sigma_min": result["sigma_min"],
                    "snr_norm": result["snr_norm"],
                    "i_disc": result["i_disc"],
                    "abstain_flag": result["abstain_flag"],
                }
            )

    return rows


def summarize(rows):
    summary = []

    for seed in SEEDS:
        seed_rows = [row for row in rows if row["seed"] == seed]

        id_rows = [row for row in seed_rows if row["group"] == "ID"]
        ood_rows = [row for row in seed_rows if row["group"] == "OOD"]

        id_scores = np.array([row["i_disc"] for row in id_rows])
        ood_scores = np.array([row["i_disc"] for row in ood_rows])

        id_abstain = np.mean([row["abstain_flag"] for row in id_rows])
        ood_abstain = np.mean([row["abstain_flag"] for row in ood_rows])

        summary.append(
            {
                "seed": seed,
                "id_mean_i_disc": float(np.mean(id_scores)),
                "ood_mean_i_disc": float(np.mean(ood_scores)),
                "id_std_i_disc": float(np.std(id_scores)),
                "ood_std_i_disc": float(np.std(ood_scores)),
                "id_abstain_rate": float(id_abstain),
                "ood_abstain_rate": float(ood_abstain),
            }
        )

    return summary


def main():
    all_rows = []

    for seed in SEEDS:
        all_rows.extend(run_seed(seed))

    csv_path = OUTPUT_DIR / "idisc_benchmark_results.csv"
    fieldnames = list(all_rows[0].keys())

    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    summary = summarize(all_rows)

    manifest = {
        "benchmark": "EHK-SCCI EHK-SCCI I_disc benchmark",
        "scope": "Synthetic simulation only; no operational validation",
        "seeds": SEEDS,
        "n_per_group": N_PER_GROUP,
        "dimension": DIMENSION,
        "id_scenario": {
            "retained_fraction": 0.75,
            "readout_snr_linear": 15.0,
            "reconstruction_noise": 0.05,
        },
        "ood_scenario": {
            "retained_fraction": 0.45,
            "readout_snr_linear": 5.0,
            "reconstruction_noise": 0.35,
        },
        "abstention_threshold": 0.3,
        "results_csv": str(csv_path),
        "summary": summary,
    }

    manifest_path = OUTPUT_DIR / "manifest.json"

    with manifest_path.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, ensure_ascii=False)

    print("=== EHK-SCCI : Benchmark du I_disc officiel EHK-SCCI ===")
    print("Graine | I_disc ID moyen | I_disc OOD moyen | Abstention ID | Abstention OOD")
    print("-" * 85)

    for item in summary:
        print(
            f"{item['seed']} | "
            f"{item['id_mean_i_disc']:.4f} | "
            f"{item['ood_mean_i_disc']:.4f} | "
            f"{item['id_abstain_rate']:.4f} | "
            f"{item['ood_abstain_rate']:.4f}"
        )

    print(f"Resultats exportes dans : {csv_path}")
    print(f"Manifeste exporte dans : {manifest_path}")


if __name__ == "__main__":
    main()

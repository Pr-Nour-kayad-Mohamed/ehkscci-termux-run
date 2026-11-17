import os
import csv
import numpy as np

from run_autosim_termux import (
    compute_batch_scores,
    compute_threshold,
    evaluate_detector,
    roc_auc_score
)


def run_robustness_sweep():
    print("=== EHK-SCCI : Balayage de robustesse multi-graines et multi-bruits ===")

    seeds = [2026, 2027, 2028, 2029, 2030]
    noise_levels = [0.1, 0.2, 0.3, 0.4, 0.5]

    n_samples = 40
    dim = 32
    k = 4
    local_cloud_size = 30
    local_noise = 0.2
    target_false_positive_rate = 0.05

    results = []

    for seed in seeds:
        rng = np.random.default_rng(seed)

        activations_id = rng.normal(
            loc=0.0,
            scale=1.0,
            size=(n_samples, dim)
        )

        activations_ood = rng.normal(
            loc=0.5,
            scale=1.4,
            size=(n_samples, dim)
        )

        scores_id = compute_batch_scores(
            activations_id,
            k=k,
            tau_reference=None,
            local_cloud_size=local_cloud_size,
            local_noise=local_noise,
            rng=rng
        )

        threshold = compute_threshold(
            scores_id,
            target_false_positive_rate=target_false_positive_rate
        )

        for noise_level in noise_levels:
            scores_ood = compute_batch_scores(
                activations_ood,
                k=k,
                tau_reference=None,
                local_cloud_size=local_cloud_size,
                local_noise=noise_level,
                rng=rng
            )

            performance = evaluate_detector(
                scores_id,
                scores_ood,
                threshold
            )

            results.append({
                "seed": seed,
                "noise_level": noise_level,
                "sigma_c": threshold,
                "auroc": performance["auroc"],
                "nominal_alarm_rate": performance["nominal_alarm_rate"],
                "ood_detection_rate": performance["ood_detection_rate"]
            })

    output_directory = "robustness_results"
    os.makedirs(output_directory, exist_ok=True)

    output_path = os.path.join(
        output_directory,
        "robustness_sweep.csv"
    )

    with open(output_path, "w", newline="") as output_file:
        writer = csv.DictWriter(
            output_file,
            fieldnames=[
                "seed",
                "noise_level",
                "sigma_c",
                "auroc",
                "nominal_alarm_rate",
                "ood_detection_rate"
            ]
        )

        writer.writeheader()

        for result in results:
            writer.writerow(result)

    print()
    print("--- SYNTHESE DES TESTS DE ROBUSTESSE ---")
    print(
        f"{'Graine':<8} | "
        f"{'Bruit OOD':<10} | "
        f"{'Seuil sigma_c':<15} | "
        f"{'AUROC':<10} | "
        f"{'Alarme ID':<10} | "
        f"{'Detection OOD':<15}"
    )
    print("-" * 90)

    for result in results:
        print(
            f"{result['seed']:<8} | "
            f"{result['noise_level']:<10.2f} | "
            f"{result['sigma_c']:<15.6f} | "
            f"{result['auroc']:<10.4f} | "
            f"{result['nominal_alarm_rate']:<10.4f} | "
            f"{result['ood_detection_rate']:<15.4f}"
        )

    print()
    print(f"Resultats exportes dans : {output_path}")


if __name__ == "__main__":
    run_robustness_sweep()

import os
import json
import hashlib
from datetime import datetime, timezone

import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.sparse.linalg import eigsh
def roc_auc_score(labels, scores):
    labels = np.asarray(labels)
    scores = np.asarray(scores)

    positive = scores[labels == 1]
    negative = scores[labels == 0]

    if len(positive) == 0 or len(negative) == 0:
        return 0.0

    greater = np.sum(
        positive[:, None] > negative[None, :]
    )

    equal = np.sum(
        positive[:, None] == negative[None, :]
    )

    return float(
        (greater + 0.5 * equal)
        / (len(positive) * len(negative))
    )

REPORT_DIRECTORY = os.path.expanduser(
    "~/ehkscci-bench-results/ehkscci_termux_report"
)


def sha256_file(path):
    hasher = hashlib.sha256()

    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            hasher.update(block)

    return hasher.hexdigest()


def build_knn_graph(activations, k=4, tau=None):
    n_samples, n_features = activations.shape

    distances = np.linalg.norm(
        activations[:, None, :] - activations[None, :, :],
        axis=2
    )

    if tau is None:
        sorted_distances = np.sort(distances, axis=1)
        tau = float(
            np.median(sorted_distances[:, k])
        )

    adjacency = np.zeros(
        (n_samples, n_samples),
        dtype=float
    )

    for i in range(n_samples):
        nearest = np.argsort(distances[i])[1:k + 1]

        for j in nearest:
            weight = np.exp(
                -(distances[i, j] ** 2)
                / (2.0 * tau ** 2)
            )

            adjacency[i, j] = weight
            adjacency[j, i] = weight

    return adjacency, tau


def spectral_gap(adjacency):
    degree = adjacency.sum(axis=1)

    inverse_sqrt_degree = np.zeros_like(degree)

    nonzero = degree > 0

    inverse_sqrt_degree[nonzero] = (
        1.0 / np.sqrt(degree[nonzero])
    )

    normalized_adjacency = (
        inverse_sqrt_degree[:, None]
        * adjacency
        * inverse_sqrt_degree[None, :]
    )

    eigenvalues = np.linalg.eigvalsh(
        normalized_adjacency
    )

    eigenvalues = np.sort(eigenvalues)

    if len(eigenvalues) < 2:
        return 0.0

    return float(eigenvalues[-2])


def graph_fisher_information(
    adjacency,
    probabilities
):
    fisher_information = 0.0

    n_samples = adjacency.shape[0]

    for i in range(n_samples):
        for j in range(i + 1, n_samples):
            weight = adjacency[i, j]

            if weight > 0:
                fisher_information += weight * (
                    np.sqrt(probabilities[j])
                    - np.sqrt(probabilities[i])
                ) ** 2 * (
                    1.0 / probabilities[i]
                    + 1.0 / probabilities[j]
                )

    return 0.5 * fisher_information


def compute_idisc(adjacency, probabilities):
    gap = spectral_gap(adjacency)

    fisher_information = graph_fisher_information(
        adjacency,
        probabilities
    )

    return gap + fisher_information


def evaluate_dataset(
    activations,
    k=4,
    tau_reference=None
):
    adjacency, tau = build_knn_graph(
        activations,
        k=k,
        tau=tau_reference
    )

    n_samples = activations.shape[0]

    probabilities = np.full(
        n_samples,
        1.0 / n_samples
    )

    invariant = compute_idisc(
        adjacency,
        probabilities
    )

    return invariant, tau


def compute_batch_scores(
    activations,
    k=4,
    tau_reference=None,
    local_cloud_size=30,
    local_noise=0.2,
    rng=None
):
    scores = []

    for sample in activations:
        local_cloud = rng.normal(
            loc=sample,
            scale=local_noise,
            size=(
                local_cloud_size,
                activations.shape[1]
            )
        )

        score, _ = evaluate_dataset(
            local_cloud,
            k=k,
            tau_reference=tau_reference
        )

        scores.append(score)

    return np.array(scores)


def compute_threshold(
    scores_nominal,
    target_false_positive_rate=0.05
):
    return float(
        np.quantile(
            scores_nominal,
            1.0 - target_false_positive_rate
        )
    )


def evaluate_detector(
    scores_nominal,
    scores_ood,
    threshold
):
    scores = np.concatenate([
        scores_nominal,
        scores_ood
    ])

    labels = np.concatenate([
        np.zeros(len(scores_nominal), dtype=int),
        np.ones(len(scores_ood), dtype=int)
    ])

    predictions = (scores >= threshold).astype(int)

    auroc = float(
        roc_auc_score(
            labels,
            scores
        )
    )

    nominal_alarm_rate = float(
        np.mean(
            predictions[:len(scores_nominal)]
        )
    )

    ood_detection_rate = float(
        np.mean(
            predictions[len(scores_nominal):]
        )
    )

    return {
        "auroc": auroc,
        "nominal_alarm_rate": nominal_alarm_rate,
        "ood_detection_rate": ood_detection_rate
    }


def roc_curve(labels, scores):
    labels = np.asarray(labels)
    scores = np.asarray(scores)

    thresholds = np.unique(scores)

    thresholds = np.concatenate([
        thresholds,
        [thresholds[-1] + 1.0]
    ])

    false_positive_rates = []
    true_positive_rates = []

    n_positive = np.sum(labels == 1)
    n_negative = np.sum(labels == 0)

    for threshold in thresholds:
        predictions = scores >= threshold

        true_positive = np.sum(
            (labels == 1) & predictions
        )

        false_positive = np.sum(
            (labels == 0) & predictions
        )

        true_positive_rates.append(
            true_positive / n_positive
        )

        false_positive_rates.append(
            false_positive / n_negative
        )

    order = np.argsort(false_positive_rates)

    false_positive_rates = np.asarray(
        false_positive_rates
    )[order]

    true_positive_rates = np.asarray(
        true_positive_rates
    )[order]

    return (
        false_positive_rates,
        true_positive_rates,
        thresholds
    )


def save_roc_curve(
    scores_nominal,
    scores_ood,
    output_directory
):
    scores = np.concatenate([
        scores_nominal,
        scores_ood
    ])

    labels = np.concatenate([
        np.zeros(len(scores_nominal), dtype=int),
        np.ones(len(scores_ood), dtype=int)
    ])

    false_positive_rate, true_positive_rate, _ = roc_curve(
        labels,
        scores
    )

    roc_path = os.path.join(
        output_directory,
        "roc_curve.csv"
    )

    np.savetxt(
        roc_path,
        np.column_stack([
            false_positive_rate,
            true_positive_rate
        ]),
        delimiter=",",
        header="false_positive_rate,true_positive_rate",
        comments=""
    )

    return roc_path


def save_results(
    performance,
    threshold,
    output_directory
):
    results_path = os.path.join(
        output_directory,
        "benchmark_results.csv"
    )

    with open(
        results_path,
        "w",
        encoding="utf-8"
    ) as handle:
        handle.write("metric,value\n")
        handle.write(
            f"threshold_sigma_c,{threshold}\n"
        )

        for key, value in performance.items():
            handle.write(
                f"{key},{value}\n"
            )

    return results_path


def save_manifest(
    performance,
    threshold,
    output_directory,
    seed,
    target_false_positive_rate
):
    manifest_path = os.path.join(
        output_directory,
        "manifest.json"
    )

    roc_path = os.path.join(
        output_directory,
        "roc_curve.csv"
    )

    results_path = os.path.join(
        output_directory,
        "benchmark_results.csv"
    )

    manifest = {
        "benchmark": "EHK-SCCI",
        "version": "1.0.0",
        "created_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "random_seed": seed,
        "calibration": {
            "threshold_sigma_c": threshold,
            "target_false_positive_rate": target_false_positive_rate
        },
        "performance": performance,
        "artifacts": {
            "roc_curve_csv": {
                "path": roc_path,
                "sha256": sha256_file(roc_path)
            },
            "benchmark_results_csv": {
                "path": results_path,
                "sha256": sha256_file(results_path)
            },
            "manifest_json": {
                "path": manifest_path,
                "sha256": None
            }
        }
    }

    with open(
        manifest_path,
        "w",
        encoding="utf-8"
    ) as handle:
        json.dump(
            manifest,
            handle,
            indent=2,
            ensure_ascii=False
        )

    manifest["artifacts"]["manifest_json"]["sha256"] = (
        sha256_file(manifest_path)
    )

    with open(
        manifest_path,
        "w",
        encoding="utf-8"
    ) as handle:
        json.dump(
            manifest,
            handle,
            indent=2,
            ensure_ascii=False
        )

    return manifest_path


def run_termux_autosimulation():
    print(
        "=== EHK-SCCI : autosimulation Termux ARM64 ==="
    )

    seed = 2026
    rng = np.random.default_rng(seed)

    n_samples = 40
    n_features = 8
    k = 3
    target_false_positive_rate = 0.05

    print(
        "[1/4] Génération des partitions ID et OOD..."
    )

    activations_train = rng.normal(
        loc=0.0,
        scale=1.0,
        size=(n_samples, n_features)
    )

    activations_calibration = rng.normal(
        loc=0.0,
        scale=1.0,
        size=(n_samples, n_features)
    )

    activations_test_id = rng.normal(
        loc=0.0,
        scale=1.0,
        size=(n_samples, n_features)
    )

    activations_test_ood = rng.normal(
        loc=0.5,
        scale=1.4,
        size=(n_samples, n_features)
    )

    print(
        "[2/4] Calibration du seuil sigma_c..."
    )

    _, tau_reference = evaluate_dataset(
        activations_train,
        k=k
    )

    scores_calibration = compute_batch_scores(
        activations_calibration,
        k=k,
        tau_reference=tau_reference,
        rng=rng
    )

    threshold = compute_threshold(
        scores_calibration,
        target_false_positive_rate=target_false_positive_rate
    )

    print(
        f"Seuil calibré sigma_c : {threshold:.6f}"
    )

    print(
        "[3/4] Évaluation ID et OOD..."
    )

    scores_test_id = compute_batch_scores(
        activations_test_id,
        k=k,
        tau_reference=tau_reference,
        rng=rng
    )

    scores_test_ood = compute_batch_scores(
        activations_test_ood,
        k=k,
        tau_reference=tau_reference,
        rng=rng
    )

    performance = evaluate_detector(
        scores_test_id,
        scores_test_ood,
        threshold
    )

    print(
        "[4/4] Génération du rapport..."
    )

    os.makedirs(
        REPORT_DIRECTORY,
        exist_ok=True
    )

    roc_path = save_roc_curve(
        scores_test_id,
        scores_test_ood,
        REPORT_DIRECTORY
    )

    results_path = save_results(
        performance,
        threshold,
        REPORT_DIRECTORY
    )

    manifest_path = save_manifest(
        performance,
        threshold,
        REPORT_DIRECTORY,
        seed,
        target_false_positive_rate
    )

    print()
    print(
        "--- Résultats de l'autosimulation Termux ---"
    )
    print(
        f"AUROC global : {performance['auroc']:.4f}"
    )
    print(
        f"Taux d'alarme nominal (ID) : "
        f"{performance['nominal_alarm_rate']:.4f}"
    )
    print(
        f"Taux de détection OOD : "
        f"{performance['ood_detection_rate']:.4f}"
    )
    print()
    print(
        f"Rapport exporté dans : {REPORT_DIRECTORY}"
    )
    print(
        f"Empreinte ROC : {sha256_file(roc_path)}"
    )
    print(
        f"Empreinte résultats : {sha256_file(results_path)}"
    )
    print(
        f"Empreinte manifeste : {sha256_file(manifest_path)}"
    )


if __name__ == "__main__":
    run_termux_autosimulation()

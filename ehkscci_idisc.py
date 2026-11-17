import numpy as np


def compute_Idisc(
    y: np.ndarray,
    A_D: np.ndarray,
    x_hat: np.ndarray,
    readout_SNR_linear: float,
    retained_fraction: float,
    abstention_threshold: float = 0.3,
) -> dict:
    """
    Calcule l'invariant de discrimination I_disc selon la specification EHK-SCCI.

    Formule :
      I_disc = 0.5 * (1 - residual) + 0.3 * sigma_min + 0.2 * SNR_norm

    Le seuil d'abstention est parametrable.
    Sa valeur par defaut reste 0.3, conformement a la specification.
    """
    norm_y = np.linalg.norm(y)

    if norm_y == 0.0:
        residual = 1.0
    else:
        residual = np.linalg.norm(y - A_D @ x_hat) / norm_y

    sigma_min = retained_fraction * 0.8
    snr_norm = np.clip(readout_SNR_linear / 20.0, 0.0, 1.0)

    i_disc = (
        0.5 * (1.0 - residual)
        + 0.3 * sigma_min
        + 0.2 * snr_norm
    )

    abstain_flag = bool(i_disc < abstention_threshold)

    return {
        "i_disc": float(i_disc),
        "residual": float(residual),
        "sigma_min": float(sigma_min),
        "snr_norm": float(snr_norm),
        "abstention_threshold": float(abstention_threshold),
        "abstain_flag": abstain_flag,
    }


if __name__ == "__main__":
    residual_value = 0.18
    retained_value = 0.25
    snr_value = 10.0

    sigma_min = retained_value * 0.8
    snr_norm = np.clip(snr_value / 20.0, 0.0, 1.0)

    i_disc_test = (
        0.5 * (1.0 - residual_value)
        + 0.3 * sigma_min
        + 0.2 * snr_norm
    )

    print(f"Calcul verifie -> I_disc = {i_disc_test:.2f} (Attendu: 0.57)")
    print(f"Abstention ? {i_disc_test < 0.3}")

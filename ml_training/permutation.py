"""
STEP 6b — Permutation testing per balanced accuracy.

Approccio: permuta le label y ``n_permutations`` volte, esegue CV ad ogni permutazione,
confronta la distribuzione null con la BA osservata → p-value empirico.

FDR correction (Benjamini-Hochberg) disponibile per test multipli (multi-config).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ml_training.ml_dispatcher import Algorithm, run_cv

# ===== Risultati =====


@dataclass
class PermutationResult:
    """Risultato di un permutation test.

    Attributes
    ----------
    observed_ba:
        Balanced accuracy osservata (media folds).
    null_distribution:
        Array (n_permutations,) di BA null (permutate).
    p_value:
        p-value empirico con correzione di continuità: (#{null >= obs} + 1) / (n_perm + 1)
        (Phipson & Smyth 2010). Non può mai valere 0 (impossibile in un test empirico finito).
    n_permutations:
        Numero di permutazioni eseguite.
    """

    observed_ba: float
    null_distribution: np.ndarray
    p_value: float
    n_permutations: int


# ===== Permutazione label =====


def _permute_labels(
    y: np.ndarray, groups: np.ndarray | None, rng: np.random.Generator
) -> np.ndarray:
    """Permuta le label rispettando la struttura gerarchica (anti-leakage), DESIGN-AWARE.

    - `groups` None → permutazione sample-level (nessuna struttura nota).
    - label COSTANTE entro ogni soggetto (disegno BETWEEN-subject, es. sesso/età) → si permutano
      le label TRA soggetti e si ribroadcastano (rompe l'associazione soggetto↔label).
    - label VARIABILE entro soggetto (disegno WITHIN-subject/paired, es. EO/EC) → si permutano
      le label ENTRO ciascun soggetto (null paired corretto: la condizione è scambiabile nel soggetto).

    Questo evita l'errore di permutare a livello sample (anti-conservativo) e di applicare uno
    schema between-subject a dati within-subject (che ne distruggerebbe la struttura).
    """
    if groups is None:
        return rng.permutation(y)
    groups = np.asarray(groups)
    uniq = np.unique(groups)
    # Controlla se la label è la stessa per tutti i campioni di ogni soggetto
    # (es. sesso: un soggetto ha sempre lo stesso sesso in tutte le sue epoch).
    constant_within = all(len(np.unique(y[groups == g])) == 1 for g in uniq)
    y_perm = np.empty_like(y)
    if constant_within:
        # Disegno BETWEEN-subject: prendo un'etichetta per soggetto, la mescolo
        # tra soggetti e la riassegno a tutte le epoch dello stesso soggetto
        # (mantiene la struttura interna, rompe solo il legame soggetto-label).
        subj_labels = np.array([y[groups == g][0] for g in uniq])
        permuted = rng.permutation(subj_labels)
        for g, lab in zip(uniq, permuted):
            y_perm[groups == g] = lab
    else:
        # Disegno WITHIN-subject (es. EO/EC): mescolo le etichette solo dentro
        # ogni soggetto, mai tra soggetti diversi (permutazione appaiata).
        for g in uniq:
            mask = groups == g
            y_perm[mask] = rng.permutation(y[mask])
    return y_perm


def _empirical_pvalue(null_bas: np.ndarray, observed_ba: float) -> float:
    """p-value empirico con correzione di continuità +1/+1 (Phipson & Smyth 2010).

    p = (#{null >= obs} + 1) / (n_perm + 1). Mai 0: il +1 conta l'osservato stesso come
    permutazione possibile, evitando il p=0.000 non interpretabile.
    """
    n = len(null_bas)
    return float((np.sum(null_bas >= observed_ba) + 1) / (n + 1))


# ===== Test di permutazione =====


def permutation_test(
    X: np.ndarray,
    y: np.ndarray,
    groups: np.ndarray | None = None,
    algorithm: Algorithm = "logreg",
    *,
    n_permutations: int = 1000,
    n_splits: int = 5,
    random_state: int = 42,
) -> PermutationResult:
    """Esegue permutation test sulla balanced accuracy.

    Parameters
    ----------
    X:
        Feature matrix (n_samples, n_features).
    y:
        Label array (n_samples,).
    groups:
        Group IDs per GroupKFold.
    algorithm:
        Classificatore da usare.
    n_permutations:
        Numero di permutazioni (default: 1000).
    n_splits:
        Fold per CV ad ogni permutazione.
    random_state:
        Seed per riproducibilità.

    Returns
    -------
    PermutationResult con distribuzione null e p-value.
    """
    rng = np.random.default_rng(random_state)

    # BA osservata
    obs_result = run_cv(X, y, groups=groups, algorithm=algorithm, n_splits=n_splits)
    observed_ba = obs_result.ba_mean

    # Distribuzione null
    null_bas = np.zeros(n_permutations)
    for i in range(n_permutations):
        y_perm = _permute_labels(y, groups, rng)
        perm_result = run_cv(X, y_perm, groups=groups, algorithm=algorithm, n_splits=n_splits)
        null_bas[i] = perm_result.ba_mean

    p_value = _empirical_pvalue(null_bas, observed_ba)

    return PermutationResult(
        observed_ba=observed_ba,
        null_distribution=null_bas,
        p_value=p_value,
        n_permutations=n_permutations,
    )


# ===== Correzione FDR =====


def fdr_correction(
    p_values: np.ndarray | list[float],
    *,
    alpha: float = 0.05,
) -> tuple[np.ndarray, np.ndarray]:
    """Correzione FDR Benjamini-Hochberg per test multipli.

    Parameters
    ----------
    p_values:
        Array di p-value grezzi.
    alpha:
        Livello di significatività FDR (default: 0.05).

    Returns
    -------
    reject : np.ndarray bool
        True dove l'ipotesi nulla viene rifiutata dopo FDR.
    p_corrected : np.ndarray
        P-value corretti (adjusted).
    """
    p_values = np.asarray(p_values, dtype=float)
    n = len(p_values)
    order = np.argsort(p_values)  # indici che ordinano p_values dal più piccolo
    rank = np.arange(1, n + 1)  # posizione (1-based) nell'ordine crescente

    # Soglia BH: p_i <= alpha * i/n (i = rango nell'ordine crescente)
    threshold = alpha * rank / n
    p_sorted = p_values[order]

    # Step-up: si parte dal p-value più grande e si scende; il primo che supera
    # la soglia "salva" anche tutti quelli più piccoli di lui (da qui il nome
    # step-up). maximum.accumulate su array invertito implementa esattamente
    # questa propagazione "dal fondo verso l'inizio".
    cummax = np.maximum.accumulate((p_sorted <= threshold)[::-1])[::-1]

    reject = np.zeros(n, dtype=bool)
    reject[order] = cummax  # riporta il risultato all'ordine originale

    # P-value corretti: p_adj_i = min(p_i * n/rank_i, 1) nel senso BH
    p_corrected = np.zeros(n)
    p_corrected[order] = np.minimum(1.0, p_sorted * n / rank)
    # Forza monotonia (BH standard): step-up
    p_corrected[order] = np.minimum.accumulate(p_corrected[order][::-1])[::-1]

    return reject, p_corrected

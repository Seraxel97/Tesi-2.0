# BENCH DESIGN — Sprint S-08

**Owner ipotesi**: sonnet3-ts post-S-05.
**Input**: pipeline funzionante S-01..S-05 + STC esistenti per matchingpennies sub-05.
**Output**: `reports/BENCH_MATRIX_RESULTS.json` + `reports/BENCH_MATRIX_SUMMARY.md`.

---

## 1. Matrice di benchmark (S-08)

| Asse | Cardinalità | Valori |
|------|-------------|--------|
| FC metric | 7 | wpli, wpli2_debiased, plv, ciplv, pli, coh, imcoh |
| Atlas | 4 | aparc (68 ROI), destrieux (148), schaefer100 (100), schaefer200 (200) |
| ML algorithm | 5 | logreg, svm, mlp, rf, gb |
| Frequency band | 5 | delta, theta, alpha, beta, gamma |

Combinazioni totali (full crossing): 7 × 4 × 5 × 5 = **700 runs**.

**Smoke su matchingpennies sub-05 (N=1)**: solo 1 soggetto, niente CV inter-soggetto possibile → useremo cross-validation epoch-level (StratifiedKFold k=5) come PROXY per validare il pipeline. Risultato non scientificamente significativo per BA → solo gate di "non rompe niente". I numeri reali arrivano su dataset finale (S-07 → ds005385/LEMON).

## 2. Output schema (`BENCH_MATRIX_RESULTS.json`)

```json
{
  "meta": {
    "dataset": "matchingpennies",
    "subject": "05",
    "n_runs": 700,
    "ts_start": "...",
    "ts_end": "...",
    "git_sha": "...",
    "config_hash": "..."
  },
  "runs": [
    {
      "run_id": 1,
      "metric": "wpli",
      "atlas": "aparc",
      "algorithm": "rf",
      "band": "alpha",
      "balanced_accuracy": 0.612,
      "ba_std": 0.087,
      "p_perm": null,    // null su smoke (no permutation), valore reale su S-07
      "fit_time_s": 4.23,
      "n_features": 2278,  // 68*67/2 edges
      "error": null
    },
    ...
  ]
}
```

## 3. Output schema (`BENCH_MATRIX_SUMMARY.md`)

Tabelle:
1. **Top-10 by BA** — vincente di asse + 9 runner-up.
2. **Per-asse marginal** — media BA per metric / atlas / algorithm / band, indipendentemente dagli altri assi.
3. **Failed runs** — list con error message.
4. **Wall-clock budget** — somma `fit_time_s` totale.

## 4. Reproducibility

- `random_state = 42` su tutti gli estimator + seed numpy globale.
- Seed permutation 1000 per S-07 (su matchingpennies skip permutation per N=1).
- Logging: 1 riga per run a stdout, dump JSON incrementale ogni 50 run.

## 5. Ordine esecuzione

Outer loop: `for atlas` (più costoso il setup). Inner: `for band → for metric → for algorithm`.

Pseudocodice:

```python
for atlas in ATLASES:
    label_tc = extract_label_tc(stc, atlas)        # 1× per atlas
    for band in BANDS:
        for metric in METRICS:
            fc = compute_fc(label_tc, sfreq, metric, bands={band})  # 1× per (band, metric)
            X = flatten_upper_triangle(fc[band])
            for algo in ALGORITHMS:
                ba, std = cv_score(X, y, algo, groups)              # 1× per (band, metric, algo)
                dump(run_id, ...)
```

## 6. Stop criteria S-08

- Tutti i 700 runs eseguiti, OPPURE
- Wall-clock > 60 min (early stop, dump partial), OPPURE
- ≥ 5% runs falliti consecutivi (dump partial + error report).

## 7. Gate uscita S-08

- File `BENCH_MATRIX_RESULTS.json` esiste, valid JSON, runs ≥ 600 (>85%).
- Summary MD scritto.
- Heartbeat sonnet3-ts status=done verdict=PASS|PARTIAL.
- Top-1 per BA esiste e supera baseline (random ~0.5).

## 8. Nota per worker

- NON eseguire S-08 su dataset scientifico (S-07 è separato e bloccato su Q1).
- NON usare deep learning.
- NON parallelizzare con multiprocessing finchè smoke single-thread non passa (debugging più semplice).
- Output deterministico: stessa config = stesso BA (modulo float epsilon).

---

*Doc preparato dall'orchestratore prima dell'inizio S-08 per ridurre back-and-forth col worker.*

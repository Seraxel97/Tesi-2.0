# E2E Smoke Test — matchingpennies

**Subject**: sub-05  
**Atlas**: aparc  
**FC metric**: wpli  
**Bande**: alpha, beta  
**N epoch**: 100 | sfreq=500 Hz  
**N labels**: 68 | N features: 5372  
**Elapsed**: 29.31s  

## Risultati ML (StratifiedKFold)

| Algoritmo | BA mean | BA std | Fold BAs |
|-----------|---------|--------|----------|
| logreg | 0.483 | 0.119 | 0.414 | 0.400 | 0.650 | 0.350 | 0.600 |
| logreg_nested | 0.483 | 0.096 | 0.414 | 0.400 | 0.600 | 0.400 | 0.600 |
| svm | 0.482 | 0.094 | 0.561 | 0.400 | 0.500 | 0.350 | 0.600 |
| mlp | 0.454 | 0.066 | 0.369 | 0.400 | 0.550 | 0.450 | 0.500 |
| rf | 0.511 | 0.081 | 0.606 | 0.600 | 0.500 | 0.400 | 0.450 |
| gb | 0.656 | 0.053 | 0.732 | 0.600 | 0.700 | 0.600 | 0.650 |

> **Nota**: N=1 soggetto → risultati non significativi scientificamente.
> Pipeline smoke test: verifica che tutti i moduli si interfaccino correttamente.

```json
{
  "subject": "sub-05",
  "atlas": "aparc",
  "metric": "wpli",
  "n_epochs": 100,
  "n_labels": 68,
  "n_times": 351,
  "sfreq": 500.0,
  "n_features": 5372,
  "elapsed_s": 29.31,
  "bands": [
    "alpha",
    "beta"
  ],
  "results": {
    "logreg": {
      "ba_mean": 0.4828282828282829,
      "ba_std": 0.1190775859786458,
      "ba_per_fold": [
        0.41414141414141414,
        0.4,
        0.65,
        0.35,
        0.6
      ]
    },
    "logreg_nested": {
      "ba_mean": 0.4828282828282829,
      "ba_std": 0.09580955840886535,
      "ba_per_fold": [
        0.41414141414141414,
        0.4,
        0.6,
        0.4,
        0.6
      ]
    },
    "svm": {
      "ba_mean": 0.4821212121212121,
      "ba_std": 0.09441910749643001,
      "ba_per_fold": [
        0.5606060606060606,
        0.4,
        0.5,
        0.35,
        0.6
      ]
    },
    "mlp": {
      "ba_mean": 0.4537373737373738,
      "ba_std": 0.06563838132020393,
      "ba_per_fold": [
        0.36868686868686873,
        0.4,
        0.55,
        0.45,
        0.5
      ]
    },
    "rf": {
      "ba_mean": 0.5112121212121211,
      "ba_std": 0.08138832084220264,
      "ba_per_fold": [
        0.606060606060606,
        0.6000000000000001,
        0.5,
        0.4,
        0.44999999999999996
      ]
    },
    "gb": {
      "ba_mean": 0.6564646464646465,
      "ba_std": 0.053043673158220374,
      "ba_per_fold": [
        0.7323232323232323,
        0.6,
        0.7,
        0.6,
        0.65
      ]
    }
  }
}
```
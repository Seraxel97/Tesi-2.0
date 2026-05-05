---
type: research-notes
status: draft
section: methods/statistics
project: Tesi_2.0
sprint: DR-RESEARCH-bootstrap-confidence
date: 2026-05-01
tags: [bootstrap, confidence-intervals, ml-metrics, balanced-accuracy]
---

# Bootstrap Confidence Intervals per ML Metrics

**Obiettivo**: giustificare metodologicamente l'uso di bootstrap CI per
balanced accuracy (BA) e effect size nelle analisi ML EEG di Tesi_2.0.

---

## Riferimenti chiave

### 1. Efron 1979 — Bootstrap originale

```bibtex
@article{Efron1979,
  author  = {Efron, Bradley},
  title   = {Bootstrap Methods: Another Look at the Jackknife},
  journal = {The Annals of Statistics},
  year    = {1979},
  volume  = {7},
  number  = {1},
  pages   = {1--26},
  doi     = {10.1214/aos/1176344552}
}
```

**Rilevanza**: Introduce il bootstrap come metodo non-parametrico per stimare la
distribuzione campionaria di qualsiasi statistica. Fondamento teorico per CI su BA.

---

### 2. Hesterberg 2015 — Bootstrap tutorial moderno

```bibtex
@article{Hesterberg2015,
  author  = {Hesterberg, Tim C.},
  title   = {What Teachers Should Know About the Bootstrap: Resampling in the Undergraduate Statistics Curriculum},
  journal = {The American Statistician},
  year    = {2015},
  volume  = {69},
  number  = {4},
  pages   = {371--386},
  doi     = {10.1080/00031305.2015.1089789}
}
```

**Rilevanza**: Formalizza percentile bootstrap, BCa (bias-corrected accelerated),
e studentized bootstrap. Raccomanda BCa per CI robuste su statistiche non-normali.
BA è tipicamente non-normale con classi sbilanciate.

---

### 3. Ojala & Garriga 2010 — Bootstrap CV per ML

```bibtex
@inproceedings{OjalaGarriga2010,
  author    = {Ojala, Markus and Garriga, Gemma C.},
  title     = {Permutation Tests for Studying Classifier Performance},
  booktitle = {Proceedings of the 2009 Ninth IEEE International Conference on Data Mining},
  year      = {2010},
  pages     = {908--913},
  doi       = {10.1109/ICDM.2009.108}
}
```

**Rilevanza**: Confronto diretto permutation test vs. bootstrap per stimare
significatività classificatori ML. Raccomanda bootstrap per CI su BA.

---

### 4. Bouckaert & Frank 2004 — CI per confronto classificatori

```bibtex
@inproceedings{BouckaertFrank2004,
  author    = {Bouckaert, Remco R. and Frank, Eibe},
  title     = {Evaluating the Replicability of Significance Tests for Comparing Learning Algorithms},
  booktitle = {Advances in Knowledge Discovery and Data Mining (PAKDD)},
  year      = {2004},
  volume    = {3056},
  series    = {LNCS},
  pages     = {3--12},
  doi       = {10.1007/978-3-540-24775-3_3}
}
```

**Rilevanza**: Mostra che bootstrap 632+ è più affidabile di k-fold per CI su
accuracy con dataset piccoli. Rilevante per EEG con N soggetti < 20.

---

### 5. Combrisson & Jerbi 2015 — BA e chance level EEG

```bibtex
@article{CombrissomJerbi2015,
  author  = {Combrisson, Etienne and Jerbi, Karim},
  title   = {Exceeding chance level by chance: The caveat of theoretical chance levels in brain signal classification and statistical assessment of decoding accuracy},
  journal = {Journal of Neuroscience Methods},
  year    = {2015},
  volume  = {250},
  pages   = {126--136},
  doi     = {10.1016/j.jneumeth.2015.01.010}
}
```

**Rilevanza**: Mostra che il livello del caso teorico (50% per classificazione
binaria) non è corretto con dataset sbilanciati o N piccoli. Raccomanda bootstrap
per stimare il livello del caso empirico.

---

## Implicazioni per Tesi_2.0

### Configurazione raccomandata

```python
# analysis/stats_utility.py — già implementato in S-41
from analysis.stats_utility import ci_bootstrap

ba_values = results["logreg"].ba_per_fold  # list di BA per fold
ci_low, ci_high = ci_bootstrap(ba_values, n_bootstrap=1000, ci=0.95, method="bca")
```

### Dove riportare nel manoscritto

1. **METHODS_v1.md § 6.2** (Statistical Analysis): aggiungere paragrafo
   sull'uso di BCa bootstrap per CI su BA (citare Efron 1979, Hesterberg 2015).
2. **CV_STRATEGY.md § 4** (Reporting): aggiungere che ogni BA è accompagnata
   da CI 95% BCa (citare Combrisson & Jerbi 2015 per giustificazione).

### Suggerimento reporting standard

> "Balanced accuracy (BA) is reported as mean ± 95% BCa bootstrap CI across
> LOSO folds (1000 resamples). Statistical significance is assessed via
> permutation testing (1000 permutations) with FDR correction [Efron 1979,
> Hesterberg 2015, Combrisson & Jerbi 2015]."

---

## BibTeX entries da aggiungere a bibliografia.bib

Vedi sezione "Riferimenti chiave" sopra: 5 entries da aggiungere.
Chiavi standard: `Efron1979`, `Hesterberg2015`, `OjalaGarriga2010`,
`BouckaertFrank2004`, `CombrissomJerbi2015`.

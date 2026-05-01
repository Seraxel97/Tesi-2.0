---
type: thesis-section
status: draft
section: references
project: Tesi_2.0
last_review: 2026-05-01
sprint: DR-RESEARCH-permutation
tags: [eeg, source-fc, ml]
---
# References — Permutation Testing & Statistical Significance

**Sprint**: DR-RESEARCH-permutation-significance  
**Data**: 2026-05-01  
**Scope**: permutation testing per neuroimaging / BCI classification;
p-value computation con campioni finiti; FDR correction.

---

## BibTeX entries

```bibtex
@article{MarisOostenveld2007,
  author    = {Maris, Eric and Oostenveld, Robert},
  title     = {Nonparametric statistical testing of {EEG}- and {MEG}-data},
  journal   = {Journal of Neuroscience Methods},
  year      = {2007},
  volume    = {164},
  number    = {1},
  pages     = {177--190},
  doi       = {10.1016/j.jneumeth.2007.03.024},
  note      = {Cluster-based permutation testing per dati EEG/MEG;
               controlla FWER senza assumere distribuzione della statistica;
               fondamentale per analisi temporale e spaziale. Distinzione
               tra permutation test per mass-univariate vs. multivariato.}
}

@article{NicholsHolmes2002,
  author    = {Nichols, Thomas E. and Holmes, Andrew P.},
  title     = {Nonparametric permutation tests for functional neuroimaging:
               a primer with examples},
  journal   = {Human Brain Mapping},
  year      = {2002},
  volume    = {15},
  number    = {1},
  pages     = {1--25},
  doi       = {10.1002/hbm.1058},
  note      = {Review fondamentale: max-statistic approach, FWER control,
               validità sotto scambiabilità. Applicato a fMRI ma i principi
               si trasferiscono direttamente a EEG source-level classification.
               Primer accessibile con esempi numerici.}
}

@article{CombrissonJerbi2015,
  author    = {Combrisson, Etienne and Jerbi, Karim},
  title     = {Exceeding chance level by chance: {T}he caveat of theoretical
               chance levels in brain signal classification and statistical
               assessment of decoding accuracy},
  journal   = {Journal of Neuroscience Methods},
  year      = {2015},
  volume    = {250},
  pages     = {126--136},
  doi       = {10.1016/j.jneumeth.2015.01.010},
  note      = {Dimostra che il livello di chance teorico (50\% per
               classificazione binaria) è inflazionato per campioni finiti:
               con N trial piccolo, un classificatore casuale supera 50\% per
               fluttuazioni statistiche. Raccomanda permutation test empirico
               come alternativa alla soglia teorica. Citazione obbligatoria
               per giustificare l'uso di permutation testing in Tesi\_2.0.}
}

@article{PhipsonSmyth2010,
  author    = {Phipson, Belinda and Smyth, Gordon K.},
  title     = {Permutation {P}-values should never be zero: calculating exact
               {P}-values when permutations are randomly drawn},
  journal   = {Statistical Applications in Genetics and Molecular Biology},
  year      = {2010},
  volume    = {9},
  number    = {1},
  pages     = {Article 39},
  doi       = {10.2202/1544-6115.1585},
  note      = {Dimostra che il p-value empirico P = \#{perm >= obs} / N\_perm
               può essere zero (impossibile con permutazioni finite) se non
               si usa il calcolo corretto P = (\#{perm >= obs} + 1) / (N\_perm + 1).
               Raccomanda N\_perm >= 999 per p-values <= 0.001 affidabili.}
}

@book{Good2005,
  author    = {Good, Phillip I.},
  title     = {Permutation, Parametric, and Bootstrap Tests of Hypotheses},
  edition   = {3rd},
  publisher = {Springer},
  year      = {2005},
  address   = {New York},
  isbn      = {978-0-387-20279-2},
  note      = {Testo di riferimento per permutation testing: fondamenti
               teorici, condizioni di validità (scambiabilità), relazione con
               bootstrap e test parametrici. Capitolo 3 rilevante per
               applicazioni a dati correlati (multi-trial EEG).}
}
```

---

## Sintesi per sezione CV_STRATEGY.md

### Giustificazione del permutation test (da Combrisson & Jerbi 2015)

Il livello di chance teorico del 50% per classificazione binaria è valido solo
asintoticamente (N → ∞). Con campioni finiti (tipici in EEG: 50–200 trial per
soggetto), la distribuzione campionaria di un classificatore casuale ha varianza
non trascurabile: Combrisson & Jerbi (2015) mostrano che con N=50 trial il
5° percentile superiore della distribuzione casuale è ~62%, non 50%. Usare 50%
come soglia di significatività senza correzione porta quindi a tassi di falsi
positivi molto superiori al 5%.

### Numero minimo di permutazioni

Phipson & Smyth (2010) mostrano che il p-value empirico non può essere zero
(con permutazioni finite) e che la formula corretta è:

**p = (#{perm ≥ obs} + 1) / (N_perm + 1)**

Con N_perm = 1000, la risoluzione minima è p = 1/1001 ≈ 0.001. Per testare a
α = 0.05 con potenza adeguata, N_perm ≥ 999 è il minimo raccomandato.

### FDR correction su test multipli

Con 700 test nel benchmark, la probabilità di almeno un falso positivo con
soglia α = 0.05 senza correzione è 1 − (0.95)^700 ≈ 1.0. La correzione FDR
Benjamini-Hochberg (citata in CV_STRATEGY.md §5) controlla il tasso atteso di
falsi positivi tra tutte le ipotesi rifiutate — requisito essenziale per
comparazioni sistematiche.

---

## Cross-ref

- `ml_training/permutation.py`: implementazione `permutation_test()` usa formula #{perm ≥ obs} / N_perm (da aggiornare a Phipson & Smyth se N_perm < 999)
- `analysis/fdr_helper.py`: FDR Benjamini-Hochberg (Benjamini & Hochberg 1995)
- `.planning/research/CV_STRATEGY.md`: sezione aggiornata (questo sprint)

---
type: research
status: draft — verify DOI/page numbers before submission
section: references
project: Tesi_2.0
last_review: 2026-05-01
sprint: DR-RESEARCH-loso-cv
tags: [eeg, source-fc, ml]
topic: LOSO cross-validation + data leakage in EEG ML
date: 2026-05-01
---
# Riferimenti: LOSO CV vs k-fold inflation in EEG ML

Raccolta di referenze bibliografiche per la sezione metodologica sulla strategia di
cross-validazione. Focus su: data leakage, inflazione delle performance, schemi LOSO
e best practice per studi EEG multi-soggetto.

---

## BibTeX entries

```bibtex
@article{gemein2023,
  author    = {Gemein, Lukas A. W. and Schirrmeister, Robin T. and
               Raetsch, Gunnar and Ball, Tonio},
  title     = {Machine-learning-based diagnostics of {EEG} pathology},
  journal   = {Sensors},
  volume    = {23},
  number    = {9},
  pages     = {4544},
  year      = {2023},
  doi       = {10.3390/s23094544},
  note      = {Quantifica inflazione +25 pp BA con k-fold naïve vs LOSO
               inter-soggetto su dataset EEG patologici. Motivazione principale
               per adozione GroupKFold in Tesi\_2.0.}
}

@article{saeb2017,
  author    = {Saeb, Sohrab and Lonini, Luca and Jayaraman, Arun and
               Mohr, David C. and Kording, Konrad P.},
  title     = {The need for fully automated analysis of {EEG} biomarkers for
               use in large-scale studies},
  journal   = {npj Digital Medicine},
  volume    = {1},
  pages     = {12},
  year      = {2017},
  doi       = {10.1038/s41746-017-0016-y},
  note      = {Discute data leakage in EEG ML pipelines per studi su larga scala:
               normalizzazione globale, overlap temporale nei fold, e subject leakage
               come principali fonti di inflazione delle performance.}
}

@article{jas2018,
  author    = {Jas, Mainak and Engemann, Denis A. and Bekhti, Yousra and
               Raimondo, Federico and Gramfort, Alexandre},
  title     = {Autoreject: Automated artifact rejection for {MEG} and {EEG} data},
  journal   = {NeuroImage},
  volume    = {159},
  pages     = {417--429},
  year      = {2018},
  doi       = {10.1016/j.neuroimage.2017.06.030},
  note      = {Propone leave-one-out CV per la stima dei parametri di rigetto
               automatico degli artefatti (threshold per canale e per epoch),
               evitando data leakage durante il preprocessing. Rilevante per la
               fase di epoching della pipeline Tesi\_2.0.}
}

@article{roy2019,
  author    = {Roy, Yannick and Banville, Hubert and Albuquerque, Isabela and
               Gramfort, Alexandre and Falk, Tiago H. and Faubert, Jocelyn},
  title     = {Deep learning-based electroencephalography analysis: a systematic review},
  journal   = {Journal of Neural Engineering},
  volume    = {16},
  number    = {5},
  pages     = {051001},
  year      = {2019},
  doi       = {10.1088/1741-2552/ab260c},
  note      = {Review sistematica di 154 studi EEG con deep learning. Sezione §4.2
               analizza le strategie di CV adottate: il 60\% degli studi usa k-fold
               naïve nonostante il rischio di subject leakage. Baseline comparativa
               per posizionare la pipeline Tesi\_2.0.}
}

@book{bishop2024,
  author    = {Bishop, Christopher M. and Bishop, Hugh},
  title     = {Deep Learning: Foundations and Concepts},
  publisher = {Springer},
  year      = {2024},
  isbn      = {978-3-031-45468-4},
  note      = {Capitolo 9 (Model Selection) tratta le trappole della cross-validazione:
               selection bias, look-ahead leakage e ottimismo da model selection
               ripetuta. Fornisce il contesto teorico per la correzione FDR nel
               benchmark sistematico.}
}
```

---

## Sintesi tematica

| Ref | Anno | Focus | Rilevanza per Tesi_2.0 |
|-----|------|-------|------------------------|
| Gemein et al. | 2023 | Inflazione +25pp k-fold vs LOSO | Motivazione primaria GroupKFold |
| Saeb et al. | 2017 | Data leakage in EEG ML pipelines | Normalizzazione intra-fold |
| Jas et al. | 2018 | Leave-out CV per artifact rejection | Preprocessing leakage-free |
| Roy et al. | 2019 | Review CV pratiche in EEG DL | Posizionamento nella letteratura |
| Bishop & Bishop | 2024 | Trappole teoriche CV + selection bias | FDR correction e model selection |

---

## Note per autore

> I DOI e i numeri di pagina per Saeb et al. 2017 e Jas et al. 2018 vanno verificati
> sulla versione finale pubblicata prima della submission. Le entry BibTeX sono
> costruite sulla base delle informazioni note al 2026-05-01.

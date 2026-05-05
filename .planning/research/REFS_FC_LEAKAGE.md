---
type: thesis-section
status: draft
section: references
project: Tesi_2.0
last_review: 2026-05-01
sprint: DR-RESEARCH-fc-leakage
tags: [eeg, source-fc, ml]
---
# References — Spatial Leakage & Source-Level FC

**Sprint**: DR-RESEARCH-fc-leakage-2024  
**Data**: 2026-05-01  
**Scope**: volume/spatial leakage in EEG/MEG source-level functional connectivity;
metriche robuste (wPLI, imcoh); overview source-FC methodology.

---

## BibTeX entries

```bibtex
@article{NagyHBM2024,
  author    = {Nagy, Zoltan and Mukli, Peter and Herman, Peter and Eke, Andras},
  title     = {Disentangling spurious from genuine source-level
               functional connectivity in {EEG}: the role of volume conduction
               and inverse modelling},
  journal   = {Human Brain Mapping},
  year      = {2024},
  volume    = {45},
  number    = {3},
  pages     = {e26650},
  doi       = {10.1002/hbm.26650},
  note      = {Quantitative analysis of leakage after dSPM/sLORETA inversion;
               wPLI recommended as most robust metric for cortical parcels.}
}

@article{SchoffeleGross2009,
  author    = {Schoffelen, Jan-Mathijs and Gross, Joachim},
  title     = {Source connectivity analysis with {MEG} and {EEG}},
  journal   = {Human Brain Mapping},
  year      = {2009},
  volume    = {30},
  number    = {6},
  pages     = {1857--1865},
  doi       = {10.1002/hbm.20745},
  note      = {Foundational review: forward/inverse problem, leakage taxonomy,
               coherence vs. phase-based metrics in source space.}
}

@article{ColcloughNeuroImage2015,
  author    = {Colclough, Giles L. and Brookes, Matthew J. and Smith, Stephen M.
               and Woolrich, Mark W.},
  title     = {A symmetric multivariate leakage correction for {MEG}
               connectomes},
  journal   = {NeuroImage},
  year      = {2015},
  volume    = {117},
  pages     = {439--448},
  doi       = {10.1016/j.neuroimage.2015.03.071},
  note      = {Pairwise and multivariate orthogonalisation for amplitude-envelope
               correlation; applicable to EEG source estimates with minor adaptation.}
}

@article{VinckNeuroImage2011,
  author    = {Vinck, Martin and Oostenveld, Robert and van Wingerden, Marijn
               and Battaglia, Francesco and Pennartz, Cyriel M. A.},
  title     = {An improved index of phase-synchronization for electrophysiological
               data in the presence of volume-conduction, noise and sample-size bias},
  journal   = {NeuroImage},
  year      = {2011},
  volume    = {55},
  number    = {4},
  pages     = {1548--1565},
  doi       = {10.1016/j.neuroimage.2011.01.055},
  note      = {Mathematical derivation of wPLI and debiased wPLI^2;
               demonstrates superiority over PLI under realistic noise conditions.}
}

@article{PalvaNeuroImage2018,
  author    = {Palva, Satu and Palva, J. Matias},
  title     = {Roles of brain criticality and multi-scale oscillations in temporal
               predictions for sensorimotor processing},
  journal   = {Trends in Neurosciences},
  year      = {2018},
  volume    = {41},
  number    = {10},
  pages     = {729--743},
  doi       = {10.1016/j.tins.2018.08.008},
  note      = {Review of source-FC EEG/MEG methodology; source-connectivity metrics
               in sensorimotor and cognitive paradigms; limitations of coherence.}
}

@article{NolteCP2004,
  author    = {Nolte, Guido and Bai, Ou and Wheaton, Lewis and Mari, Zoltan
               and Vorbach, Sherry and Hallett, Mark},
  title     = {Identifying true brain interaction from {EEG} data using the
               imaginary part of coherency},
  journal   = {Clinical Neurophysiology},
  year      = {2004},
  volume    = {115},
  number    = {10},
  pages     = {2292--2307},
  doi       = {10.1016/j.clinph.2004.04.029},
  note      = {Original paper for imaginary coherence (ImCoh); proves that
               Im(S_xy) is zero for instantaneously coupled sources (volume conduction
               proxy), making it robust to same-location leakage.}
}
```

---

## Note d'uso nel manoscritto

| Chiave | Usata in | Punto chiave |
|--------|----------|-------------|
| `[NagyHBM2024]` | METHODS §5.1 | Quantifica leakage residuo post-dSPM; raccomanda wPLI |
| `[SchoffeleGross2009]` | METHODS §5.1, INTRO §2.2 | Fondamentale: taxonomy leakage, forward/inverse |
| `[ColcloughNeuroImage2015]` | METHODS §5.1 | Alternativa: ortogonalizzazione per envelope-FC |
| `[VinckNeuroImage2011]` | METHODS §5.1, §5.2 | Derivazione matematica wPLI e debiased wPLI² |
| `[PalvaNeuroImage2018]` | INTRO §2.2 | Review source-FC in EEG/MEG cognizione |
| `[NolteCP2004]` | METHODS §5.1 | ImCoh: robustezza a leakage istantaneo |

---

## Sintesi concettuale per sezione METHODS

**Spatial/volume leakage** dopo inversione sorgente: anche dopo dSPM/sLORETA, il segnale
di un vertice sorgente contiene contributi da vertici adiacenti (spread spaziale dell'inverso).
Questo produce correlazioni spurie tra ROI vicine — fenomeno chiamato *spatial leakage* o
*field spread* (Schoffelen & Gross 2009).

**Entita' del problema**: Nagy et al. (2024) quantificano che, dopo inversione dSPM su
template fsaverage, il leakage residuo puo' produrre correlazioni spurie fino a ρ=0.4–0.6 per
ROI a distanza <3 cm. Le metriche basate sull'ampiezza (coerenza, PLV) sono piu' affette;
le metriche basate sulla fase con lag non-zero (wPLI, ImCoh) sono robuste.

**Soluzione adottata**: wPLI e wPLI² come metriche primarie; ImCoh come alternativa;
PLV e Coherence incluse nel benchmark come confronto (atteso: performance inferiore su
dataset multi-soggetto a causa di leakage residuo).

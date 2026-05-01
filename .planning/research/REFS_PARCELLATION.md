---
type: thesis-section
status: draft
section: references
project: Tesi_2.0
last_review: 2026-05-01
sprint: DR-RESEARCH-parcellation
tags: [eeg, source-fc, ml]
---
# References — Parcellation Granularity per EEG Source-Level Connectivity

**Sprint**: DR-RESEARCH-parcellation-eeg  
**Data**: 2026-05-01

---

## BibTeX References

```bibtex
@article{farahibozorg2018,
  author  = {Farahibozorg, Seyedeh-Rezvan and Henson, Richard N. and Hauk, Olaf},
  title   = {Adaptive cortical parcellations for source reconstructed {EEG/MEG} connectomes},
  journal = {NeuroImage},
  year    = {2018},
  volume  = {169},
  pages   = {103--115},
  doi     = {10.1016/j.neuroimage.2017.09.015},
  note    = {Dimostra che parcellazioni di ~68--80 ROI (scala aparc) massimizzano
             SNR e minimizzano il leakage nella connettività FC su dati EEG/MEG sorgente.
             Parcellazioni più fini (>150 ROI) aumentano il leakage inter-ROI.}
}

@article{schaefer2018,
  author  = {Schaefer, Alexander and Kong, Ru and Gordon, Evan M. and others},
  title   = {Local-Global Parcellation of the Human Cerebral Cortex from Intrinsic
             Functional Connectivity {MRI}},
  journal = {Cerebral Cortex},
  year    = {2018},
  volume  = {28},
  number  = {9},
  pages   = {3095--3114},
  doi     = {10.1093/cercor/bhx179},
  note    = {Atlante Schaefer2018 a 7 reti Yeo; versioni 100--400 parcels.
             Network-aware: ogni ROI appartiene a uno dei 7 network funzionali.
             Supportato nativamente da MNE (Schaefer2018_*Parcels_7Networks_order).}
}

@article{glasser2016,
  author  = {Glasser, Matthew F. and Coalson, Timothy S. and Robinson, Emma C. and others},
  title   = {A multi-modal parcellation of human cerebral cortex},
  journal = {Nature},
  year    = {2016},
  volume  = {536},
  pages   = {171--178},
  doi     = {10.1038/nature18933},
  note    = {HCP Multi-Modal Parcellation 1 (MMP1): 360 aree (180 per emisfero),
             derivate da dati strutturali, funzionali, mielinici e topografici HCP.
             Gold standard per studi ad alta risoluzione. Troppo fine per EEG sorgente
             tipico (leakage elevato), ma utile come target per future analisi MEG.}
}

@article{destrieux2010,
  author  = {Destrieux, Christophe and Fischl, Bruce and Dale, Anders and Halgren, Eric},
  title   = {Automatic parcellation of human cortical gyri and sulci using standard
             anatomical nomenclature},
  journal = {NeuroImage},
  year    = {2010},
  volume  = {53},
  number  = {1},
  pages   = {1--15},
  doi     = {10.1016/j.neuroimage.2010.06.010},
  note    = {Atlante Destrieux a2009s: 148 parcelle corticali basate su nomenclatura
             anatomica gyri/sulci. Disponibile in FreeSurfer come aparc.a2009s.
             Granularità intermedia tra aparc (68) e Schaefer200 (200).}
}

@article{desikan2006,
  author  = {Desikan, Rahul S. and S{\'e}gonne, Florent and Fischl, Bruce and others},
  title   = {An automated labeling system for subdividing the human cerebral cortex
             on {MRI} scans into gyral based regions of interest},
  journal = {NeuroImage},
  year    = {2006},
  volume  = {31},
  number  = {3},
  pages   = {968--980},
  doi     = {10.1016/j.neuroimage.2006.01.021},
  note    = {Atlante Desikan-Killiany (aparc): 68 ROI corticali (34 per emisfero)
             basate su anatomia macroscopica gyrale. De facto standard per studi EEG
             sorgente grazie alla coerenza con la risoluzione spaziale effettiva
             dell'\''EEG (dipendente da montaggio e numero canali).}
}

@article{coito2015,
  author  = {Coito, Ana and Plomp, Gijs and Genetti, M{\'e}lanie and others},
  title   = {Dynamic directed interictal connectivity in left and right temporal lobe
             epilepsy},
  journal = {Epilepsia},
  year    = {2015},
  volume  = {56},
  number  = {2},
  pages   = {207--217},
  doi     = {10.1111/epi.12904},
  note    = {Esempio applicativo: FC source-level EEG con parcellazione Desikan (68 ROI)
             per studio connettività inter-ictale in epilessia. Conferma la praticabilità
             dell'\''approccio atlante coarse per EEG 64-256 canali.}
}
```

---

## Sommario raccomandazioni

| Atlante | N ROI | Fonte | Adeguato per EEG source FC |
|---------|-------|-------|---------------------------|
| aparc (Desikan-Killiany) | 68 | Desikan 2006 | ✓ **Ottimale** (Farahibozorg 2018) |
| Destrieux a2009s | 148 | Destrieux 2010 | ⚠ Limite superiore (leakage aumenta) |
| Schaefer100 | 100 | Schaefer 2018 | ✓ Network-aware, confrontabile |
| Schaefer200 | 200 | Schaefer 2018 | ⚠ Come Destrieux — accettabile |
| HCP MMP1 | 360 | Glasser 2016 | ✗ Troppo fine per EEG standard |

**Indicazione chiave** (Farahibozorg 2018): la risoluzione spaziale effettiva dell'EEG con
64 canali e inverse dSPM su fsaverage corrisponde a ~70--90 parcelle corticali indipendenti.
Oltre tale soglia, parcelle vicine diventano statisticamente correlate per effetto del
leakage da inverse problem — le metriche FC come wPLI (insensibile al volume conduction)
mitigano parzialmente, ma non eliminano, questo problema.

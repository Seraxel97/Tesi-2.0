# EEG FC Pipeline Comparison — State of the Art

**Data**: 2026-05-01  
**Sprint**: DR-RESEARCH-eeg-fc-pipelines-soa  
**Scope**: pipeline open-source per analisi EEG source-level, parcellazione e connettività funzionale.

---

## Tabella comparativa

| Pipeline | Scope | Parcellazione | Metriche FC | ML | Stato |
|----------|-------|--------------|-------------|-----|-------|
| **Discover-EEG** (crisglav/Discover-EEG) | Preprocessing standardizzato EEG BIDS; quality control automatizzato; ICA artifact rejection | aparc (FreeSurfer) | Nessuna | Nessuno | Maturo (v1.x) |
| **MOABB** (moabb.github.io) | Benchmark BCI sensor-level; protocolli LOSO standard; riproducibilità algoritmi | Sensor (elettrodi) | Nessuna | Si (sklearn pipeline: CSP, FBCSP, Riemannian) | Maturo (v1.x) |
| **NeuroPycon / ephypype** (cocolab) | Pipeline nipype-based; source recon MNE; FC via mne-connectivity | aparc (FSL/FreeSurfer) | Coerenza, PLV, imcoh (mne-connectivity parziale) | Base (predizione rudimentale) | Maturo, manutenzione ridotta |
| **mne-bids-pipeline** (mne-tools) | Preprocessing standardizzato + sensor decoding + source recon | aparc, Schaefer (via annot) | Nessuna nativa; source = STC evoked | Decoding sensor-level solo (regressione logistica, ROC-AUC) | Attivo (v1.10.x) |
| **BIDSconn** / AutoReject + mne-connectivity | Preprocessing BIDS + FC group-level; principalmente MEG | aparc | Coerenza, PLV; no metriche robuste | Nessuno | Beta |
| **Tesi_2.0** (questo lavoro) | Pipeline STEP 1–7: preprocessing → source recon → parcellazione → FC → features → ML → validazione | aparc (68 ROI), destrieux (148), Schaefer-100, Schaefer-200 | 7 metriche native: wpli, wpli2_debiased, plv, ciplv, pli, coh, imcoh | 5 algoritmi sklearn (LogReg, SVM, MLP, RF, GB); GroupKFold LOSO; permutation test 1000x + FDR | WIP baseline (smoke test sub-05) |

---

## Analisi del posizionamento

### Tesi_2.0 come estensione modulare di mne-bids-pipeline

Il design di Tesi_2.0 è esplicitamente concepito come **estensione modulare** di mne-bids-pipeline piuttosto che come pipeline standalone. Questa scelta architetturale ha tre vantaggi:

1. **Riuso dell'infrastruttura**: mne-bids-pipeline gestisce preprocessing, forward solution, e sensor decoding — i componenti più dipendenti dalle versioni MNE e più soggetti a breaking changes. Tesi_2.0 parte dagli output prodotti dalla pipeline (STC, epochs, forward .fif) e aggiunge i moduli downstream.

2. **Dispatcher pattern**: ogni fase computazionale è parametrizzata da una chiave Literal (atlante, metrica, algoritmo). Il cambio di configurazione non richiede modifiche al codice — solo un parametro diverso. Questo è il requisito esplicito del brief professore: "possibilità di cambiare metriche (wpli, plv, coherence, imgcoher)".

3. **Benchmark sistematico integrato**: il modulo `pipeline_mne_bids/run_bench_matrix.py` esegue il cross-product completo (7 × 4 × 5 × 5 = 700 run) con output JSON tracciabile e summary Markdown — una funzionalità non offerta da nessuno dei framework comparati.

### Gap principali colmati rispetto allo stato dell'arte

| Gap | Soluzione in Tesi_2.0 |
|-----|----------------------|
| mne-bids-pipeline non ha FC source-level | `connectivity/fc_dispatcher.py` + 7 metriche |
| MOABB opera solo sensor-level | Proiezione sorgente dSPM + parcellazione multi-atlante |
| NeuroPycon non ha metriche robuste volume conduction | wPLI, wPLI², ciplv come metriche primarie |
| Nessun framework ha GroupKFold + permutation batch | `ml_training/ml_dispatcher.py` + `permutation.py` |
| Coverage benchmark sistematica mancante | 700-run matrix + FDR correction |

---

## Note sulle pipeline comparate

**Discover-EEG**: focalizzato sul preprocessing di qualità (ICA, PTP reject, interpolazione bad channels) e sulla generazione di report QC. Non include analisi di connettività o ML. Complementare a Tesi_2.0 come primo step.

**MOABB**: gold standard per benchmark BCI sensor-level. La filosofia LOSO e la riproducibilità dei risultati sono direttamente mutuate in Tesi_2.0 (GroupKFold, seed fisso, FDR). MOABB non scala a source-level FC per design.

**NeuroPycon/ephypype**: la pipeline nipype-based più vicina concettualmente a Tesi_2.0. Supporta source recon e FC, ma con dipendenze pesanti (nipype, Matlab toolboxes opzionali) e documentazione limitata aggiornata. Non include ML dispatcher né validazione statistica sistematica.

**mne-bids-pipeline**: la dipendenza upstream di Tesi_2.0. Produce il STC e le epochs che alimentano i moduli downstream. La scelta di non modificare mne-bids-pipeline e di aggiungere moduli separati garantisce compatibilità con aggiornamenti futuri.

---

## Riferimenti

- Discover-EEG: Crisol-Martínez et al. (2023). *Discover-EEG: an open, fully automated EEG pipeline for biomarker discovery in clinical neuroscience*. Scientific Data.
- MOABB: Jayaram & Barachant (2018). *MOABB: trustworthy algorithm benchmarking for BCIs*. Journal of Neural Engineering, 15(6).
- NeuroPycon: Meunier et al. (2020). *NeuroPycon: an open-source python toolbox for fast multi-thread MEG/EEG connectivity pipelines*. NeuroImage, 219.
- mne-bids-pipeline: Appelhoff et al. (2022). MNE-BIDS. *Journal of Open Source Software*, 5(44).

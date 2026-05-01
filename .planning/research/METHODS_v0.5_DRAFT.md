---
type: thesis-section
status: draft
section: methods
project: Tesi_2.0
last_review: 2026-05-01
sprint: S-13
tags: [eeg, source-fc, ml]
---
# Methods — v0.5 DRAFT (preprocessing + source reconstruction)

**Stato**: scaffold scientifico, sezione preprocessing + source recon basata su STEP 2 done sul dataset smoke `eeg_matchingpennies` (sub-05).
**Cross-ref**: integra/anticipa `.planning/research/METHODS_v1.md` (S-13 done) e `.planning/research/MAIN_v1.md` (S-15 done). Questo `v0.5_DRAFT` è un bridge focalizzato sui due step già eseguiti, NON sostituisce v1.
**Lingua**: italiano per testo, inglese per termini tecnici e nomi pacchetti.

---

## 1. Acquisizione dati e formato BIDS

Il dataset di sviluppo (`eeg_matchingpennies`, 7 soggetti, BrainVision EEG) è organizzato secondo la specifica Brain Imaging Data Structure (BIDS) per dati EEG. La pipeline `mne-bids-pipeline` (versione 1.10.1) consuma direttamente la struttura BIDS senza conversione intermedia: `bids_root` punta alla directory radice del dataset; ogni soggetto è isolato in `sub-XX/eeg/` e contiene tre file fondamentali (`*.eeg`, `*.vhdr`, `*.vmrk`) più i metadati BIDS (`channels.tsv`, `events.tsv`, sidecar JSON).

Per il restart Tesi_2.0 il dataset scientifico finale resta scelta operatore (Q1 in `.planning/QUESTIONS_FOR_OPERATOR.md`): le opzioni sono `ds005385` (Dortmund Vital Study, 200 soggetti, 21 GB) e `LEMON` (220 soggetti, 65 GB). Entrambi i dataset sono già scaricati in `~/Scrivania/Tesi/data/` e disponibili per integrazione via symlink.

## 2. Preprocessing (STEP 1, validato 2026-04-28)

Il preprocessing EEG segue lo schema standard di `mne-bids-pipeline` con tre passi attivi nella config `config/config_step1_matchingpennies.py`:

1. **Frequency filtering**: filtro passa-basso a 100 Hz (`h_freq = 100`, `l_freq = None`); rimozione del rumore di rete a 50 Hz tramite Zapline (`zapline_fline = 50`, `zapline_iter = False`). Zapline è preferito al notch filter classico perché preserva meglio il contenuto in banda larga rimuovendo solo le componenti sincrone alla frequenza di rete.
2. **Epoching**: finestre `-0.2 s` / `+0.5 s` rispetto a trigger `raised-left` / `raised-right` su matchingpennies. Per resting-state EC/EO (dataset finale) sarà necessario epoching artificiale a finestra fissa 2 s sliding senza overlap, costruito a valle della pipeline ufficiale (`source_reconstruction/apply_inverse_epochs_rs.py`).
3. **Peak-to-peak rejection**: soglia `150 µV` su tutti i canali EEG. Sui dati matchingpennies sub-05 nessuna epoch è stata rifiutata (0/100), confermando che il segnale post-filter è pulito.

Pipeline cache: `mne-bids-pipeline` usa `joblib.Memory` per memoizzare gli step. Re-run a config invariata sono istantanei. Output di STEP 1 in `data/derivatives/mne-bids-pipeline/sub-XX/eeg/`: `*_proc-filt_raw.fif` (raw filtrato), `*_epo.fif` (epochs), `*_proc-clean_epo.fif` (epochs post-reject), `*_bads.tsv`, `*_scores.json`, `*_report.html`.

ICA e SSP sono disponibili nella pipeline ma disabilitati per il dataset di sviluppo (10 canali EEG senza artefatti oculari evidenti). Per il dataset finale a 64 canali ICA verrà attivata con `mne-icalabel` per identificazione automatica delle componenti.

## 3. Source reconstruction (STEP 2, validato 2026-05-01)

### 3.1 Anatomia template

In assenza di MRI individuale per i soggetti (vincolo della scelta dataset matchingpennies + LEMON candidate per resting), si adotta l'anatomia template `fsaverage` (Free-Surfer). Il template `fsaverage` è già installato in `/home/seraxel/mne_data/MNE-fsaverage-data/fsaverage/` e include: BEM solution precalcolata (`fsaverage-5120-5120-5120-bem-sol.fif`), source space `oct-6` (`fsaverage-ico-5-src.fif`), trasformazione fiducial (`fsaverage-trans.fif`). Nessun calcolo BEM è quindi necessario: la pipeline salta automaticamente `_01_make_bem_surfaces` e `_02_make_bem_solution` quando `use_template_mri = "fsaverage"`.

La limitazione anatomica è ben documentata in letteratura: la localizzazione delle sorgenti su template introduce un errore dell'ordine di 1-2 cm rispetto a forward modelling individuale (Cuffin 1996, Fuchs et al. 2007). Per analisi a livello di parcel (STEP 3) questa imprecisione è in larga parte assorbita dall'aggregazione spaziale.

### 3.2 Forward model

La forward solution è calcolata da `mne-bids-pipeline` step `source/_04_make_forward` usando il source space `oct-6` (8196 sorgenti totali, 4098 per emisfero), il BEM solution `fsaverage-5120-5120-5120-bem-sol.fif`, e il template montage `standard_1020` applicato alle posizioni elettrodi prima del forward computation. La pipeline salva l'output in `sub-XX_fwd.fif` (~20 MB per soggetto).

### 3.3 Inverse operator e dSPM

L'inverse operator è calcolato da `mne.minimum_norm.make_inverse_operator` con i parametri standard MNE-Python:
- **Loose**: 0.2 (constraint moderato sull'orientamento delle sorgenti rispetto alla normale corticale, accettato il compromesso tra orientamento fisso e libero).
- **Depth weighting**: 0.8 (compensazione del bias superficiale tipico di MNE non-pesato).
- **Noise covariance**: matrice diagonale ad-hoc (`mne.make_ad_hoc_cov`), motivata dall'assenza di empty room recording per EEG e dalla baseline pre-trigger insufficiente per stima robusta.
- **Inverse method**: dSPM (dynamic statistical parametric mapping). Su matchingpennies dSPM produce mappe in unità di z-score, naturalmente normalizzate per il rumore.

L'inverse operator è salvato in `sub-XX_inv.fif` (~21 MB).

### 3.4 Source time courses

Per ogni evoked (3 condizioni: `raised-left`, `raised-right`, contrasto LR-RR), `mne.minimum_norm.apply_inverse` produce uno `SourceEstimate` (STC) di shape `(8196, 3501)` (sorgenti × timepoints alla frequenza di campionamento del raw, qui 5000 Hz × 0.7 s window = 3501 sample). Salvataggio in `sub-XX_task-XX_cond-*_inv-dSPM-{lh,rh}.stc`.

### 3.5 Nota tecnica: bypass rendering 3D

La pipeline `mne-bids-pipeline` 1.10.1 tenta di renderizzare il sensor alignment 3D nel report HTML al termine dello step `_04_make_forward`. In ambiente headless senza `xvfb` (caso del nostro server senza display), PyVista fallisce con `RuntimeError: Could not load any valid 3D backend`. La forward solution è comunque calcolata e salvata correttamente prima del fallimento; l'inverse operator è poi calcolato fuori pipeline tramite `source_reconstruction/finalize_inverse.py`, che usa solo API MNE pure (`make_inverse_operator`, `apply_inverse`) — esattamente le stesse che la pipeline avrebbe invocato. Questa decisione è documentata in `reports/STEP2_LOG.md` §4 e mantiene la pipeline come fonte unica di verità per preprocessing/sensor/forward, demandando solo l'ultimo step in modo agnostico.

Per il dataset finale, l'installazione di `xvfb` (`sudo apt install xvfb`) consentirà esecuzione end-to-end della pipeline ufficiale anche per la sezione inverse.

## 4. Validazione qualitativa (smoke test sub-05)

Il pipeline ha completato STEP 1 + STEP 2 sul soggetto sub-05 senza errori scientifici. La forward solution presenta condizionamento numerico accettabile (97-98% varianza spiegata dal solver inverse). I file STC sono leggibili tramite `mne.read_source_estimate` e mostrano shape e sample rate coerenti. La validazione quantitativa (statistica robusta) è rimandata al dataset scientifico finale (dopo Q1 risolto), perché matchingpennies con N=1 soggetto non ha potenza per inferenza.

---

## Sezioni successive (rimando)

- **Parcellation**: documentata in `reports/STEP3_PROPOSAL.md` (S-21) e implementata in `parcellation/extract_label_tc.py` (S-01 hardenato).
- **Connettività**: `connectivity/fc_dispatcher.py` con 7 metriche × 5 bande (S-02 + DR-REVIEW-fc-symmetrize fix).
- **Feature extraction**: `features/dispatcher.py` (S-03).
- **Machine learning**: `ml_training/ml_dispatcher.py` con 5 algoritmi + GroupKFold + permutation testing (S-04).
- **End-to-end smoke**: `pipeline_mne_bids/run_e2e_matchingpennies.py` (S-05) e benchmark matrix `run_bench_matrix.py` (S-08, 700 runs).

Per la sintesi completa vedere `.planning/research/METHODS_v1.md` (5000 parole) e `.planning/research/MAIN_v1.md` (manuscript skeleton).

---

*Doc bridge v0.5: focus su preprocessing + source reconstruction. Compatibile con METHODS_v1 e MAIN_v1.*

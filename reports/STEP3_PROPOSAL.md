# STEP 3 — Parcellazione atlastica (PROPOSTA TECNICA)

**Data**: 2026-05-01
**Stato**: PROPOSAL — in attesa di conferma operatore prima dell'esecuzione su dataset scientifico
**Scope**: da source time courses (STC) a label time courses (label_tc) per ROI atlastiche.
Nessun calcolo FC, nessun ML. Solo STEP 3 di parcellazione.

> Documento di pianificazione. NON contiene codice eseguibile. Fissa le scelte tecniche
> prima dell'esecuzione su dataset scientifico finale.

---

## 1. Obiettivo

STEP 3 trasforma gli STC prodotti da STEP 2 (source time courses a risoluzione di vertice
su spazio fsaverage) in time courses aggregati per regione di interesse (ROI) secondo un
atlante corticale. L'output e' un array `(n_labels, n_times)` per ogni condizione e soggetto,
che diventa l'input di STEP 4 (connettivita spettrale).

La scelta dell'atlante determina la granularita' spaziale della rete funzionale, il trade-off
segnale/rumore (SNR) e la comparabilita' con la letteratura. Per questo il SYNC S-21 richiede
una decisione esplicita dell'operatore prima di procedere (vedi §6).

Implementazione corrente: `parcellation/extract_label_tc.py`, funzione `extract_tc_from_files()`.
Riferimento tecnico: `[[070_THESIS/MNE_PROFESSOR_LINKS]]` (vault Obsidian, link prof 1-5).

---

## 2. Atlanti disponibili e confronto

Tutti gli atlanti elencati sono gia' presenti su spazio `fsaverage` nella directory
`/home/seraxel/mne_data/MNE-fsaverage-data/`. Nessun download richiesto.

| Atlas | Parametro | N ROI | Tipo | Network map | Note |
|-------|-----------|-------|------|-------------|------|
| Desikan-Killiany | `"aparc"` | 68 | anatomico | No | Classico, massima comparabilita' letteratura |
| Destrieux a2009s | `"destrieux"` | 148 | anatomico | No | Piu' granulare, stesso paradigma DK |
| Schaefer 2018 100 | `"schaefer100"` | 100 | funzionale | 7 networks | Moderno, allineato a resting-state FC |
| Schaefer 2018 200 | `"schaefer200"` | 200 | funzionale | 7 networks | Benchmark standard letteratura FC |
| Schaefer 2018 400 | `"schaefer400"` | 400 | funzionale | 7 networks | Alta risoluzione, alto costo computazionale |

### Pro/contro per source-level FC

**aparc (68 ROI)**
- Pro: massima copertura in letteratura EEG source, ROI semanticamente interpretabili,
  basso costo computazionale, allineato al vecchio repo Tesi/ (continuita').
- Contro: granularita' grossolana, nessun mapping network nativo.

**destrieux (148 ROI)**
- Pro: stesso paradigma anatomico di aparc ma piu' granulare, utile come sensitivity test.
- Contro: ROI piu' piccole = piu' vertices vuoti, SNR inferiore per vertici rari.

**schaefer100 (100 ROI)**
- Pro: network-aware (7 resting-state networks di Yeo), moderno, confrontabile con
  letteratura fMRI/EEG FC, dimensione simile ad aparc.
- Contro: ROI funzionali su fsaverage potrebbero non allinearsi ottimalmente con
  source space EEG (costruite su fMRI resting-state).

**schaefer200 (200 ROI)**
- Pro: gold standard de facto per studi FC multi-atlas su resting-state, benchmark S-08
  richiede questo livello di granularita'.
- Contro: matrice FC 200x200 = 19900 features upper-triangle per banda; con 5 bande e 7
  metriche il vettore features cresce rapidamente (>700k). Richiede selezione features o
  riduzione dimensionalita' in STEP 5.

**schaefer400 (400 ROI)**
- Pro: massima granularita'.
- Contro: FC matrix 400x400 = 79800 features per banda. Out of scope per baseline
  (raccomandazione: escludere da S-08, vedi D3).

---

## 3. Mode di aggregazione

La funzione `mne.extract_label_time_course` aggrega i time courses di tutti i vertici
di una ROI in un unico segnale scalare per time step.

| Mode | Formula | Quando usare | Limitazioni |
|------|---------|--------------|-------------|
| `mean` | media aritmetica | mai per FC source-level | ignora sign-flip dei dipoli |
| `mean_flip` | media con flip di segno per allineamento | **raccomandato per FC** | lieve smoothing |
| `pca_flip` | prima componente PCA + flip | sensitivity test | piu' lento, assumere stazionarieta' |
| `max` | massimo assoluto | peak detection | non rappresentativo della ROI |

**Raccomandazione**: `mean_flip` come default. Il flip di segno allinea i time courses
dei dipoli orientati in direzioni opposte all'interno di una ROI, riducendo la
cancellazione di segnale che altrimenti degraderebbe le metriche FC leakage-corrected
(wPLI, imcoh). Questa e' la scelta standard della letteratura MNE source-level FC.

---

## 4. Anatomia soggetto: fsaverage template

Per `eeg_matchingpennies` e per il dataset scientifico finale (se privo di MRI individuale),
si usa il template `fsaverage` di FreeSurfer fornito da MNE via `fetch_fsaverage()`.

Conseguenze:
- La localizzazione source ha un errore atteso di circa 1-2 cm rispetto all'anatomia
  individuale. Accettabile per studi di connettività funzionale di rete (non si cercano
  hotspot millimetrici).
- Tutti i soggetti condividono lo stesso spazio sorgente (fsaverage oct6, ~4098 sorgenti
  per emisfero). Questo semplifica il confronto inter-soggetto senza registrazione morfologica.
- Limitazione sub-corticale: gli atlanti sopra citati sono corticali-only. Strutture
  sub-corticali (amigdala, ippocampo, thalamo) sono escluse. Non critico per il task
  cognitivo corrente (matchingpennies, lateralizzazione motoria + decision-making corticale).

---

## 5. neuromaps: integrazione (sprint S-10, opzionale)

`neuromaps` (v0.0.5, gia' installato) permette di associare a ogni ROI atlastica valori
scalari da annotazioni cerebrali pre-calcolate: gradienti funzionali, microarchitettura
corticale, espansione evolutiva, myelinazione T1w/T2w.

**Workflow proposto** (sprint S-10, deps=[S-01]):
1. Fetch annotazione via `neuromaps.fetch_annotation(source=..., desc=...)`.
2. Parcellazione annotazione su same atlas via `neuromaps.parcellate`.
3. Output: vettore `(n_labels,)` per annotazione, allineato alle stesse label di label_tc.
4. Uso in analisi: correlazione tra BA del classificatore per ROI e valori neurobiologici
   (e.g. la ROI piu' discriminante e' ad alta myelinazione o in zona T1w/T2w elevato?).

**Classificazione**: nice-to-have, non critico per baseline S-01. Sprint S-10 non blocca
S-02..S-08. Raccomandazione: incluso come sprint parallelo opzionale post-S-01.

---

## 6. Decisioni richieste operatore

| # | Domanda | Opzioni | Raccomandazione |
|---|---------|---------|-----------------|
| D1 | Atlas primario per baseline | aparc vs schaefer100 | aparc primario + schaefer100 confronto (entrambi in S-01) |
| D2 | Mode aggregazione | mean_flip vs pca_flip | mean_flip primario; pca_flip come sensitivity test facoltativo |
| D3 | Includere schaefer400 nel benchmark S-08? | si / no | NO — out of scope baseline (costo features eccessivo) |
| D4 | neuromaps integration S-10: critical o nice-to-have? | critical / nice-to-have | nice-to-have; S-10 non blocca S-02..S-08 |

---

## 7. Rischi tecnici

| Rischio | Probabilita' | Impatto | Mitigazione |
|---------|-------------|---------|-------------|
| Vertices vuoti in ROI piccole (Schaefer 400, destrieux) | Media | Basso | `allow_empty=True` in `extract_label_time_course`; warning loggato |
| Label medial_wall / unknown includono vertices bianchi | Alta | Medio | filtro gia' implementato in `get_labels()` via `_EXCLUDE_KEYWORDS` |
| fsaverage oct6 vs Schaefer (diverso spacing sulla white surface) | Bassa | Basso | entrambi su stessa white surface fsaverage; compatibili |
| Sign ambiguity senza mean_flip (cancellazione segnale) | Alta se si usa mean | Alto | default mean_flip elimina il problema |
| NaN in label_tc (ROI con source space vuoto) | Bassa | Alto | asserzione in test: `assert not np.isnan(tc).any()` |

---

## 8. Criteri di accettazione (gate S-01)

Sprint S-01 (hardening parcellation) si considera chiuso quando:

- `pytest tests/test_parcellation.py -v` ritorna 4/4 PASS.
- Test coprono: aparc, destrieux, schaefer100, schaefer200 su STC reale sub-05.
- Shape output verificata: `tc.shape == (n_labels_atlas, n_times_stc)` per ogni atlas.
- Zero NaN in output: `assert not np.isnan(tc).any()`.
- Filtraggio label verifica: medial_wall e unknown assenti da `names`.
- `extract_tc_from_files` accetta sia path fwd che path src (fix F4 deep review).

---

## 9. Cosa STEP 3 NON fa

- NO calcolo FC (e' STEP 4, sprint S-02).
- NO feature extraction ML (e' STEP 5, sprint S-03).
- NO classificazione (e' STEP 6, sprint S-04).
- NO dataset scientifico finale — STEP 3 si valida su matchingpennies sub-05, poi si
  esegue su dataset finale quando Q1 (dataset choice) e' risolta.
- NO sub-cortical parcellation (fuori scope per gli atlanti selezionati).

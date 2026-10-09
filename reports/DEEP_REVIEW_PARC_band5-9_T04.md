# Deep Review Parcellation — Edge Cases (BAND-5-9-T04)

**Sprint**: BAND-5-9-T04  
**Data**: 2026-05-01  
**Owner**: sonnet2-ts  
**Pre-condizione**: S-01 done  

---

## Metodologia

Sweep: **4 atlas × 4 mode × 4 edge scenarios + input validation cases**.

| Parametro | Valori |
|-----------|--------|
| atlas | aparc (68 ROI), destrieux (148), schaefer100 (100), schaefer200 (200) |
| mode | mean, mean_flip, pca_flip, max |
| edge scenarios | n_times=1, zero data, label vuota, wrong subject |
| dati | STC reale sub-05 matchingpennies (n_verts=8196, n_times=3501) |

---

## Matrice Outcome: atlas × mode (normale)

| Atlas | mean | mean_flip | pca_flip | max |
|-------|------|-----------|----------|-----|
| aparc | **PASS** | **PASS** | **PASS** | **PASS** |
| destrieux | **PASS** | **PASS** | **PASS** | **PASS** |
| schaefer100 | **PASS** | **PASS** | **PASS** | **PASS** |
| schaefer200 | **PASS** | **PASS** | **PASS** | **PASS** |

Shape output corretta, valori finiti, nessun NaN. 16/16 combo PASS.

---

## Matrice Outcome: edge scenarios × mode

### n_times=1 (STC con singolo time point)

| Atlas | mean | mean_flip | pca_flip | max |
|-------|------|-----------|----------|-----|
| aparc | **PASS** | **PASS** | **PASS** | **PASS** |
| destrieux | **PASS** | **PASS** | **PASS** | **PASS** |
| schaefer100 | **PASS** | **PASS** | **PASS** | **PASS** |
| schaefer200 | **PASS** | **PASS** | **PASS** | **PASS** |

**Nota pca_flip**: con n_times=1 la PCA non ha senso statistico, ma MNE non crasha.
Output shape (n_rois, 1) finita per tutti. Nessun warning aggiuntivo.

### Zero data STC (tutti i valori = 0)

| Mode | Outcome | Dettaglio |
|------|---------|-----------|
| mean | **PASS** | all-zero output, finito |
| mean_flip | **PASS** | all-zero output, finito |
| pca_flip | **PASS** | all-zero output, finito (0 * sign = 0) |
| max | **PASS** | all-zero output, finito |

Nessun NaN da 0/0. MNE gestisce il caso correttamente.

### Label vuota (0 vertici, allow_empty=True)

| Scenario | Outcome | Dettaglio |
|----------|---------|-----------|
| Label iniettata con 0 vertici | **WARN** | RuntimeWarning da MNE, riga output = 0 |

`mne.extract_label_time_course(allow_empty=True)` emette 1 RuntimeWarning per label vuota
e restituisce una riga di zeri. Comportamento corretto e documentato in MNE.

**Note**: `extract_label_tc.py` usa già `allow_empty=True`. Le label medial_wall/unknown
vengono filtrate a monte da `get_labels()`, quindi questo scenario si verifica solo se
l'utente inietta manualmente label vuote.

### Wrong subject (get_labels con subject non esistente)

| Scenario | Outcome | Dettaglio |
|----------|---------|-----------|
| `get_labels("aparc", subject="sub-NONEXISTENT-999")` | **FAIL** (atteso) | `OSError`: directory annotation non trovata |

Errore **informativo e atteso**: MNE non trova le annotazioni per un subject non esistente.
Non è un bug di `extract_label_tc.py` — è il comportamento corretto.

---

## Input validation (extract_tc_from_files)

| Test | Outcome |
|------|---------|
| Nessuna sorgente (no fwd_path, no src_path) | **PASS** — `ValueError: "esattamente uno"` |
| Entrambe le sorgenti | **PASS** — `ValueError: "mutuamente esclusivi"` |

---

## Sommario outcomi

| Scenario | n_combos | PASS | WARN | FAIL |
|----------|----------|------|------|------|
| atlas × mode normale | 16 | 16 | 0 | 0 |
| n_times=1 × atlas × mode | 16 | 16 | 0 | 0 |
| zero data × mode | 4 | 4 | 0 | 0 |
| empty label | 1 | 0 | 1 | 0 |
| wrong subject (atteso) | 1 | 0 | 0 | 1 (expected) |
| input validation | 2 | 2 | 0 | 0 |
| **Totale** | **40** | **38** | **1** | **1** |

> Il FAIL "wrong subject" è **atteso e corretto** (OSError informativo). Nessun FAIL non atteso.

---

## Conclusione priorita' fix

| Finding | Severity | Azione |
|---------|----------|--------|
| Label vuota → RuntimeWarning + zeros | INFO | Comportamento MNE by design; `allow_empty=True` gia' impostato |
| pca_flip + n_times=1 silente | INFO | Produce output valido (anche se statisticamente privo di senso) |
| wrong subject → OSError | INFO | Errore informativo; nessun fix necessario |

**Nessun fix urgente** in `extract_label_tc.py`. Il codice gestisce correttamente
tutti gli scenari testati.

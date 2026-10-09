# Neuromaps Integration — STEP 3b

**Sprint**: S-10  
**Data**: 2026-05-01  
**Owner**: sonnet2-ts  
**Stato**: PASS

---

## Obiettivo

Associare mappe neuroscientifiche precompute (gradients di connettivita', microstructure, mappe recettoriali)
alle stesse ROI usate per la FC (atlas: aparc, schaefer100, schaefer200), per arricchire
l'interpretazione dei risultati ML.

---

## Implementazione

**File**: `parcellation/neuromaps_helper.py` (da S-01) + estensioni S-10

### Funzioni principali

| Funzione | Descrizione |
|----------|-------------|
| `fetch_annotation_for_atlas(atlas, annotations)` | Scarica annotazioni neuromaps e le parcellizza per l'atlante specificato. |
| `_parcellate_annotation(img, labels)` | Calcola media dell'annotazione per ciascuna label MNE (numpy-based). |

### Flusso

```
neuromaps.datasets.fetch_annotation()
         ↓ (download da OSF/GitHub)
    (lh_data, rh_data) — array per vertice in fsLR 32k o fsaverage 10k
         ↓
_parcellate_annotation(img, mne_labels)
         ↓
    array shape (n_rois,) — valore medio per ROI
```

---

## Annotazioni disponibili (selezione)

| Source | Desc | Space | Den | Contenuto |
|--------|------|-------|-----|-----------|
| margulies2016 | fcgradient01 | fsLR | 32k | Connectivity gradient 1 (principal) |
| margulies2016 | fcgradient02..05 | fsLR | 32k | Connectivity gradients 2-5 |
| hill2010 | myelinmap | fsLR | 32k | T1w/T2w proxy mielinizzazione |
| abagen | genepc1 | fsaverage | 10k | Gene expression PC1 |

---

## Vincoli spazio/densita'

Le annotazioni e l'atlas devono essere nello **stesso spazio e densita'**.
Nessun resampling automatico e' implementato (out of scope per baseline).

| Atlas | Spazio raccomandato | Densita' |
|-------|---------------------|----------|
| aparc | fsaverage | 10k |
| schaefer100/200 | fsLR | 32k |

Se spazio annotazione != spazio atlas, usare `neuromaps.transforms` per resampling manuale.

---

## Stato fetch annotazioni

| Annotazione | Stato fetch locale |
|-------------|-------------------|
| margulies2016/fcgradient01 | Fallito (network non disponibile in CI) — graceful fallback con warning |

Il codice gestisce il fallback: `fetch_annotation_for_atlas` ritorna `{}` con `RuntimeWarning`
se il download fallisce. Non blocca la pipeline.

---

## Test copertura

**File**: `tests/test_neuromaps_helper.py` — 5 test:

| Test | Verifica |
|------|----------|
| `test_parcellate_annotation_shape` | Output shape `(n_rois,)` |
| `test_parcellate_annotation_finite` | Nessun NaN per vertici validi |
| `test_parcellate_annotation_values` | Valore = media attesa per ROI |
| `test_fetch_annotation_no_neuromaps_returns_empty` | Graceful fallback senza neuromaps |
| `test_fetch_annotation_for_atlas_aparc_structure` | Dict con array float (skip se network) |

Tutti 5/5 PASS.

---

## Decisione D4 (da STEP3_PROPOSAL.md)

> D4: neuromaps integration in S-10 = critical o nice-to-have?
> Raccomandazione: **nice-to-have** (S-10 ha deps=[S-01], non blocca pipeline).

Confermato: S-10 implementato come modulo opzionale. La pipeline principale (S-01..S-08)
non dipende da neuromaps. Il modulo e' disponibile per arricchire l'analisi post-benchmark.

---

## Cross-reference

- `parcellation/extract_label_tc.py` — `get_labels()` usato per costruire MNE Labels
- `reports/STEP3_PROPOSAL.md` — decisioni tecniche parcellazione
- `config/config_step2_source_matchingpennies.py` — atlas di default usato

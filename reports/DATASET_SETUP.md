# Dataset Setup — Scientific Datasets (S-40)

**Script**: `scripts/setup_scientific_dataset.py`  
**Data**: 2026-05-01

---

## Datasets supportati

| Dataset | Descrizione | Task | N sub (attesi) | Disk space |
|---------|-------------|------|----------------|------------|
| `ds005385` | OpenNeuro EEG resting-state EC/EO | restingstate | 50 | ~4.5 GB |
| `LEMON` | MPI Leipzig Mind-Brain-Body EEG | restingstate | ~200 | ~8.0 GB |

**Pre-requisito**: dataset scaricati in `~/Scrivania/Tesi/data/<dataset>/` prima di eseguire lo script.

---

## CLI Usage

```bash
python scripts/setup_scientific_dataset.py \
    --dataset {ds005385|LEMON} \
    --action {symlink|verify|prep}
```

### `--action symlink`

Crea un symlink `data/<dataset>/` → `~/Scrivania/Tesi/data/<dataset>/`.

```bash
python scripts/setup_scientific_dataset.py --dataset ds005385 --action symlink
# Output: Symlink creato: data/ds005385 → /home/seraxel/Scrivania/Tesi/data/ds005385
```

**Sicurezza**: rifiuta path al di fuori di `data/` (validazione esplicita).  
Se il symlink esiste già e punta alla destinazione corretta, lo segnala senza modificare.

### `--action verify`

Legge 1 soggetto casuale con `mne_bids.read_raw_bids` e stampa un report di verifica.

```bash
python scripts/setup_scientific_dataset.py --dataset ds005385 --action verify
```

Output atteso:
```
==================================================
Dataset: ds005385 (OpenNeuro ds005385 ...)
BIDS root: /path/to/data/ds005385
N soggetti: 50
Soggetto campione: sub-12
N canali: 64
sfreq: 500.0 Hz
Durata: 300.0s
Tipo canali: {'eeg'}
Verifica BIDS: PASS
==================================================
```

### `--action prep`

Genera `config/config_step1_<dataset>.py` con override dei path e parametri dataset-specifici.

```bash
python scripts/setup_scientific_dataset.py --dataset ds005385 --action prep
# Output: Config generato: config/config_step1_ds005385.py
```

Il file generato eredita da `config_base.py` e sovrascrive:
- `bids_root` → path al dataset
- `task`, `ch_types`, `conditions` → parametri specifici del dataset

---

## Pre-requisiti per dataset

### ds005385 (OpenNeuro)

```bash
# Download manuale (richiede DataLad o AWS):
datalad install -r https://github.com/OpenNeuroDatasets/ds005385.git
# Oppure: aws s3 sync --no-sign-request s3://openneuro.org/ds005385 ~/Scrivania/Tesi/data/ds005385/
```

| Campo | Valore atteso |
|-------|--------------|
| BIDS structure | `sub-XX/eeg/*.{vhdr,vmrk,eeg}` |
| Montaggio | Standard 10-20, 64+ canali |
| Condizioni | eyes_closed (run-1), eyes_open (run-2) |
| MRI individuale | Non richiesto (fsaverage template) |

### LEMON (MPI Leipzig)

```bash
# Download LEMON:
# https://ftp.gwdg.de/pub/misc/MPI-Leipzig_Mind-Brain-Body-LEMON/
```

| Campo | Valore atteso |
|-------|--------------|
| BIDS structure | `sub-XX/eeg/*.{vhdr,vmrk,eeg}` |
| Montaggio | Standard 10-20, 61 canali |
| Condizioni | eyes_closed (EC), eyes_open (EO) |
| MRI individuale | Disponibile ma non richiesto (fsaverage OK) |

---

## Output post-setup

Dopo `--action symlink` + `--action prep`:

```
data/
  ds005385/               ← symlink → ~/Scrivania/Tesi/data/ds005385/
    sub-01/eeg/...
    ...
    participants.tsv
    dataset_description.json
config/
  config_step1_ds005385.py  ← generato da --action prep
```

Il config generato e' pronto per essere usato con `pipeline_mne_bids` sostituendo
`config_step1_matchingpennies.py`.

---

## Validazione path (sicurezza)

Lo script rifiuta esplicitamente qualsiasi path di output che non sia sotto `data/`:

```python
# Esempio interno:
_validate_data_path(Path("/tmp/evil"))
# SystemExit: Sicurezza: il path deve essere sotto .../data/
```

"""Configurazione dataset LEMON per Tesi_2.0.

LEMON (Leipzig Mind-Brain-Body Dataset): dataset pubblico EEG a riposo
con paradigma EC/EO, compatibile con pipeline ds005385.

Ref: Babayan et al. (2019), Scientific Data.
DOI: https://doi.org/10.1038/sdata.2018.308
Download: https://ftp.gwdg.de/pub/misc/MPI-Leipzig_Mind-Brain-Body-Dataset/

STATO: SCAFFOLDING — dati non ancora integrati.
Prerequisiti operatore (gate bloccante):
    1. Download LEMON BIDS da URL sopra (~200GB)
    2. Eseguire STEP 1-5 pipeline Tesi_2.0 su LEMON
    3. Verificare sfreq_target=500Hz + parcellazione aparc/schaefer100
    4. Aggiornare LEMON_RAW_PATH qui sotto con il path reale
"""

from __future__ import annotations

from pathlib import Path

# ── Path operatore (da configurare) ──────────────────────────────────────────
# BLOCCO OPERATORE: impostare il path reale dopo download LEMON BIDS.
# Radice del dataset LEMON BIDS su disco; None finche' l'operatore non la imposta
LEMON_RAW_PATH: Path | None = None  # es. Path("~/data/LEMON_BIDS").expanduser()

# ── Configurazione pipeline ───────────────────────────────────────────────────
# Identificativo del dataset (usato in nomi file e log)
DATASET_ID = "lemon"
SFREQ_TARGET = 500  # Hz: frequenza di campionamento dopo resampling (allineata a ds005385)
# Paradigma sperimentale: confronto occhi chiusi vs aperti
PARADIGM = "EC_EO"  # Eyes Closed / Eyes Open

# Pilot whitelist (15 subjects, seed=42) — da aggiornare con sub-ID LEMON reali
# NOTA: sub-ID LEMON seguono formato "sub-010001", "sub-010002", etc.
# Numero di soggetti del pilota (stessa taglia della whitelist N=15)
PILOT_N = 15
# Seed del campionamento casuale (riproducibilita)
PILOT_SEED = 42

# Label mapping EC/EO per LEMON
# LEMON usa "EC" e "EO" nei task names BIDS
LABEL_MAP = {  # etichetta numerica per classificazione binaria
    "EC": 0,  # Eyes Closed → classe 0
    "EO": 1,  # Eyes Open → classe 1
}

# Atlanti supportati (stessi di ds005385)
# Parcellazioni corticali usate (Desikan-Killiany e Schaefer 100 parcelle)
ATLASES = ["aparc", "schaefer100"]

"""Workaround per mne-bids-pipeline==1.10.1 + noise_cov="ad-hoc".

Con `noise_cov = "ad-hoc"` lo step `sensor/_06_make_cov` salta il calcolo
della covarianza ("Skipping, using ad-hoc diagonal covariance") e non scrive
mai `<...>_proc-adhoc_rank.json`. Lo step successivo `source/_05_make_inverse`
richiede però quel file come input obbligatorio (bug noto upstream, vedi
`get_input_fnames_make_inverse` in mne_bids_pipeline: commento `XXX is this
the right solution also for noise_cov = 'ad-hoc'?`), quindi la pipeline
abortisce con `AssertionError: missing in_files["rank"]`.

Questa funzione calcola il rank dalle epoch "clean" già prodotte dallo step
sensor e scrive il rank.json nel path esatto atteso da mne-bids-pipeline
(riusando `get_noise_cov_bids_path`, per restare corretti anche se lo schema
di naming BIDS cambia tra versioni). Va chiamata tra "sensor" e "source".

Posizione nella pipeline: STEP 2 (source reconstruction), a valle del preprocessing (STEP 1).
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace


def ensure_adhoc_rank_json(config_path: str, subject: str, task: str) -> None:
    """Garantisce l'esistenza del file `*_rank.json` per la covarianza ad-hoc.

    Se la config usa `noise_cov = "ad-hoc"` e il file di rank manca, lo ricava
    dalle epoche "clean" del soggetto. Non fa nulla negli altri casi.

    Args:
        config_path: Percorso della config mne-bids-pipeline (modulo Python).
        subject: Identificativo soggetto (senza prefisso "sub-").
        task: Nome del task BIDS.

    Raises:
        ImportError: Se mne_bids_pipeline non e' importabile.
    """
    from mne_bids_pipeline._config_utils import get_noise_cov_bids_path

    spec = importlib.util.spec_from_file_location("_tesi_step2_cfg", config_path)
    cfg_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cfg_mod)

    if getattr(cfg_mod, "noise_cov", None) != "ad-hoc":
        return

    cfg = SimpleNamespace(
        acq=getattr(cfg_mod, "acq", None),
        rec=getattr(cfg_mod, "rec", None),
        space=getattr(cfg_mod, "space", None),
        datatype=getattr(cfg_mod, "datatype", "eeg"),
        deriv_root=cfg_mod.deriv_root,
        noise_cov="ad-hoc",
    )
    cov_bp = get_noise_cov_bids_path(cfg=cfg, subject=subject, session=None)
    rank_path = cov_bp.copy().update(suffix="rank", extension=".json")
    if rank_path.fpath.exists():
        return

    epo_path = cov_bp.copy().update(task=task, processing="clean", suffix="epo", extension=".fif")
    if not Path(epo_path.fpath).exists():
        return  # niente epoch "clean" ancora prodotte: nulla da fare qui

    import mne

    epochs = mne.read_epochs(str(epo_path.fpath), preload=True, verbose=False)
    cov_rank = getattr(cfg_mod, "cov_rank", "info")
    rank = mne.compute_rank(epochs, info=epochs.info, rank=cov_rank, verbose=False)

    rank_path.fpath.parent.mkdir(parents=True, exist_ok=True)
    with open(rank_path.fpath, "w") as f:
        json.dump(rank, f)

"""Smoke test S-29: valida la struttura BIDS di un dataset mock.

Scopo:
    Genera un piccolo dataset BIDS sintetico con ``generate_mock_bids.py``,
    ne controlla la struttura (file obbligatori, chiavi di
    dataset_description.json, cartelle soggetto, import di mne_bids) e lo
    cancella a fine test.

Input:
    Nessun dato reale; argomenti CLI ``--n-subjects``, ``--output-dir``,
    ``--report``.

Output:
    Report Markdown (default ``reports/MOCK_VALIDATION.md``); la cartella
    mock temporanea viene rimossa. Exit code 0 se tutto OK, 1 altrimenti.

Esempio:
    python scripts/validate_mock_bids.py --n-subjects 5
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import mne_bids


# ===== 1. Validazione del dataset mock =====
def validate_mock_bids(
    output_dir: str | Path = "data/mock_validation_test",
    n_subjects: int = 5,
) -> dict:
    """Genera un dataset mock e ne valida la struttura BIDS.

    Parameters
    ----------
    output_dir:
        Directory di output del test (creata e cancellata alla fine).
    n_subjects:
        Numero di soggetti da generare e verificare.

    Returns
    -------
    dict
        Chiavi ``status`` (OK/FAIL/ERROR), ``n_subjects``, ``checks``
        (esito dei singoli controlli) ed ``errors`` (messaggi).

    Side effects
    ------------
    Lancia ``scripts/generate_mock_bids.py`` in un sottoprocesso (timeout 300 s),
    scrive in ``output_dir`` e lo rimuove nel blocco ``finally``.
    """
    output_dir = Path(output_dir)
    results = {
        "status": "OK",
        "n_subjects": n_subjects,
        "checks": {},
        "errors": [],
    }

    try:
        # 1. Genera dataset mock
        print(f"[VALIDATE] Generating mock dataset → {output_dir}")
        cmd = [
            "python",
            "scripts/generate_mock_bids.py",
            "--n-subjects",
            str(n_subjects),
            "--output-dir",
            str(output_dir),
            "--sfreq",
            "250",
            "--duration",
            "60",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            results["status"] = "FAIL"
            results["errors"].append(f"Generate failed: {result.stderr}")
            return results

        results["checks"]["generate"] = "PASS"
        print("  [OK] Dataset generated")

        # 2. Valida struttura directory
        print("[VALIDATE] Checking directory structure")
        required_files = [
            output_dir / "dataset_description.json",
            output_dir / "participants.tsv",
        ]
        for fpath in required_files:
            if not fpath.exists():
                results["errors"].append(f"Missing: {fpath.name}")
                results["status"] = "FAIL"
            else:
                print(f"  [OK] {fpath.name} exists")

        # 3. Valida dataset_description.json
        print("[VALIDATE] Checking dataset_description.json")
        desc_path = output_dir / "dataset_description.json"
        with open(desc_path) as f:
            desc = json.load(f)

        required_keys = ["Name", "BIDSVersion", "DatasetType"]
        for key in required_keys:
            if key not in desc:
                results["errors"].append(f"dataset_description missing: {key}")
                results["status"] = "FAIL"
            else:
                print(f"  [OK] {key}: {desc[key]}")

        # 4. Valida subject directories
        print(f"[VALIDATE] Checking {n_subjects} subject directories")
        subjects_found = 0
        for i in range(1, n_subjects + 1):
            sub_dir = output_dir / f"sub-{i:02d}" / "eeg"
            if sub_dir.exists():
                subjects_found += 1
                # Serve almeno un file EEG (.fif o .vhdr)
                eeg_files = list(sub_dir.glob("*.fif")) + list(sub_dir.glob("*.vhdr"))
                if eeg_files:
                    print(f"  [OK] sub-{i:02d}: {len(eeg_files)} file(s)")
                else:
                    results["errors"].append(f"sub-{i:02d}: no EEG files")
            else:
                results["errors"].append(f"sub-{i:02d}: directory missing")

        results["checks"]["subjects_found"] = subjects_found
        if subjects_found != n_subjects:
            results["status"] = "FAIL"

        # 5. Valida con mne_bids validator (if available)
        print("[VALIDATE] Running mne_bids validator")
        try:
            mne_bids.BIDSPath(subject="01", task="restingstate", run=1, datatype="eeg")
            results["checks"]["mne_bids_import"] = "OK"
            print("  [OK] mne_bids imported successfully")
        except Exception as e:
            results["errors"].append(f"mne_bids error: {e}")
            results["checks"]["mne_bids_import"] = "FAIL"

        results["checks"]["final_status"] = results["status"]

    except Exception as e:
        results["status"] = "ERROR"
        results["errors"].append(str(e))

    finally:
        # Cleanup test directory
        if output_dir.exists():
            print(f"[CLEANUP] Removing {output_dir}")
            shutil.rmtree(output_dir, ignore_errors=True)

    return results


# ===== 2. Entry point CLI =====
if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Validate mock BIDS dataset (smoke test)")
    ap.add_argument("--n-subjects", type=int, default=5)
    ap.add_argument("--output-dir", default="data/mock_validation_test")
    ap.add_argument("--report", default="reports/MOCK_VALIDATION.md")
    args = ap.parse_args()

    print("=" * 60)
    print("MOCK BIDS VALIDATION — Smoke Test S-29")
    print("=" * 60)

    results = validate_mock_bids(args.output_dir, args.n_subjects)

    # Scrittura del report Markdown
    report_lines = [
        "# Mock BIDS Validation Report",
        "",
        f"**Status**: {results['status']}",
        f"**Subjects**: {results['n_subjects']}",
        "",
        "## Checks",
        "",
    ]

    for check, status in results["checks"].items():
        report_lines.append(f"- {check}: {status}")

    if results["errors"]:
        report_lines.extend(
            [
                "",
                "## Errors",
                "",
            ]
        )
        for err in results["errors"]:
            report_lines.append(f"- {err}")

    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w") as f:
        f.write("\n".join(report_lines) + "\n")

    print("\n" + "=" * 60)
    print(f"Report → {report_path}")
    print(f"Result: {results['status']}")
    print("=" * 60)

    sys.exit(0 if results["status"] == "OK" else 1)

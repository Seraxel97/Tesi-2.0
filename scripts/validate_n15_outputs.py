"""Validate N15 — Data integrity validation for N=15 ds005385 outputs.

Validates label_tc per-epoch, FC matrices, and feature matrices produced by
the S-FULL-N15 pipeline run. Read-only — no pipeline execution, no data modification.

Scopo:
    Controllo di integrita' dei dati prodotti dalla pipeline sui 15 soggetti
    della whitelist: forma degli array, assenza di NaN/Inf, simmetria e range
    fisiologico delle matrici di connettivita'.

Input:
    ``data/label_ts/ds005385`` (60 file), ``data/connectivity/ds005385``
    (120 file) e ``data/features/ds005385`` (4 matrici X + y.npy + groups.npy).

Output:
    Report Markdown (default ``reports/VALIDATE_N15.md``) e riepilogo su stdout.

Usage
-----
    python scripts/validate_n15_outputs.py
    python scripts/validate_n15_outputs.py --data-root /path/to/Tesi_2.0 --output reports/VALIDATE_N15.md

Exit codes: 0=PASS, 1=WARN (anomalies present but not critical), 2=FAIL
"""

from __future__ import annotations

import argparse
import datetime
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

# ===== 1. Configurazione =====
# Soggetti attesi (whitelist N=15, seed 42)
SUBJECTS = [
    "sub-007",
    "sub-010",
    "sub-011",
    "sub-026",
    "sub-031",
    "sub-033",
    "sub-041",
    "sub-066",
    "sub-071",
    "sub-080",
    "sub-125",
    "sub-157",
    "sub-169",
    "sub-185",
    "sub-195",
]
ATLASES = ["aparc", "schaefer100"]  # parcellazioni corticali
CONDITIONS = ["EO", "EC"]  # occhi aperti / occhi chiusi
METRICS = ["wpli", "coh"]  # metriche di connettivita' spettrale

_ATLAS_N_LABELS = {"aparc": 68, "schaefer100": 100}  # ROI per atlante
_N_TIMES_EXPECTED = 501  # campioni temporali per epoca nei label_tc
_N_EPOCHS_MIN, _N_EPOCHS_MAX = 80, 200  # intervallo plausibile di epoche per file
_N_SUBJECTS = 15
_N_SAMPLES_EXPECTED = _N_SUBJECTS * 2  # 30 (un campione EO e uno EC per soggetto)
# Numero di feature = archi del triangolo superiore, n*(n-1)/2 (68 -> 2278; 100 -> 4950)
_FEAT_N_LABELS = {"aparc": 2278, "schaefer100": 4950}

_WPLI_OFFDIAG_MED_MIN = 0.0  # wPLI can be 0 on diagonal; off-diag median > 0
_WPLI_OFFDIAG_MAX_ABS = 1.0
_COH_MIN, _COH_MAX = 0.0, 1.0
_LABEL_TC_MAX_ABS = 1e6


# ===== 2. Strutture dati =====
@dataclass
class Anomaly:
    """Singola anomalia rilevata.

    Attributes:
        category: tipo di dato (``label_tc``, ``FC``, ``features``).
        file: nome del file coinvolto.
        field: controllo fallito (es. ``shape``, ``finite``).
        value: dettaglio del valore anomalo.
    """

    category: str
    file: str
    field: str
    value: str


@dataclass
class SubjectStats:
    """Statistiche off-diagonal di wPLI e coerenza per un soggetto (EO/EC).

    Attributes:
        subject: ID soggetto.
        atlas: atlante a cui si riferiscono le statistiche.
        wpli_*_median / wpli_*_max: mediana e massimo assoluto di wPLI.
        coh_*_median: mediana della coerenza.
    """

    subject: str
    atlas: str = ""
    wpli_eo_median: float = float("nan")
    wpli_ec_median: float = float("nan")
    wpli_eo_max: float = float("nan")
    wpli_ec_max: float = float("nan")
    coh_eo_median: float = float("nan")
    coh_ec_median: float = float("nan")


@dataclass
class ValidationReport:
    """Contatori e anomalie della validazione.

    Per ciascuna categoria (label_tc ``lt``, FC ``fc``, feature ``feat``) tiene
    il numero di file attesi, trovati, validi e le anomalie; ``anomalies`` e
    ``subject_stats`` raccolgono il dettaglio per il report.
    """

    timestamp: str
    lt_expected: int = 60
    lt_found: int = 0
    lt_valid: int = 0
    lt_anomalies: int = 0
    fc_expected: int = 120
    fc_found: int = 0
    fc_valid: int = 0
    fc_anomalies: int = 0
    feat_expected: int = 4
    feat_found: int = 0
    feat_valid: int = 0
    feat_anomalies: int = 0
    anomalies: list[Anomaly] = field(default_factory=list)
    subject_stats: list[SubjectStats] = field(default_factory=list)

    @property
    def verdict(self) -> str:
        """Verdetto complessivo: FAIL (file mancanti o feature anomale), WARN o PASS."""
        total_anom = self.lt_anomalies + self.fc_anomalies + self.feat_anomalies
        missing = (
            (self.lt_expected - self.lt_found)
            + (self.fc_expected - self.fc_found)
            + (self.feat_expected - self.feat_found)
        )
        if missing > 0 or self.feat_anomalies > 0:
            return "FAIL"
        if total_anom > 0:
            return "WARN"
        return "PASS"


# ===== 3. Validatori =====
def _validate_label_tc(lt_dir: Path, report: ValidationReport) -> None:
    """Valida i file label_tc per-epoch (15 soggetti x 2 atlanti x 2 condizioni).

    Controlla forma (epoche, ROI, tempi), numero di epoche plausibile, assenza
    di NaN/Inf e ampiezza massima.

    Args:
        lt_dir: cartella dei file ``*_per-epoch.npz``.
        report: report aggiornato in-place (contatori e anomalie).
    """
    for sub in SUBJECTS:
        for atlas in ATLASES:
            for cond in CONDITIONS:
                fname = f"{sub}_atlas-{atlas}_cond-{cond}_per-epoch.npz"
                fpath = lt_dir / fname
                if not fpath.exists():
                    report.lt_anomalies += 1
                    report.anomalies.append(Anomaly("label_tc", fname, "exists", "MISSING"))
                    continue
                report.lt_found += 1
                try:
                    d = np.load(fpath, allow_pickle=False)
                    lt = d["label_tc"]
                except Exception as e:
                    report.lt_anomalies += 1
                    report.anomalies.append(Anomaly("label_tc", fname, "load", str(e)[:80]))
                    continue

                ok = True
                n_epochs, n_labels, n_times = lt.shape

                if n_labels != _ATLAS_N_LABELS[atlas]:
                    report.anomalies.append(
                        Anomaly(
                            "label_tc", fname, "n_labels", f"{n_labels} != {_ATLAS_N_LABELS[atlas]}"
                        )
                    )
                    ok = False

                if n_times != _N_TIMES_EXPECTED:
                    report.anomalies.append(
                        Anomaly("label_tc", fname, "n_times", f"{n_times} != {_N_TIMES_EXPECTED}")
                    )
                    ok = False

                if not (_N_EPOCHS_MIN <= n_epochs <= _N_EPOCHS_MAX):
                    report.anomalies.append(
                        Anomaly(
                            "label_tc",
                            fname,
                            "n_epochs",
                            f"{n_epochs} out of [{_N_EPOCHS_MIN}, {_N_EPOCHS_MAX}]",
                        )
                    )
                    ok = False

                if not np.isfinite(lt).all():
                    n_bad = int(np.sum(~np.isfinite(lt)))
                    report.anomalies.append(
                        Anomaly("label_tc", fname, "finite", f"{n_bad} NaN/Inf")
                    )
                    ok = False

                max_abs = float(np.abs(lt).max())
                if max_abs > _LABEL_TC_MAX_ABS:
                    report.anomalies.append(
                        Anomaly(
                            "label_tc", fname, "max_abs", f"{max_abs:.3e} > {_LABEL_TC_MAX_ABS:.0e}"
                        )
                    )
                    ok = False

                if ok:
                    report.lt_valid += 1
                else:
                    report.lt_anomalies += 1


def _validate_fc(fc_dir: Path, report: ValidationReport) -> None:
    """Valida le matrici FC per-epoch (120 attese: 15x2x2x2).

    Controlla forma, finitezza, simmetria e range (wPLI in [0,1] in modulo,
    coerenza in [0,1]) sugli elementi fuori diagonale; raccoglie le statistiche
    per (soggetto, atlante).

    Args:
        fc_dir: cartella dei file FC.
        report: report aggiornato in-place.
    """
    stats_map: dict[tuple[str, str], SubjectStats] = {
        (s, a): SubjectStats(subject=s, atlas=a) for s in SUBJECTS for a in ATLASES
    }

    for sub in SUBJECTS:
        for atlas in ATLASES:
            n_labels = _ATLAS_N_LABELS[atlas]
            for cond in CONDITIONS:
                for metric in METRICS:
                    fname = (
                        f"{sub}_atlas-{atlas}_cond-{cond}_metric-{metric}_band-alpha_per-epoch.npz"
                    )
                    fpath = fc_dir / fname
                    if not fpath.exists():
                        report.fc_anomalies += 1
                        report.anomalies.append(Anomaly("FC", fname, "exists", "MISSING"))
                        continue
                    report.fc_found += 1
                    try:
                        d = np.load(fpath, allow_pickle=False)
                        mat = d["fc_matrix"]
                    except Exception as e:
                        report.fc_anomalies += 1
                        report.anomalies.append(Anomaly("FC", fname, "load", str(e)[:80]))
                        continue

                    ok = True

                    if mat.shape != (n_labels, n_labels):
                        report.anomalies.append(
                            Anomaly("FC", fname, "shape", f"{mat.shape} != ({n_labels},{n_labels})")
                        )
                        ok = False

                    if not np.isfinite(mat).all():
                        report.anomalies.append(
                            Anomaly(
                                "FC", fname, "finite", f"{int(np.sum(~np.isfinite(mat)))} NaN/Inf"
                            )
                        )
                        ok = False
                    else:
                        # Symmetry check
                        sym_err = float(np.abs(mat - mat.T).max())
                        if sym_err > 1e-6:
                            report.anomalies.append(
                                Anomaly("FC", fname, "symmetry", f"max_err={sym_err:.2e}")
                            )
                            ok = False

                        # Controlli di range sugli elementi fuori diagonale
                        mask_offdiag = ~np.eye(n_labels, dtype=bool)
                        off = mat[mask_offdiag]
                        med = float(np.median(off))
                        mx = float(np.abs(off).max())

                        if metric == "wpli":
                            if not (0.0 <= mx <= _WPLI_OFFDIAG_MAX_ABS):
                                report.anomalies.append(
                                    Anomaly(
                                        "FC", fname, "wpli_range", f"max_abs={mx:.4f} out of [0,1]"
                                    )
                                )
                                ok = False
                            # Salva le statistiche per soggetto
                            st = stats_map[(sub, atlas)]
                            if cond == "EO":
                                st.wpli_eo_median = med
                                st.wpli_eo_max = mx
                            else:
                                st.wpli_ec_median = med
                                st.wpli_ec_max = mx

                        elif metric == "coh":
                            if not (_COH_MIN <= med <= _COH_MAX) or not (mx <= _COH_MAX + 1e-6):
                                report.anomalies.append(
                                    Anomaly(
                                        "FC", fname, "coh_range", f"median={med:.4f}, max={mx:.4f}"
                                    )
                                )
                                ok = False
                            st = stats_map[(sub, atlas)]
                            if cond == "EO":
                                st.coh_eo_median = med
                            else:
                                st.coh_ec_median = med

                    if ok:
                        report.fc_valid += 1
                    else:
                        report.fc_anomalies += 1

    report.subject_stats = list(stats_map.values())


def _validate_features(xs_dir: Path, report: ValidationReport) -> None:
    """Valida le matrici di feature ``X_*.npz`` e i file ``y.npy``/``groups.npy``.

    Controlla forma (30 campioni, n_archi atteso), finitezza, bilanciamento
    delle classi (15+15) e numero di gruppi (15 soggetti).

    Args:
        xs_dir: cartella delle feature.
        report: report aggiornato in-place.
    """
    y_path = xs_dir / "y.npy"
    groups_path = xs_dir / "groups.npy"

    # Prima y e groups (etichette e gruppi di CV)
    y = groups = None
    if not y_path.exists():
        report.feat_anomalies += 1
        report.anomalies.append(Anomaly("features", "y.npy", "exists", "MISSING"))
    else:
        y = np.load(y_path)
        if y.shape != (_N_SAMPLES_EXPECTED,):
            report.feat_anomalies += 1
            report.anomalies.append(
                Anomaly("features", "y.npy", "shape", f"{y.shape} != ({_N_SAMPLES_EXPECTED},)")
            )
        unique_y = np.unique(y)
        if not np.array_equal(unique_y, [0, 1]):
            report.feat_anomalies += 1
            report.anomalies.append(Anomaly("features", "y.npy", "values", f"unique={unique_y}"))
        n0, n1 = int(np.sum(y == 0)), int(np.sum(y == 1))
        if n0 != _N_SUBJECTS or n1 != _N_SUBJECTS:
            report.feat_anomalies += 1
            report.anomalies.append(
                Anomaly(
                    "features",
                    "y.npy",
                    "balance",
                    f"class0={n0}, class1={n1} (expect {_N_SUBJECTS} each)",
                )
            )

    if not groups_path.exists():
        report.feat_anomalies += 1
        report.anomalies.append(Anomaly("features", "groups.npy", "exists", "MISSING"))
    else:
        groups = np.load(groups_path)
        if groups.shape != (_N_SAMPLES_EXPECTED,):
            report.feat_anomalies += 1
            report.anomalies.append(
                Anomaly(
                    "features", "groups.npy", "shape", f"{groups.shape} != ({_N_SAMPLES_EXPECTED},)"
                )
            )
        if len(np.unique(groups)) != _N_SUBJECTS:
            report.feat_anomalies += 1
            report.anomalies.append(
                Anomaly(
                    "features",
                    "groups.npy",
                    "unique_groups",
                    f"{len(np.unique(groups))} != {_N_SUBJECTS}",
                )
            )

    for atlas in ATLASES:
        for metric in METRICS:
            fname = f"X_{atlas}_{metric}_alpha.npz"
            fpath = xs_dir / fname
            if not fpath.exists():
                report.feat_anomalies += 1
                report.anomalies.append(Anomaly("features", fname, "exists", "MISSING"))
                continue
            report.feat_found += 1
            try:
                X = np.load(fpath, allow_pickle=False)["X"]
            except Exception as e:
                report.feat_anomalies += 1
                report.anomalies.append(Anomaly("features", fname, "load", str(e)[:80]))
                continue

            ok = True
            expected_nfeat = _FEAT_N_LABELS[atlas]

            if X.shape[0] != _N_SAMPLES_EXPECTED:
                report.anomalies.append(
                    Anomaly(
                        "features", fname, "n_samples", f"{X.shape[0]} != {_N_SAMPLES_EXPECTED}"
                    )
                )
                ok = False

            if X.shape[1] != expected_nfeat:
                report.anomalies.append(
                    Anomaly("features", fname, "n_features", f"{X.shape[1]} != {expected_nfeat}")
                )
                ok = False

            if not np.isfinite(X).all():
                n_bad = int(np.sum(~np.isfinite(X)))
                report.anomalies.append(Anomaly("features", fname, "finite", f"{n_bad} NaN/Inf"))
                ok = False

            if ok:
                report.feat_valid += 1
            else:
                report.feat_anomalies += 1


# ===== 4. Generazione del report =====
def _render_report(report: ValidationReport) -> str:
    """Rende il report di validazione in Markdown.

    Args:
        report: esito della validazione.

    Returns:
        Testo Markdown (riepilogo, anomalie, tabelle wPLI/coerenza, note).
    """
    ts = report.timestamp
    verdict = report.verdict
    verdict_icon = {"PASS": "[OK]", "WARN": "[WARNING]", "FAIL": "[FAIL]"}[verdict]

    lines = [
        "# N=15 Outputs — Validation Report",
        "",
        f"**Timestamp**: {ts}  ",
        "**Data root**: `data/{label_ts,connectivity,features}/ds005385/`  ",
        f"**Subjects**: {len(SUBJECTS)} ({', '.join(SUBJECTS[:5])}, ...)",
        "",
        "## Summary",
        "",
        "| Categoria | File attesi | Trovati | Validi | Anomalie |",
        "|-----------|-------------|---------|--------|----------|",
        f"| label_tc per-epoch | {report.lt_expected} | {report.lt_found} | {report.lt_valid} | {report.lt_anomalies} |",
        f"| FC matrices (per-epoch) | {report.fc_expected} | {report.fc_found} | {report.fc_valid} | {report.fc_anomalies} |",
        f"| Feature matrices X | {report.feat_expected} | {report.feat_found} | {report.feat_valid} | {report.feat_anomalies} |",
        "",
        f"**Verdict**: {verdict_icon} **{verdict}**",
        "",
    ]

    if report.anomalies:
        lines += [
            "## Anomalie dettagliate",
            "",
            "| Categoria | File | Campo | Valore |",
            "|-----------|------|-------|--------|",
        ]
        for a in report.anomalies:
            lines.append(f"| {a.category} | `{a.file}` | {a.field} | {a.value} |")
        lines.append("")
    else:
        lines += ["## Anomalie dettagliate", "", "Nessuna anomalia rilevata.", ""]

    # wPLI table
    lines += [
        "## Range fisiologico — wPLI off-diagonal (per sub e atlante)",
        "",
        "| Sub | Atlas | EO median | EC median | EO max | EC max |",
        "|-----|-------|-----------|-----------|--------|--------|",
    ]
    for st in report.subject_stats:
        lines.append(
            f"| {st.subject} "
            f"| {st.atlas} "
            f"| {st.wpli_eo_median:.4f} "
            f"| {st.wpli_ec_median:.4f} "
            f"| {st.wpli_eo_max:.4f} "
            f"| {st.wpli_ec_max:.4f} |"
        )

    lines += [
        "",
        "## Range — coh off-diagonal (per sub e atlante)",
        "",
        "| Sub | Atlas | EO median | EC median |",
        "|-----|-------|-----------|-----------|",
    ]
    for st in report.subject_stats:
        lines.append(
            f"| {st.subject} | {st.atlas} | {st.coh_eo_median:.4f} | {st.coh_ec_median:.4f} |"
        )

    lines += [
        "",
        "## Note",
        "",
        "- Validazione read-only — nessuna modifica ai dati.",
        "- label_tc: chiave `label_tc`, shape `(n_epochs, n_labels, n_times)`.",
        "- FC: chiave `fc_matrix`, simmetria verificata (`max|M - M^T| < 1e-6`).",
        "- Features: `X` da npz, `y`/`groups` da `.npy` separati.",
        "- wPLI atteso: off-diagonal in [0, 1], range fisiologico ~[0.05, 0.50].",
        "- coh atteso: off-diagonal in [0, 1].",
        "",
    ]
    return "\n".join(lines)


# ===== 5. Entry point =====
def validate(data_root: Path, output: Path) -> int:
    """Esegue la validazione completa e scrive il report.

    Args:
        data_root: radice del repo (contiene ``data/``).
        output: percorso del report Markdown da scrivere.

    Returns:
        Exit code: 0 = PASS, 1 = WARN, 2 = FAIL.

    Side effects:
        Scrive ``output`` (crea le cartelle mancanti) e stampa il riepilogo.
    """
    lt_dir = data_root / "data/label_ts/ds005385"
    fc_dir = data_root / "data/connectivity/ds005385"
    xs_dir = data_root / "data/features/ds005385"

    report = ValidationReport(timestamp=datetime.datetime.now().astimezone().isoformat())

    _validate_label_tc(lt_dir, report)
    _validate_fc(fc_dir, report)
    _validate_features(xs_dir, report)

    md = _render_report(report)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(md)

    verdict = report.verdict
    print(f"Validation complete — Verdict: {verdict}")
    print(
        f"  label_tc : {report.lt_valid}/{report.lt_found} valid ({report.lt_anomalies} anomalies)"
    )
    print(
        f"  FC       : {report.fc_valid}/{report.fc_found} valid ({report.fc_anomalies} anomalies)"
    )
    print(
        f"  features : {report.feat_valid}/{report.feat_found} valid ({report.feat_anomalies} anomalies)"
    )
    print(f"  Report   → {output}")

    return {"PASS": 0, "WARN": 1, "FAIL": 2}[verdict]


def main() -> int:
    """Interpreta gli argomenti CLI (``--data-root``, ``--output``) e lancia :func:`validate`."""
    ap = argparse.ArgumentParser(description="Validate N15 — data integrity check")
    ap.add_argument("--data-root", default=".", type=Path, help="Tesi_2.0 root (default: cwd)")
    ap.add_argument(
        "--output", default="reports/VALIDATE_N15.md", type=Path, help="Output markdown report"
    )
    args = ap.parse_args()
    return validate(args.data_root, args.output)


if __name__ == "__main__":
    sys.exit(main())

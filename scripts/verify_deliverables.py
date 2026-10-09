"""Verifica la presenza dei deliverable di tutti gli sprint completati.

Scopo:
    Audit di completezza: per ogni sprint con ``status == "done"`` nella coda
    di dispatch controlla che i file elencati in ``deliverables`` esistano.

Input:
    ``.planning/DISPATCH_QUEUE_tesi.jsonl`` (una riga JSON per sprint, chiavi
    ``id``, ``sprint``, ``status``, ``deliverables``).

Output:
    Report Markdown su stdout e in ``reports/DELIVERABLES_AUDIT.md``.
    Exit code 0 se nessun file manca, 1 altrimenti.

Esempio:
    python scripts/verify_deliverables.py
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


# ===== 1. Scansione della coda =====
def verify_deliverables(queue_file: str | Path = ".planning/DISPATCH_QUEUE_tesi.jsonl") -> dict:
    """Scansiona gli sprint completati e verifica i deliverable.

    Parameters
    ----------
    queue_file:
        Percorso del file JSONL della coda di dispatch.

    Returns
    -------
    dict
        Chiavi ``timestamp``, ``total_done``, ``total_present``,
        ``total_missing`` e ``sprints`` (lista di dict con ``id``, ``sprint``,
        ``deliverables`` e ``verdict`` PASS/MISSING).

    Side effects
    ------------
    Nessuno: legge solo il file della coda e controlla l'esistenza dei path.
    """
    queue_file = Path(queue_file)
    results = {
        "timestamp": datetime.now().isoformat(),
        "total_done": 0,
        "total_present": 0,
        "total_missing": 0,
        "sprints": [],
    }

    with open(queue_file) as f:
        for line in f:
            task = json.loads(line)

            # Controlliamo solo gli sprint completati
            if task["status"] != "done":
                continue

            if "deliverables" not in task or not task["deliverables"]:
                continue

            results["total_done"] += 1
            sprint_result = {
                "id": task["id"],
                "sprint": task["sprint"][:60],  # Truncate for display
                "deliverables": [],
            }

            all_present = True
            for deliverable in task["deliverables"]:
                # Il path può essere assoluto/relativo al CWD: proviamo entrambi
                paths_to_check = [
                    Path(deliverable),
                    Path.cwd() / deliverable,
                ]

                found = False
                for p in paths_to_check:
                    if p.exists():
                        found = True
                        results["total_present"] += 1
                        sprint_result["deliverables"].append(
                            {"path": deliverable, "status": "[OK]"}
                        )
                        break

                if not found:
                    all_present = False
                    results["total_missing"] += 1
                    sprint_result["deliverables"].append({"path": deliverable, "status": "[FAIL]"})

            sprint_result["verdict"] = "PASS" if all_present else "MISSING"
            results["sprints"].append(sprint_result)

    return results


# ===== 2. Formattazione del report =====
def format_report(audit_results: dict) -> str:
    """Formatta i risultati dell'audit come report Markdown.

    Parameters
    ----------
    audit_results:
        Dizionario restituito da :func:`verify_deliverables`.

    Returns
    -------
    str
        Testo Markdown con riepilogo, tabella per sprint ed elenco dei
        deliverable mancanti. Nessun side effect su file.
    """
    lines = [
        "# Deliverables Audit Report",
        "",
        f"**Timestamp**: {audit_results['timestamp']}",
        f"**Total completed**: {audit_results['total_done']} sprints",
        f"**Deliverables present**: {audit_results['total_present']}",
        f"**Deliverables missing**: {audit_results['total_missing']}",
        "",
    ]

    # Summary verdict
    if audit_results["total_missing"] == 0:
        lines.append("**Verdict**: CLEAN [OK]")
    else:
        lines.append("**Verdict**: MISSING FILES [WARNING]")

    lines.extend(
        [
            "",
            "## Sprint Breakdown",
            "",
            "| Sprint ID | Status | Deliverables |",
            "|-----------|--------|--------------|",
        ]
    )

    for sprint in audit_results["sprints"]:
        verdict = sprint["verdict"]
        deliverable_str = ", ".join(
            f"{d['status']} {Path(d['path']).name}" for d in sprint["deliverables"]
        )
        sprint_id = sprint["id"]
        lines.append(f"| {sprint_id} | {verdict} | {deliverable_str} |")

    lines.extend(
        [
            "",
            "## Missing Deliverables",
            "",
        ]
    )

    missing = [sprint for sprint in audit_results["sprints"] if sprint["verdict"] == "MISSING"]

    if not missing:
        lines.append("[OK] All deliverables present")
    else:
        lines.append("The following sprints have missing deliverables:")
        lines.append("")
        for sprint in missing:
            lines.append(f"### {sprint['id']}")
            lines.append("")
            for d in sprint["deliverables"]:
                if d["status"] == "[FAIL]":
                    lines.append(f"- **MISSING**: {d['path']}")
            lines.append("")

    return "\n".join(lines)


# ===== 3. Entry point CLI =====
if __name__ == "__main__":
    import sys

    audit = verify_deliverables()
    report = format_report(audit)
    print(report)

    # Also write to file
    report_path = Path("reports/DELIVERABLES_AUDIT.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w") as f:
        f.write(report)

    # Exit code based on missing deliverables
    sys.exit(0 if audit["total_missing"] == 0 else 1)

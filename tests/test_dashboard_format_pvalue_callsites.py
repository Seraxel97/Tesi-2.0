"""Regression test — format_pvalue() call-site arity nella dashboard.

Contesto: `analysis.stats_utility.format_pvalue(p_value, n_perm)` richiede 2
argomenti. Un bug (2026-06-12) aveva 4 call-site nella dashboard che lo
chiamavano con 1 solo argomento → `TypeError` solo cambiando target ML su
Sesso/Età (il positive-control EO/EC, default, mascherava il crash). Il pytest
esistente non testava il path interattivo, quindi era un false-positive.

Questo test scansiona staticamente (AST) i file Python della dashboard e
verifica che ogni chiamata a `format_pvalue` abbia almeno 2 argomenti
posizionali. Non richiede Streamlit running.
"""

from __future__ import annotations

import ast
from pathlib import Path

_DASHBOARD = Path(__file__).parent.parent / "dashboard"


def _format_pvalue_calls(tree: ast.AST) -> list[ast.Call]:
    calls = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fn = node.func
            name = fn.id if isinstance(fn, ast.Name) else getattr(fn, "attr", None)
            if name == "format_pvalue":
                calls.append(node)
    return calls


def test_format_pvalue_callsites_pass_two_args():
    """Ogni chiamata a format_pvalue nella dashboard deve passare p_value + n_perm."""
    offenders = []
    for py in _DASHBOARD.rglob("*.py"):
        tree = ast.parse(py.read_text(encoding="utf-8"), filename=str(py))
        for call in _format_pvalue_calls(tree):
            n_args = len(call.args) + len(call.keywords)
            if n_args < 2:
                offenders.append(
                    f"{py.relative_to(_DASHBOARD.parent)}:{call.lineno} ({n_args} arg)"
                )
    assert not offenders, (
        "format_pvalue() richiede (p_value, n_perm); call-site con <2 arg:\n  "
        + "\n  ".join(offenders)
    )

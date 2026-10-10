"""Test CLI unificato — typer app callable senza errori (--help e subcomandi)."""

from __future__ import annotations

import re

from typer.testing import CliRunner

from cli.main import app

runner = CliRunner(env={"NO_COLOR": "1", "TERM": "dumb"})


def _out(result) -> str:
    """Output del comando senza codici colore ANSI (Rich li emette in CI)."""
    return re.sub(r"\x1b\[[0-9;]*m", "", result.output)


def test_main_help() -> None:
    """App principale risponde a --help senza errori."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Pipeline EEG" in _out(result)
    assert "step1" in _out(result)
    assert "step2" in _out(result)
    assert "bench" in _out(result)
    assert "e2e" in _out(result)


def test_step1_help() -> None:
    """Subcomando step1 --help è accessibile."""
    result = runner.invoke(app, ["step1", "--help"])
    assert result.exit_code == 0
    assert "STEP 1" in _out(result)
    assert "--config" in _out(result)


def test_step2_help() -> None:
    """Subcomando step2 --help è accessibile."""
    result = runner.invoke(app, ["step2", "--help"])
    assert result.exit_code == 0
    assert "STEP 2" in _out(result)
    assert "--config" in _out(result)
    assert "--subject" in _out(result)
    assert "--method" in _out(result)


def test_bench_help() -> None:
    """Subcomando bench --help è accessibile."""
    result = runner.invoke(app, ["bench", "--help"])
    assert result.exit_code == 0
    assert "700" in _out(result) or "benchmark" in result.output.lower()
    assert "--output" in _out(result)


def test_e2e_help() -> None:
    """Subcomando e2e --help è accessibile."""
    result = runner.invoke(app, ["e2e", "--help"])
    assert result.exit_code == 0
    out = _out(result)
    assert "E2E" in out
    assert "--atlas" in out
    assert "--metric" in out


def test_unknown_command() -> None:
    """Comando sconosciuto produce exit code != 0."""
    result = runner.invoke(app, ["nonexistent"])
    assert result.exit_code != 0

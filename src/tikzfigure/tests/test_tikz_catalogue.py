"""Run the parser over every example in ``tikz_catalogue/``."""

import shutil
import subprocess
from pathlib import Path

import pytest

from tikzfigure.parser import parse_tikz
from tikzfigure.parser.catalogue import (
    evaluate_entry,
    format_report,
    load_catalogue,
    main,
)

CATALOGUE = Path(__file__).resolve().parents[3] / "tikz_catalogue"
ENTRIES = load_catalogue(CATALOGUE) if CATALOGUE.is_dir() else []

pytestmark = pytest.mark.skipif(not ENTRIES, reason="tikz_catalogue/ not available")


@pytest.mark.parametrize("entry", ENTRIES, ids=lambda e: e.name)
def test_catalogue_entry_parses_stably(entry):
    report = evaluate_entry(entry)
    assert report.error is None
    assert report.fixed_point, "re-parsing the generated TikZ changed it"
    assert report.coverage >= entry.min_coverage, (
        f"coverage dropped to {report.coverage:.0%} "
        f"(min {entry.min_coverage:.0%}):\n{report.result.summary()}"
    )


def test_catalogue_report_and_cli(capsys):
    reports = [evaluate_entry(entry) for entry in ENTRIES]
    report = format_report(reports, details=True)
    assert "| **total** |" in report
    assert "## Unsupported constructs" in report
    assert main([str(CATALOGUE)]) == 0
    assert "| Entry |" in capsys.readouterr().out


def _render(tex: str, directory: Path, name: str) -> tuple:
    import fitz

    (directory / f"{name}.tex").write_text(tex)
    completed = subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", f"{name}.tex"],
        cwd=directory,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout[-2000:]
    with fitz.open(directory / f"{name}.pdf") as doc:
        pixmap = doc[0].get_pixmap(dpi=60)
        return pixmap.width, pixmap.height, pixmap.samples


@pytest.mark.latex
@pytest.mark.skipif(shutil.which("pdflatex") is None, reason="pdflatex not installed")
@pytest.mark.parametrize("entry", ENTRIES, ids=lambda e: e.name)
def test_catalogue_entry_renders_identically(entry, tmp_path):
    pytest.importorskip("fitz")
    original = _render(entry.source, tmp_path, "original")
    figure = parse_tikz(entry.source).figure
    regenerated = _render(figure.generate_standalone(), tmp_path, "regenerated")
    assert original == regenerated, "parsed figure renders differently"

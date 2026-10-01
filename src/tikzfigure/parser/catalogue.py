"""Evaluate the TikZ parser against a catalogue of TikZ documents.

A catalogue is a directory of ``.tex`` files, each containing a
``tikzpicture`` (usually as a complete standalone document so it can be
compiled on its own). Optional metadata lines at the top of a file look like::

    % catalogue: title = Flowchart with positioning
    % catalogue: min-coverage = 0.8

For every entry the report shows how many statements were mapped to
tikzfigure objects, whether re-parsing the generated code reproduces it
exactly, and which unsupported constructs forced a raw-TikZ fallback. The
aggregated list of reasons is a to-do list of what to wrap next.

Usage::

    python -m tikzfigure.parser.catalogue [DIRECTORY] [--details] [--fail-under 0.5]
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from tikzfigure.parser import ParseResult, TikzParseError, parse_tikz

_META = re.compile(r"^%\s*catalogue:\s*([\w-]+)\s*=\s*(.*?)\s*$")


@dataclass
class CatalogueEntry:
    """One TikZ example in the catalogue."""

    path: Path
    source: str
    metadata: dict[str, str] = field(default_factory=dict)

    @property
    def name(self) -> str:
        return self.path.stem

    @property
    def title(self) -> str:
        return self.metadata.get("title", self.name)

    @property
    def min_coverage(self) -> float:
        return float(self.metadata.get("min-coverage", "0"))


@dataclass
class EntryReport:
    """Parser evaluation of a single :class:`CatalogueEntry`."""

    entry: CatalogueEntry
    result: ParseResult | None = None
    generated: str | None = None
    fixed_point: bool = False
    error: str | None = None

    @property
    def coverage(self) -> float:
        return self.result.coverage if self.result is not None else 0.0


def load_catalogue(directory: Path | str) -> list[CatalogueEntry]:
    """Load all ``.tex`` entries of *directory*, sorted by file name."""
    entries = []
    for path in sorted(Path(directory).glob("*.tex")):
        source = path.read_text(encoding="utf-8")
        metadata: dict[str, str] = {}
        for line in source.splitlines():
            match = _META.match(line.strip())
            if match:
                metadata[match.group(1)] = match.group(2)
        entries.append(CatalogueEntry(path=path, source=source, metadata=metadata))
    return entries


def evaluate_entry(entry: CatalogueEntry) -> EntryReport:
    """Parse *entry*, regenerate it and check the round trip is stable."""
    report = EntryReport(entry)
    try:
        report.result = parse_tikz(entry.source)
        report.generated = report.result.figure.generate_tikz()
        regenerated = parse_tikz(report.generated).figure.generate_tikz()
        report.fixed_point = regenerated == report.generated
    except TikzParseError as exc:
        report.error = str(exc)
    return report


def evaluate_catalogue(directory: Path | str) -> list[EntryReport]:
    return [evaluate_entry(entry) for entry in load_catalogue(directory)]


def format_report(reports: list[EntryReport], details: bool = False) -> str:
    """Render *reports* as Markdown."""
    lines = [
        "| Entry | Statements | Mapped | Coverage | Stable round trip |",
        "| --- | ---: | ---: | ---: | :---: |",
    ]
    total = mapped = 0
    reasons: Counter[str] = Counter()
    reason_entries: dict[str, set[str]] = defaultdict(set)
    for report in reports:
        name = report.entry.name
        if report.result is None:
            lines.append(f"| {name} | – | – | error | ✗ |")
            continue
        result = report.result
        total += len(result.diagnostics)
        mapped += len(result.mapped)
        lines.append(
            f"| {name} | {len(result.diagnostics)} | {len(result.mapped)} | "
            f"{result.coverage:.0%} | {'✓' if report.fixed_point else '✗'} |"
        )
        for diagnostic in result.raw:
            reason = diagnostic.reason or "unknown"
            reasons[reason] += 1
            reason_entries[reason].add(name)

    overall = mapped / total if total else 1.0
    lines.append(f"| **total** | {total} | {mapped} | **{overall:.0%}** | |")

    errors = [r for r in reports if r.error]
    if errors:
        lines += ["", "## Parse errors", ""]
        lines += [f"- `{r.entry.name}`: {r.error}" for r in errors]

    if reasons:
        lines += [
            "",
            "## Unsupported constructs",
            "",
            "| Reason | Statements | Entries |",
            "| --- | ---: | --- |",
        ]
        for reason, count in reasons.most_common():
            entries = ", ".join(sorted(reason_entries[reason]))
            lines.append(f"| {reason} | {count} | {entries} |")

    if details:
        for report in reports:
            if report.result is None or not report.result.raw:
                continue
            lines += ["", f"## {report.entry.name}: {report.entry.title}", ""]
            for diagnostic in report.result.raw:
                source = diagnostic.source
                if len(source) > 90:
                    source = source[:87] + "..."
                why = diagnostic.reason
                if diagnostic.detail:
                    why = f"{why} ({diagnostic.detail})"
                lines.append(f"- line {diagnostic.line}: {why} — `{source}`")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m tikzfigure.parser.catalogue",
        description="Report how much of a TikZ catalogue tikzfigure can parse.",
    )
    parser.add_argument("directory", nargs="?", default="tikz_catalogue")
    parser.add_argument(
        "--details", action="store_true", help="list every raw statement"
    )
    parser.add_argument(
        "--fail-under",
        type=float,
        default=None,
        help="exit with status 1 if overall coverage is below this fraction",
    )
    args = parser.parse_args(argv)

    if not Path(args.directory).is_dir():
        parser.error(f"catalogue directory not found: {args.directory}")
    reports = evaluate_catalogue(args.directory)
    print(format_report(reports, details=args.details))

    results = [r.result for r in reports if r.result is not None]
    total = sum(len(r.diagnostics) for r in results)
    mapped = sum(len(r.mapped) for r in results)
    overall = mapped / total if total else 1.0
    failed = any(r.error for r in reports) or not all(r.fixed_point for r in reports)
    if args.fail_under is not None and overall < args.fail_under:
        failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

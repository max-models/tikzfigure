"""End-to-end checks that the generated TikZ is real, compilable LaTeX.

Most of the suite asserts on the *string* tikzfigure emits. That catches
regressions in the generator but not the failure mode that actually bites
users: output that looks plausible and then fails in pdflatex, or silently
renders the wrong thing.

This module builds one small figure per public feature and

* compiles it with pdflatex (``-m latex``, skipped when pdflatex is missing),
* compares its TikZ against a committed snapshot, so changes to the output of
  any feature show up as a reviewable diff rather than going unnoticed.

Snapshots live in ``tests/snapshots/``. To accept intentional changes, run::

    UPDATE_SNAPSHOTS=1 pytest src/tikzfigure/tests/test_compile_smoke.py
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

from tikzfigure import TikzFigure

SNAPSHOT_DIR = Path(__file__).parent / "snapshots"
UPDATE_SNAPSHOTS = os.environ.get("UPDATE_SNAPSHOTS", "") not in ("", "0")

needs_pdflatex = pytest.mark.skipif(
    shutil.which("pdflatex") is None, reason="pdflatex not installed"
)


# ------------------------------------------------------------- #
# One builder per feature. Keep these small: they exist to prove the
# construct compiles, not to exercise every option.


def _nodes() -> TikzFigure:
    fig = TikzFigure()
    a = fig.node(x=0, y=0, shape="circle", fill="blue!40", content="A")
    b = fig.node(x=3, y=0, shape="rectangle", draw="black", content="B")
    fig.draw([a, b], arrows="->", line_width=2, color="gray")
    fig.midpoint(a, b, content="mid")
    return fig


def _shapes() -> TikzFigure:
    fig = TikzFigure()
    fig.circle((0, 0), 1.0, fill="red!30", draw="black")
    fig.rectangle((2, -1), (4, 1), fill="blue!20", rounded_corners="3pt")
    fig.ellipse((6, 0), 1.5, 0.8, draw="green!60!black", dash_pattern="on 2pt off 2pt")
    fig.polygon((9, 0), 1.0, 6, fill="yellow!40")
    fig.triangle((12, 0), 1.0, fill="purple!30")
    fig.square((15, 0), 1.0, fill="orange!30")
    return fig


def _paths() -> TikzFigure:
    fig = TikzFigure()
    fig.line((0, 0), (2, 2), arrows="->", line_width="1pt")
    fig.arc((3, 0), 0, 120, 1.0, color="red")
    fig.parabola((5, 0), (7, 0), (6, 1), color="blue")
    fig.grid((8, 0), (10, 2), step=0.5, color="gray!40")
    fig.filldraw([(11, 0), (12, 1), (13, 0)], fill="cyan!30", draw="black")
    fig.clip([(0, -2), (14, -2), (14, 3), (0, 3)])
    return fig


def _loops_and_variables() -> TikzFigure:
    fig = TikzFigure()
    fig.variable("R", 1.5)
    with fig.loop("angle", range(0, 360, 45)) as loop:
        loop.node(
            x=r"\R*cos(\angle)", y=r"\R*sin(\angle)", shape="circle", fill="red!50"
        )
    return fig


def _scopes_and_layers() -> TikzFigure:
    fig = TikzFigure()
    with fig.scope(options="rotate=30", xshift="2cm", yshift="1cm") as scope:
        a = scope.node((0, 0), label="sa", content="A")
        b = scope.node((1, 0), label="sb", content="B")
        scope.draw([a, b], color="green!50!black")
    fig.circle((0, 0), 0.5, fill="blue!40", layer=1)
    fig.circle((1, 0), 0.5, fill="red!40", layer=0)
    return fig


def _styles_and_colors() -> TikzFigure:
    fig = TikzFigure()
    fig.colorlet("mycolor", "blue!60!black")
    fig.add_style("boxed", options="draw, rounded corners, fill=mycolor!20")
    fig.node(x=0, y=0, content="styled", options="boxed")
    return fig


def _declared_functions() -> TikzFigure:
    fig = TikzFigure()
    # The body is PGF math, so the argument is referenced as \x, not x.
    fig.declare_function("myfunc", "x", r"\x^2")
    fig.add_plot(r"\x", r"myfunc(\x)", domain=(0, 2), samples=20)
    return fig


def _axis() -> TikzFigure:
    fig = TikzFigure()
    axis = fig.axis2d(xlabel="$x$", ylabel="$y$", xlim=(0, 10), ylim=(0, 100))
    axis.add_plot([0, 1, 2, 3], [0, 1, 4, 9])
    return fig


def _tiny_png() -> bytes:
    """A 2x2 RGB PNG, made without an imaging library."""
    import struct
    import zlib

    def chunk(kind: bytes, data: bytes) -> bytes:
        body = kind + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body))

    rows = b"".join(
        b"\x00" + bytes(pixels)
        for pixels in ([255, 0, 0, 0, 0, 255], [0, 255, 0, 255, 255, 0])
    )
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", 2, 2, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(rows))
        + chunk(b"IEND", b"")
    )


def _axis_extras() -> TikzFigure:
    fig = TikzFigure()
    axis = fig.axis2d(
        xlabel="$x$, in cm",
        ylabel="$y$",
        title="Extras, all of them",
        xlim=(0, 2),
        ylim=(0, 2),
    )
    axis.add_graphics(
        0,
        2,
        0,
        2,
        data=_tiny_png(),
        filename="extras.png",
        plot_options=["forget plot"],
    )
    axis.add_plot([0, 1, 2], [0, 1.5, 0.5], label="line, labelled", color="red")
    axis.add_plot(
        [0.2, 0.8, 0.5], [0.2, 0.2, 0.8], cycle=True, fill="blue", fill_opacity=0.3
    )
    axis.add_plot(
        [0.5, 1.0, 1.5],
        [1.5, 1.0, 1.8],
        meta=[0.0, 1.0, 2.0],
        options=["scatter", "only marks", "point meta=explicit"],
    )
    axis.add_raw(r"\node at (axis cs:1.5,0.3) {raw};")
    axis.set_ticks("x", [0, 1, 2], ["zero", "one, really", "two"])
    axis.set_legend(at=(0.02, 0.98), anchor="north west", style="draw=none")
    return fig


def _matrix() -> TikzFigure:
    fig = TikzFigure()
    fig.add_matrix([["a", "b"], ["c", "d"]], x=0, y=0, options="matrix of nodes, draw")
    return fig


def _gantt() -> TikzFigure:
    fig = TikzFigure()
    fig.add_gantt_chart(
        0,
        10,
        options=["hgrid", "vgrid"],
        rows=[
            {"type": "titlelist", "content": "1,...,10"},
            {"type": "group", "content": "Planning", "start": 1, "end": 4},
            {"type": "bar", "content": "Design", "start": 1, "end": 4},
            {"type": "bar", "content": "Build", "start": 4, "end": 9},
            {"type": "milestone", "content": "Ship", "at": 10},
        ],
    )
    return fig


def _fit() -> TikzFigure:
    fig = TikzFigure()
    a = fig.node(x=0, y=0, content="A", label="a")
    b = fig.node(x=2, y=1, content="B", label="b")
    fig.add_fit([a, b], options="draw, dashed, inner sep=4pt")
    return fig


def _spy() -> TikzFigure:
    fig = TikzFigure()
    fig.circle((0, 0), 1.0, fill="red!30")
    fig.add_spy(on=(0.5, 0.5))
    return fig


def _plot3d() -> TikzFigure:
    fig = TikzFigure(ndim=3)
    fig.plot3d([0, 1, 2], [0, 1, 0], [0, 1, 2])
    return fig


def _raw() -> TikzFigure:
    fig = TikzFigure()
    fig.add_raw(r"\draw[thick, red] (0,0) -- (1,1);")
    return fig


#: name -> builder. The name is also the snapshot filename.
FIGURES = {
    "axis": _axis,
    "axis_extras": _axis_extras,
    "declared_functions": _declared_functions,
    "fit": _fit,
    "gantt": _gantt,
    "loops_and_variables": _loops_and_variables,
    "matrix": _matrix,
    "nodes": _nodes,
    "paths": _paths,
    "plot3d": _plot3d,
    "raw": _raw,
    "scopes_and_layers": _scopes_and_layers,
    "shapes": _shapes,
    "spy": _spy,
    "styles_and_colors": _styles_and_colors,
}


# ------------------------------------------------------------- #
# Tests


@pytest.mark.parametrize("name", sorted(FIGURES))
def test_figure_builds(name):
    """The builder runs and produces a non-empty tikzpicture."""
    tikz = FIGURES[name]().generate_tikz()
    assert "\\begin{tikzpicture}" in tikz
    assert "\\end{tikzpicture}" in tikz


@pytest.mark.parametrize("name", sorted(FIGURES))
def test_tikz_matches_snapshot(name):
    """The emitted TikZ matches its committed snapshot."""
    # skip_header drops the generated-by banner, which carries the package
    # version -- otherwise every release would invalidate every snapshot.
    tikz = FIGURES[name]().generate_standalone(skip_header=True)
    snapshot = SNAPSHOT_DIR / f"{name}.tex"

    if UPDATE_SNAPSHOTS:
        SNAPSHOT_DIR.mkdir(exist_ok=True)
        snapshot.write_text(tikz)
        pytest.skip(f"updated snapshot {snapshot.name}")

    assert snapshot.exists(), (
        f"missing snapshot {snapshot.name}; regenerate with "
        f"UPDATE_SNAPSHOTS=1 pytest {Path(__file__).name}"
    )
    assert tikz == snapshot.read_text(), (
        f"output for {name!r} changed. If that is intended, regenerate with "
        f"UPDATE_SNAPSHOTS=1 pytest {Path(__file__).name}"
    )


@pytest.mark.latex
@needs_pdflatex
@pytest.mark.parametrize("name", sorted(FIGURES))
def test_figure_compiles(name, tmp_path):
    """The generated standalone document compiles with pdflatex."""
    figure = FIGURES[name]()
    document = figure.generate_standalone()
    tex_file = tmp_path / f"{name}.tex"
    tex_file.write_text(document)
    for file_name, data in figure.files().items():  # images the axes refer to
        (tmp_path / file_name).write_bytes(data)

    completed = subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", tex_file.name],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, (
        f"pdflatex failed for {name!r}:\n"
        f"{completed.stdout[-3000:]}\n\n--- source ---\n{document}"
    )
    assert (tmp_path / f"{name}.pdf").exists()


@pytest.mark.latex
@needs_pdflatex
def test_compile_pdf_produces_a_pdf(tmp_path):
    """The public compile_pdf() path works against a real pdflatex."""
    output = tmp_path / "figure.pdf"
    _nodes().compile_pdf(filename=output)

    assert output.exists()
    assert output.read_bytes().startswith(b"%PDF")
    # compile_pdf cleans up after itself.
    assert not output.with_suffix(".aux").exists()
    assert not output.with_suffix(".log").exists()


@pytest.mark.latex
@needs_pdflatex
def test_savefig_png(tmp_path):
    """savefig() rasterizes through a real compile."""
    pytest.importorskip("fitz")
    output = tmp_path / "figure.png"
    _shapes().savefig(output, dpi=50)

    assert output.exists()
    assert output.read_bytes().startswith(b"\x89PNG")

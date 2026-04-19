import builtins
import os
import platform
import runpy
import subprocess
import sys
from types import ModuleType

import pytest

from tikzfigure import TikzCoordinate, TikzVector, arrows, colors, styles, units
from tikzfigure.core.base import TikzObject
from tikzfigure.core.color import Color
from tikzfigure.core.figure import TikzFigure
from tikzfigure.core.line import Line
from tikzfigure.core.loop import Loop
from tikzfigure.core.node import Node
from tikzfigure.core.path import TikzPath
from tikzfigure.core.plot import Plot3D
from tikzfigure.core.variable import Variable


class DummyTikzObject(TikzObject):
    def to_tikz(self, output_unit: str | None = None) -> str:
        options = self.tikz_options(output_unit)
        body = "\\dummy"
        if options:
            body += f"[{options}]"
        return self.add_comment(body + ";\n")


def test_tikzobject_options_and_comments():
    obj = TikzObject(options=None, comment=None, layer=1, label="a", foo="bar")
    assert obj.tikz_options() == "foo=bar"
    assert obj.add_comment("X") == "X"

    obj2 = TikzObject(
        options=["draw", "thick"],
        comment="note",
        layer=0,
        label="b",
        fill="red",
    )
    assert obj2.tikz_options() == "draw, thick, fill=red"
    assert obj2.add_comment("Y") == "% note\nY"


def test_tikzobject_to_dict_from_dict():
    obj = TikzObject(label="a", comment="note", layer=2, options=["thick"], fill="red")
    d = obj.to_dict()
    assert d == {
        "label": "a",
        "comment": "note",
        "layer": 2,
        "options": ["thick"],
        "kwargs": {"fill": "red"},
    }

    obj2 = TikzObject.from_dict(d)
    assert obj2.label == "a"
    assert obj2.comment == "note"
    assert obj2.layer == 2
    assert obj2.options == ["thick"]
    assert obj2.kwargs == {"fill": "red"}


def test_tikzobject_rich_values_round_trip():
    obj = TikzObject(
        label="rich",
        options=[styles.dashed, arrows.forward],
        fill=colors.red.mix(colors.blue, 25),
        inner_sep=2 * units.cm,
    )

    d = obj.to_dict()

    assert d["options"][0]["__tikzfigure_serialized_type__"] == "TikzStyle"
    assert d["options"][1]["__tikzfigure_serialized_type__"] == "TikzArrow"
    assert d["kwargs"]["fill"]["__tikzfigure_serialized_type__"] == "TikzColor"
    assert d["kwargs"]["inner_sep"]["__tikzfigure_serialized_type__"] == "TikzDimension"

    obj2 = TikzObject.from_dict(d)
    assert obj2.options == [styles.dashed, arrows.forward]
    assert obj2.kwargs["fill"] == colors.red.mix(colors.blue, 25)
    assert obj2.kwargs["inner_sep"] == 2 * units.cm


def test_tikzobject_check_requires_to_tikz():
    obj = TikzObject(label="plain")

    with pytest.raises(NotImplementedError, match="must implement to_tikz"):
        obj._check()


def test_tikzobject_check_round_trips_concrete_subclass():
    obj = DummyTikzObject(
        label="dummy",
        comment="note",
        options=[styles.dashed],
        draw=colors.red,
    )

    restored = obj._check()

    assert isinstance(restored, DummyTikzObject)
    assert restored == obj


def test_tikzfigure_to_dict_from_dict_roundtrip():
    fig = TikzFigure(
        ndim=2,
        label="fig1",
        grid=True,
        figsize=(8, 5),
        description="desc",
        document_setup="\\usepackage{xcolor}",
        figure_setup="scale=1.5",
    )
    fig.add_package("pgfplots")

    # Add nodes, a path, a variable, a color, raw tikz, and a loop
    n1 = fig.add_node(x=0, y=0, label="A", content="Hello", fill="red")
    n2 = fig.add_node(x=1, y=1, label="B", content="World")
    fig.draw([n1, n2])
    fig.add_raw("\\draw (0,0) -- (1,1);")
    fig.add_variable("myvar", 42)
    fig.colorlet("mycolor", "blue!30")
    fig.add_style(
        "important line",
        options=[styles.very_thick],
        fill=colors.red.mix(percent=10),
        inner_sep=1 * units.ex,
    )

    loop = fig.add_loop("i", [1, 2, 3])
    ln = loop.add_node(x="\\i", y=0, label="L\\i", content="")
    loop.add_path([ln])

    d = fig.to_dict()

    # Check top-level keys
    assert d["type"] == "TikzFigure"
    assert d["ndim"] == 2
    assert d["label"] == "fig1"
    assert d["grid"] is True
    assert d["figsize"] == [8, 5]
    assert d["extra_packages"] == ["pgfplots"]
    assert d["named_styles"] == [
        {
            "name": "important line",
            "options": [
                {
                    "__tikzfigure_serialized_type__": "TikzStyle",
                    "style_spec": "very thick",
                }
            ],
            "kwargs": {
                "fill": {
                    "__tikzfigure_serialized_type__": "TikzColor",
                    "color_spec": "red!10",
                },
                "inner_sep": {
                    "__tikzfigure_serialized_type__": "TikzDimension",
                    "value": 1,
                    "unit": "ex",
                },
            },
        }
    ]
    assert len(d["variables"]) == 1
    assert d["variables"][0]["value"] == 42
    assert len(d["colors"]) == 1
    assert d["colors"][0]["name"] == "mycolor"
    assert d["colors"][0]["color_spec"] == "blue!30"

    # Round-trip
    fig2 = TikzFigure.from_dict(d)
    assert fig2.ndim == 2
    assert fig2._label == "fig1"
    assert fig2._grid is True
    assert fig2._figsize == (8, 5)
    assert fig2._extra_packages == ["pgfplots"]
    assert fig2.named_styles == [
        {
            "name": "important line",
            "options": [styles.very_thick],
            "kwargs": {
                "fill": colors.red.mix(percent=10),
                "inner_sep": 1 * units.ex,
            },
        }
    ]
    assert len(fig2._variables) == 1
    assert fig2._variables[0].value == 42
    assert len(fig2._colors) == 1
    assert fig2._colors[0][0] == "mycolor"

    # TikZ output should be identical
    assert fig.generate_tikz() == fig2.generate_tikz()


def test_tikzfigure_check_round_trips():
    fig = TikzFigure(figure_setup="scale=2")
    fig.add_style("important", options=[styles.very_thick])
    fig.add_node(x=0, y=0, label="A", content="A", fill=colors.red)
    fig.draw([(0, 0), (1, 0)], options=[styles.dashed], color=colors.blue)

    restored = fig._check()

    assert isinstance(restored, TikzFigure)
    assert restored.generate_tikz() == fig.generate_tikz()


def test_tikzfigure_add_package_deduplicates_and_trims():
    fig = TikzFigure()

    fig.add_package(" amsmath ")
    fig.add_package("amsmath")

    assert fig.extra_packages == ["amsmath"]
    assert "\\usepackage{amsmath}" in fig.generate_standalone()


def test_color_variable_coordinate():
    color = Color("blue!20")
    assert color.color_spec == "blue!20"

    var = Variable(label="v", value=3, comment="c")
    assert var.value == 3
    assert var.to_tikz() == "% Hi\n"

    coord2 = TikzCoordinate(1, 2)
    assert coord2.ndim == 2
    assert coord2.coordinate == (1, 2)
    assert coord2.to_tikz() == "({1}, {2})"

    coord2_tuple = TikzCoordinate((1, 2))
    assert coord2_tuple.ndim == 2
    assert coord2_tuple.coordinate == (1, 2)

    coord3 = TikzCoordinate(1, 2, 3)
    assert coord3.ndim == 3
    assert coord3.coordinate == (1, 2, 3)
    assert coord3.to_tikz() == "(axis cs:{1}, {2}, {3})"

    coord3_clone = TikzCoordinate(coord3)
    assert coord3_clone.ndim == 3
    assert coord3_clone.coordinate == (1, 2, 3)

    vector2 = TikzVector(3, 4)
    assert vector2.coordinate == (3, 4)
    assert vector2.norm() == 5.0


def test_point_and_vector_linear_algebra():
    vector_u = TikzVector(1, 2, 3)
    vector_v = TikzVector(4, 5, 6)

    assert vector_u + vector_v == TikzVector(5, 7, 9)
    assert vector_v - vector_u == TikzVector(3, 3, 3)
    assert 2 * vector_u == TikzVector(2, 4, 6)
    assert vector_u * 3 == TikzVector(3, 6, 9)
    assert vector_u.dot(vector_v) == 32.0
    assert (vector_u @ vector_v) == 32.0
    assert vector_u.cross(vector_v) == TikzVector(-3, 6, -3)

    point_p = TikzCoordinate(1, 2)
    point_q = TikzCoordinate(4, 6)
    diff = point_q - point_p

    assert diff == TikzVector(3, 4)
    assert point_p + TikzVector(3, 4) == point_q
    assert point_q - TikzVector(3, 4) == point_p
    assert point_p.vector_to(point_q) == TikzVector(3, 4)
    assert point_p.distance_to(point_q) == 5.0
    assert point_q.to_vector() == TikzVector(4, 6)

    with pytest.raises(TypeError, match="requires numeric coordinates"):
        TikzCoordinate("x", 2).distance_to(TikzCoordinate(1, 2))


def test_node_to_tikz_branches():
    node_no_pos = Node(label="n", content="X")
    assert "at" not in node_no_pos.to_tikz()

    node2d = Node(1, 2, label="n2", content="Y", options=["draw"], color="red")
    tikz2d = node2d.to_tikz()
    assert "at ({1}, {2})" in tikz2d
    assert "draw" in tikz2d
    assert "color=red" in tikz2d

    node3d = Node(1, 2, 3, label="n3", content="Z")
    assert "axis cs:{1}, {2}, {3}" in node3d.to_tikz()


def test_node_and_line_geometry_helpers():
    node_a = Node(1, 2, label="a")
    node_b = Node(4, 6, label="b")

    assert node_a.position == TikzCoordinate(1, 2)
    assert node_a.to_vector() == TikzVector(1, 2)
    assert node_a.vector_to(node_b) == TikzVector(3, 4)
    assert node_a.distance_to(node_b) == 5.0
    assert node_a.translate(TikzVector(3, 4)) == TikzCoordinate(4, 6)

    line = Line((1, 2), (4, 6), color="red")
    shifted = line.translate((1, 1))

    assert line.vector == TikzVector(3, 4)
    assert line.direction == TikzVector(3, 4)
    assert line.length == 5.0
    assert shifted.start == TikzCoordinate(2, 3)
    assert shifted.end == TikzCoordinate(5, 7)
    assert shifted.kwargs["color"] == "red"


def test_path_label_list_and_options():
    n1 = Node(0, 0, label="a")
    n2 = Node(1, 1, label="b")
    coord = TikzCoordinate(2, 2)

    path = TikzPath(nodes=[n1, n2, coord], options=["thick"], color="red")
    label_list = path.label_list
    assert "(a)" in label_list[0]
    assert "(b)" in label_list[1]
    assert "(2, 2)" == label_list[2]

    tikz = path.to_tikz()
    assert "thick" in tikz
    assert "color=red" in tikz

    centered = TikzPath(nodes=[n1], center=True)
    assert centered.label_list == ["(a.center)"]

    cycle = TikzPath(nodes=[n1, n2], cycle=True)
    assert "-- cycle" in cycle.to_tikz()


def test_plot3d_to_tikz():
    plot = Plot3D(
        x=[0, 1],
        y=[0, 1],
        z=[0, 1],
        options=["thick"],
        color="red",
        comment="plot",
    )
    tikz = plot.to_tikz()
    assert "\\addplot3" in tikz
    assert "coordinates" in tikz
    assert "% plot" in tikz


def test_loop_to_tikz_and_nested():
    loop = Loop("i", [1, 2], comment="outer")
    with loop as loop_l:
        loop_l.add_node(0, 0, label="n", content="A")
        loop_l.add_path([Node(0, 0, label="m")])
        inner = loop_l.add_loop("j", [3], comment="inner")
        inner.add_node(0, 0, label="n2")

    tikz = loop.to_tikz()
    assert "\\foreach \\i in {1,2}" in tikz
    assert "% outer" in tikz


def test_figure_parse_tikz_code():
    tikz_code = r"""
\begin{tikzpicture}
\pgfdeclarelayer{1}
\begin{pgfonlayer}{1}
\node[fill=red, draw=blue] (n1) at (0, 0) {A};
\end{pgfonlayer}{1}
\draw[thick] (n1) to (n1);
\end{tikzpicture}
"""
    fig = TikzFigure(tikz_code=tikz_code)
    fig2 = TikzFigure.from_tikz_code(tikz_code)
    output = fig.generate_tikz() + fig2.generate_tikz()
    assert "n1" in output
    assert "fill=red" in output


def test_figure_generate_tikz_features_and_ordering():
    fig = TikzFigure(
        ndim=3,
        grid=True,
        figure_setup="scale=0.5",
        label="fig:1",
        description="desc",
    )

    fig.add_variable("var", 2)
    fig.colorlet("mycolor", "red!50")

    n0 = Node(0, 0, label="n0", layer=0, content="A")
    n1 = Node(1, 1, label="n1", layer=1, content="B")

    fig.draw(
        [n0, n1], layer=1, comment="path", center=True, options=["thick"], verbose=True
    )
    fig.add(n0, layer=0)
    fig.add(n1, layer=1)
    fig.draw([(0, 0), (1, 1)], layer=0)
    fig.filldraw([n0, n1], layer=1)
    fig.plot3d([0, 1], [0, 1], [0, 1], layer=2, comment="plot3d")
    fig.add_node(x=2, y=2, label=None, content="C", options="right of=n0")
    fig.add_node(x=3, y=3, label="s", content="S")
    fig.draw(["s", "s"], layer=0)
    fig.add_raw("% raw", layer=0)

    loop = fig.add_loop("i", [1, 2], layer=0, comment="loop")
    loop.add_node(0, 0, label="ln0", content="L")

    unnamed = Node(label="")
    fig.add(unnamed, layer=0)
    assert unnamed.label.startswith("node")

    tikz = fig.generate_tikz()
    assert "\\begin{axis}" in tikz
    assert "\\pgfmathsetmacro{\\var}{2}" in tikz
    assert "\\colorlet{mycolor}{red!50}" in tikz
    assert "\\pgfsetlayers{0,1,2}" in tikz
    assert "\\begin{figure}" in tikz
    assert "\\label{fig:1}" in tikz

    pos_layer_0 = tikz.find("% Layer 0")
    pos_layer_1 = tikz.find("% Layer 1")
    assert 0 <= pos_layer_0 < pos_layer_1


def test_add_path_errors():
    fig = TikzFigure()
    with pytest.raises(ValueError, match="nodes parameter must be a list"):
        fig._add_path("not-a-list")

    with pytest.raises(NotImplementedError):
        fig._add_path([object()])


def test_generate_standalone():
    fig = TikzFigure()
    latex = fig.generate_standalone()
    assert "\\documentclass" in latex
    assert "\\begin{document}" in latex


def test_generate_standalone_colorlet_no_double_braces():
    """Colorlet specs passed without outer braces must NOT produce double braces.

    Double braces cause 'TeX capacity exceeded' on TeX Live 2026.
    The fix is to omit the outer {…} from the color_spec when calling
    fig.colorlet(), so the emitted line is:
        \\colorlet{name}{rgb,255:red,59;green,130;blue,246}
    and NOT:
        \\colorlet{name}{{rgb,255:red,59;green,130;blue,246}}
    """
    fig = TikzFigure()
    fig.colorlet("n1_fill", "rgb,255:red,59;green,130;blue,246")
    fig.add_node(
        x=0,
        y=0,
        label="n1",
        content="Test",
        fill="n1_fill",
        minimum_width="2cm",
        minimum_height="1cm",
    )
    standalone = fig.generate_standalone()
    # Must have single-brace colorlet (correct xcolor syntax)
    assert "\\colorlet{n1_fill}{rgb,255:red,59;green,130;blue,246}" in standalone
    # Must NOT have double-brace colorlet (causes TeX capacity exceeded)
    assert "\\colorlet{n1_fill}{{rgb,255:red,59;green,130;blue,246}}" not in standalone


@pytest.mark.network
def test_generate_standalone_compiles_via_latex_on_http():
    """Integration test: verify standalone LaTeX compiles via latex.ytotech.com API.

    Marked 'network' so it only runs when explicitly selected:
        pytest -m network
    """
    import json as _json
    import urllib.error
    import urllib.request

    fig = TikzFigure()
    fig.colorlet("n1_fill", "rgb,255:red,59;green,130;blue,246")
    fig.colorlet("n1_draw", "rgb,255:red,147;green,197;blue,253")
    fig.add_node(
        x=0,
        y=0,
        label="n1",
        content="Hello",
        fill="n1_fill",
        draw="n1_draw",
        minimum_width="2cm",
        minimum_height="1cm",
    )
    latex = fig.generate_standalone()

    payload = _json.dumps(
        {
            "compiler": "pdflatex",
            "resources": [{"main": True, "content": latex}],
        }
    ).encode()
    req = urllib.request.Request(
        "https://latex.ytotech.com/builds/sync",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            assert resp.status == 201, f"Expected 201, got {resp.status}"
            pdf = resp.read()
            assert pdf[:4] == b"%PDF", "Response is not a valid PDF"
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        pytest.fail(f"HTTP {e.code}: {body[:500]}")


def test_generate_tikz_single_layer_no_layers_block():
    fig = TikzFigure()
    fig.add_node(x=0, y=0, label="n", content="N")
    tikz = fig.generate_tikz(use_layers=True)
    assert "\\pgfdeclarelayer" not in tikz


def test_compile_pdf_success_and_failure(tmp_path, monkeypatch, capsys):
    fig = TikzFigure()
    output_pdf = tmp_path / "out.pdf"
    aux_file = tmp_path / "out.aux"
    log_file = tmp_path / "out.log"
    aux_file.write_text("")
    log_file.write_text("")

    def fake_run(*args, **kwargs):
        return 0

    monkeypatch.setattr(subprocess, "run", fake_run)
    fig.compile_pdf(filename=output_pdf, verbose=True)

    def raise_run(*args, **kwargs):
        raise subprocess.CalledProcessError(1, "pdflatex", stderr=b"boom")

    monkeypatch.setattr(subprocess, "run", raise_run)

    # Mock requests.post to simulate successful web compilation
    from unittest.mock import MagicMock

    import requests

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"%PDF-1.4\ndummy pdf"
    monkeypatch.setattr(requests, "post", lambda *args, **kwargs: mock_response)

    fig.compile_pdf(filename=output_pdf, verbose=False)
    # After fallback, the file should exist (created by web compiler)
    assert output_pdf.exists()


def test_savefig_tikz_pdf_png_and_invalid(tmp_path, monkeypatch):
    fig = TikzFigure()

    pdf_path = tmp_path / "out.pdf"
    tikz_path = tmp_path / "out.tikz"
    png_path = tmp_path / "out.png"

    def fake_compile_pdf(filename, verbose=False, use_web_compilation=False):
        with open(filename, "wb") as f:
            f.write(b"%PDF-1.4")

    monkeypatch.setattr(fig, "compile_pdf", fake_compile_pdf)

    fig.savefig(filename=str(pdf_path), verbose=True)
    assert pdf_path.exists()

    fig.savefig(filename=str(tikz_path), verbose=True)
    assert "\\begin{tikzpicture}" in tikz_path.read_text()

    class DummyPix:
        def save(self, filename):
            with open(filename, "wb") as f:
                f.write(b"png")

    class DummyPage:
        def get_pixmap(self, dpi, alpha=False):
            return DummyPix()

    class DummyDoc:
        def __getitem__(self, idx):
            return DummyPage()

        def close(self):
            return None

    def dummy_open(path):
        return DummyDoc()

    import tikzfigure.core.figure as figure_module

    # TODO: This test doesn't work because we are lazy-loading fitz,
    # so the monkeypatch doesn't take effect.
    # monkeypatch.setattr(figure_module.fitz, "open", dummy_open)
    # fig.savefig(filename=str(png_path), verbose=True)
    # assert png_path.exists()

    with pytest.raises(ValueError, match="Unsupported file format"):
        fig.savefig(filename=str(tmp_path / "out.txt"))


def test_savefig_check_warning_does_not_block_save(tmp_path, monkeypatch, caplog):
    fig = TikzFigure()
    tikz_path = tmp_path / "out.tikz"

    def fail_check(output_unit=None):
        raise AssertionError("broken check")

    monkeypatch.setattr(fig, "_check", fail_check)

    with caplog.at_level("WARNING"):
        fig.savefig(filename=str(tikz_path), check=True)

    assert tikz_path.exists()
    assert "TikzFigure._check() failed: broken check" in caplog.text


def test_compile_pdf_check_warning_does_not_block_compile(
    tmp_path, monkeypatch, caplog
):
    fig = TikzFigure()
    output_pdf = tmp_path / "checked.pdf"

    def fail_check(output_unit=None):
        raise AssertionError("broken check")

    def fake_web_compile(latex_document, filename, verbose=False):
        with open(filename, "wb") as f:
            f.write(b"%PDF-1.4")

    monkeypatch.setattr(fig, "_check", fail_check)
    monkeypatch.setattr(
        "tikzfigure.core.web_compiler.compile_with_latex_on_http",
        fake_web_compile,
    )

    with caplog.at_level("WARNING"):
        fig.compile_pdf(filename=output_pdf, use_web_compilation=True, check=True)

    assert output_pdf.exists()
    assert "TikzFigure._check() failed: broken check" in caplog.text


def test_show_suppressed(monkeypatch, capsys):
    fig = TikzFigure()
    monkeypatch.setenv("tikzfigure_NO_SHOW", "1")
    fig.show(verbose=True)
    captured = capsys.readouterr()
    assert "Display suppressed" in captured.out


def test_show_jupyter_branch(monkeypatch):
    fig = TikzFigure()
    monkeypatch.delenv("tikzfigure_NO_SHOW", raising=False)
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)

    class DummyShell:
        config = {"IPKernelApp": True}

    def fake_get_ipython():
        return DummyShell()

    class DummyImage:
        def __init__(self, filename, width=None, height=None):
            self.filename = filename

    def fake_display(_image):
        return None

    ipy_module = ModuleType("IPython")
    ipy_module.__path__ = []
    ipy_module.get_ipython = fake_get_ipython
    display_module = ModuleType("IPython.display")
    display_module.Image = DummyImage
    display_module.display = fake_display

    ipy_module.display = display_module
    monkeypatch.setitem(sys.modules, "IPython", ipy_module)
    monkeypatch.setitem(sys.modules, "IPython.display", display_module)
    monkeypatch.setattr(
        fig,
        "savefig",
        lambda filename, verbose=False, transparent=False, use_web_compilation=False: (
            None
        ),
    )

    fig.show(width=100, height=200, verbose=False)


def test_show_backends_and_errors(monkeypatch, capsys):
    fig = TikzFigure()
    monkeypatch.delenv("tikzfigure_NO_SHOW", raising=False)
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)

    ipy_module = ModuleType("IPython")
    ipy_module.__path__ = []
    ipy_module.get_ipython = lambda: None
    monkeypatch.setitem(sys.modules, "IPython", ipy_module)

    fake_matplotlib = ModuleType("matplotlib")
    fake_matplotlib.__path__ = []
    fake_image = ModuleType("matplotlib.image")
    fake_pyplot = ModuleType("matplotlib.pyplot")

    class FakeImageObj:
        shape = (100, 200, 3)

    class FakeAx:
        def imshow(self, _img):
            return None

        def axis(self, _):
            return None

    def fake_subplots(figsize=None):
        return object(), FakeAx()

    fake_image.imread = lambda _path: FakeImageObj()
    fake_pyplot.subplots = fake_subplots
    fake_pyplot.tight_layout = lambda pad=0: None
    fake_pyplot.show = lambda: None

    fake_matplotlib.image = fake_image
    fake_matplotlib.pyplot = fake_pyplot
    monkeypatch.setitem(sys.modules, "matplotlib", fake_matplotlib)
    monkeypatch.setitem(sys.modules, "matplotlib.image", fake_image)
    monkeypatch.setitem(sys.modules, "matplotlib.pyplot", fake_pyplot)
    monkeypatch.setattr(
        fig,
        "savefig",
        lambda filename,
        dpi=300,
        verbose=False,
        transparent=False,
        use_web_compilation=False: (None),
    )

    fig._show_matplotlib(dpi=72, verbose=True)

    monkeypatch.setattr(platform, "system", lambda: "Linux")
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: 0)
    fig._show_system(dpi=72, verbose=False)

    monkeypatch.setattr(platform, "system", lambda: "Darwin")
    fig._show_system(dpi=72, verbose=False)

    monkeypatch.setattr(platform, "system", lambda: "Windows")
    monkeypatch.setattr(os, "startfile", lambda *_: None, raising=False)
    fig._show_system(dpi=72, verbose=False)

    monkeypatch.setattr(platform, "system", lambda: "Other")
    fig._show_system(dpi=72, verbose=False)

    def raise_savefig(*args, **kwargs):
        raise RuntimeError("fail")

    monkeypatch.setattr(fig, "savefig", raise_savefig)
    fig._show_system(dpi=72, verbose=False)
    captured = capsys.readouterr()
    assert "Could not open figure automatically" in captured.out

    fake_pil = ModuleType("PIL")
    fake_pil.__path__ = []
    fake_pil_image = ModuleType("PIL.Image")

    class FakePILImage:
        def show(self):
            return None

    fake_pil_image.open = lambda _path: FakePILImage()
    fake_pil.Image = fake_pil_image
    monkeypatch.setitem(sys.modules, "PIL", fake_pil)
    monkeypatch.setitem(sys.modules, "PIL.Image", fake_pil_image)
    monkeypatch.setattr(
        fig,
        "savefig",
        lambda filename,
        dpi=300,
        verbose=False,
        transparent=False,
        use_web_compilation=False: (None),
    )

    fig._show_pillow(dpi=72, verbose=False)

    def import_fail(name, *args, **kwargs):
        if name.startswith("PIL"):
            raise ImportError("no pil")
        return original_import(name, *args, **kwargs)

    original_import = builtins.__import__
    monkeypatch.setattr(builtins, "__import__", import_fail)
    with pytest.raises(ImportError, match="Pillow is required"):
        fig._show_pillow(dpi=72, verbose=False)

    def import_fail_matplotlib(name, *args, **kwargs):
        if name.startswith("matplotlib"):
            raise ImportError("no mpl")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", import_fail_matplotlib)
    with pytest.raises(ImportError, match="matplotlib is required"):
        fig._show_matplotlib(dpi=72, verbose=False)

    called = {"matplotlib": False, "system": False, "pillow": False}

    monkeypatch.setattr(
        fig, "_show_matplotlib", lambda **_: called.__setitem__("matplotlib", True)
    )
    monkeypatch.setattr(
        fig, "_show_system", lambda **_: called.__setitem__("system", True)
    )
    monkeypatch.setattr(
        fig, "_show_pillow", lambda **_: called.__setitem__("pillow", True)
    )

    fig.show(backend="matplotlib")
    fig.show(backend="system")
    fig.show(backend="pillow")

    assert all(called.values())

    with pytest.raises(ValueError, match="Unknown backend"):
        fig.show(backend="unknown")


def test_show_check_warning_does_not_block_backend(monkeypatch, caplog):
    fig = TikzFigure()
    monkeypatch.delenv("tikzfigure_NO_SHOW", raising=False)
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)

    ipy_module = ModuleType("IPython")
    ipy_module.__path__ = []
    ipy_module.get_ipython = lambda: None
    monkeypatch.setitem(sys.modules, "IPython", ipy_module)

    called = {"matplotlib": False}

    def fail_check(output_unit=None):
        raise AssertionError("broken check")

    monkeypatch.setattr(fig, "_check", fail_check)
    monkeypatch.setattr(
        fig, "_show_matplotlib", lambda **_: called.__setitem__("matplotlib", True)
    )

    with caplog.at_level("WARNING"):
        fig.show(backend="matplotlib", check=True)

    assert called["matplotlib"] is True
    assert "TikzFigure._check() failed: broken check" in caplog.text


def test_add_tabs_custom():
    fig = TikzFigure()
    script = """\\begin{tikzpicture}
start \\foreach
line
end \\foreach
\\end{tikzpicture}"""
    result = fig._add_tabs(script)
    assert "\\begin{tikzpicture}" in result


def test_ipython_magic_error_paths(monkeypatch, capsys):
    pytest.importorskip("IPython")
    from tikzfigure.core.ipython import TikzMagics

    magics = TikzMagics(shell=object())
    magics.tikz("--bad", "\\begin{tikzpicture}\\end{tikzpicture}")
    assert "Error parsing arguments" in capsys.readouterr().out

    class DummyFig:
        def savefig(self, filename, verbose=False):
            return None

        def show(self, width=None, height=None, verbose=False):
            return None

    monkeypatch.setattr(
        "tikzfigure.core.ipython.TikzFigure.from_tikz_code",
        lambda _cell: DummyFig(),
    )
    magics.tikz("-s out.pdf -v", "\\begin{tikzpicture}\\end{tikzpicture}")
    assert "Saved to" in capsys.readouterr().out

    def raise_from_code(_cell):
        raise ValueError("bad")

    monkeypatch.setattr(
        "tikzfigure.core.ipython.TikzFigure.from_tikz_code", raise_from_code
    )
    magics.tikz("-v", "bad")
    captured = capsys.readouterr().out
    assert "Error: bad" in captured

    magics.tikz_load("--bad")
    assert "Error parsing arguments" in capsys.readouterr().out

    magics.tikz_load("missing_file.tikz")
    assert "not found" in capsys.readouterr().out


def test_ipython_extension_hooks():
    pytest.importorskip("IPython")
    from tikzfigure.core.ipython import load_ipython_extension, unload_ipython_extension

    class DummyIP:
        def __init__(self):
            self.registered = False

        def register_magics(self, _magics):
            self.registered = True

    dummy = DummyIP()
    load_ipython_extension(dummy)
    assert dummy.registered is True
    unload_ipython_extension(dummy)


def test_execute_main_blocks(monkeypatch):
    test_dir = os.path.dirname(__file__)

    runpy.run_path(os.path.join(test_dir, "test_app.py"), run_name="__main__")

    monkeypatch.setattr(pytest, "main", lambda *args, **kwargs: 0)
    runpy.run_path(os.path.join(test_dir, "test_layer.py"), run_name="__main__")

    runpy.run_path(
        os.path.join(test_dir, "test_tikz_generation.py"), run_name="__main__"
    )

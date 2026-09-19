import pytest

import tikzfigure as tf
from tikzfigure import pyplot
from tikzfigure.core.figure import TikzFigure


@pytest.fixture(autouse=True)
def _fresh_current_figure():
    """Give every test its own current figure and clean up afterwards."""
    pyplot.close()
    yield
    pyplot.close()


def test_gcf_creates_a_figure_lazily():
    """gcf() creates a figure on first use and returns the same one after."""
    assert pyplot._current_figure is None
    fig = tf.gcf()
    assert isinstance(fig, TikzFigure)
    assert tf.gcf() is fig


def test_draw_without_initializing_a_figure():
    """The module-level draw() works without creating a TikzFigure first."""
    path = tf.draw([(0, 0), (1, 1), (2, 0)])
    tikz = tf.generate_tikz()
    assert path in tf.gcf().layers.get_paths()
    assert "(0, 0) to (1, 1) to (2, 0)" in tikz


def test_shapes_go_to_the_current_figure():
    """Shape helpers add to the implicit current figure."""
    tf.circle((0, 0), radius=1)
    tf.rectangle((0, 0), (2, 1))
    tikz = tf.generate_tikz()
    assert "circle" in tikz
    assert "rectangle" in tikz


def test_figure_switches_the_current_figure():
    """figure() starts a new figure, leaving the previous one untouched."""
    first = tf.gcf()
    tf.draw([(0, 0), (1, 1)])

    second = tf.figure()
    assert second is not first
    assert tf.gcf() is second
    assert "(0, 0) to (1, 1)" not in tf.generate_tikz()
    assert "(0, 0) to (1, 1)" in first.generate_tikz()


def test_scf_sets_an_existing_figure_as_current():
    """scf() lets an explicitly created figure receive module-level calls."""
    fig = TikzFigure()
    assert tf.scf(fig) is fig
    tf.draw([(0, 0), (1, 1)])
    assert "(0, 0) to (1, 1)" in fig.generate_tikz()


def test_scf_rejects_non_figures():
    """scf() only accepts TikzFigure instances."""
    with pytest.raises(TypeError):
        tf.scf("not a figure")


def test_clf_replaces_the_current_figure():
    """clf() drops the drawn content by installing a fresh figure."""
    tf.draw([(0, 0), (1, 1)])
    old = tf.gcf()
    new = tf.clf()
    assert new is not old
    assert tf.gcf() is new
    assert "(0, 0) to (1, 1)" not in tf.generate_tikz()


def test_close_forgets_the_current_figure():
    """After close() the next call starts from an empty figure."""
    tf.draw([(0, 0), (1, 1)])
    first = tf.gcf()
    tf.close()
    assert pyplot._current_figure is None
    assert tf.gcf() is not first


def test_figure_forwards_constructor_arguments():
    """figure() passes its arguments through to TikzFigure."""
    fig = tf.figure(ndim=3, figsize=(4, 3))
    assert fig.ndim == 3
    assert fig._figsize == (4, 3)


def test_show_is_available_at_module_level():
    """show() runs on the current figure (suppressed under pytest)."""
    tf.draw([(0, 0), (1, 1)])
    tf.show()


def test_savefig_writes_tikz(tmp_path):
    """savefig() saves the current figure."""
    tf.draw([(0, 0), (1, 1)])
    out = tmp_path / "figure.tikz"
    tf.savefig(out)
    assert "(0, 0) to (1, 1)" in out.read_text()


def test_short_aliases_match_the_figure_aliases():
    """The module-level short aliases point at the same helpers as on TikzFigure."""
    aliases = {
        "coordinate": "add_coordinate",
        "function": "declare_function",
        "gantt": "add_gantt_chart",
        "loop": "add_loop",
        "node": "add_node",
        "plot": "add_plot",
        "raw": "add_raw",
        "scope": "add_scope",
        "spy": "add_spy",
        "subfigure": "add_subfigure",
        "variable": "add_variable",
    }
    for alias, target in aliases.items():
        assert getattr(tf, alias) is getattr(tf, target), alias
        assert getattr(TikzFigure, alias) is getattr(TikzFigure, target), alias


def test_loop_container_works_at_module_level():
    """Containers such as loops can be used without an explicit figure."""
    tf.variable("R", 1.0)
    with tf.loop("angle", range(0, 360, 90)) as loop:
        loop.node(x=r"\R*cos(\angle)", y=r"\R*sin(\angle)", shape="circle")

    tikz = tf.generate_tikz()
    assert "\\foreach" in tikz
    assert "\\R*cos(\\angle)" in tikz


def test_exported_names_are_importable():
    """Every name in pyplot.__all__ is re-exported from the package."""
    for name in pyplot.__all__:
        assert hasattr(tf, name), name
        assert name in tf.__all__

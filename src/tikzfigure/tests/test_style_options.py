"""Tests for the shared style options of the shape helpers.

The shape helpers declare their style parameters explicitly but collect them
with :func:`~tikzfigure.core.style_options.collect_style`, which reads
``locals()``. These tests pin that contract down: every style parameter a
helper declares has to reach the generated TikZ, and nothing else may.
"""

from __future__ import annotations

import inspect

import pytest

from tikzfigure import TikzFigure
from tikzfigure.core.style_options import (
    STYLE_FIELDS,
    StyleOptions,
    collect_style,
)

#: The shape helpers that build their options with ``collect_style``, with the
#: positional arguments needed to call them.
SHAPE_HELPERS = {
    "arc": ((0, 0), 0, 90, 1.0),
    "circle": ((0, 0), 1.0),
    "rectangle": ((0, 0), (1, 1)),
    "ellipse": ((0, 0), 1.0, 2.0),
    "grid": ((0, 0), (1, 1)),
    "parabola": ((0, 0), (2, 0), (1, 1)),
    "line": ((0, 0), (1, 1)),
    "polygon": ((0, 0), 1.0, 5),
    "triangle": ((0, 0), 1.0),
    "square": ((0, 0), 1.0),
}

#: A plausible value per style option, used to check it survives the round trip.
SAMPLE_VALUES = {
    "color": "red",
    "fill": "blue!50",
    "draw": "green",
    "text": "black",
    "opacity": 0.5,
    "draw_opacity": 0.6,
    "fill_opacity": 0.7,
    "text_opacity": 0.8,
    "line_width": "2pt",
    "line_cap": "round",
    "line_join": "bevel",
    "miter_limit": 3.0,
    "dash_pattern": "on 2pt off 3pt",
    "dash_phase": "1pt",
    "rounded_corners": "3pt",
    "rotate": 45,
    "xshift": "1cm",
    "yshift": "2cm",
    "scale": 2.0,
    "xscale": 1.5,
    "yscale": 0.5,
}


def _style_params(method_name: str) -> list[str]:
    """The style options that *method_name* actually declares."""
    signature = inspect.signature(getattr(TikzFigure, method_name))
    return [name for name in STYLE_FIELDS if name in signature.parameters]


def test_sample_values_cover_every_style_field():
    assert set(SAMPLE_VALUES) == set(STYLE_FIELDS)


def test_style_fields_match_dataclass():
    """STYLE_FIELDS is derived from StyleOptions, so the two cannot drift."""
    assert set(STYLE_FIELDS) == set(StyleOptions.__dataclass_fields__)


@pytest.mark.parametrize("method_name", sorted(SHAPE_HELPERS))
def test_helper_declares_style_options(method_name):
    """Every shape helper offers at least the core styling options."""
    declared = _style_params(method_name)
    assert {"color", "line_width", "opacity"} <= set(declared)


@pytest.mark.parametrize("method_name", sorted(SHAPE_HELPERS))
def test_every_declared_style_option_reaches_the_tikz(method_name):
    """Each style option a helper declares is emitted into the TikZ output."""
    declared = _style_params(method_name)
    kwargs = {name: SAMPLE_VALUES[name] for name in declared}

    fig = TikzFigure()
    getattr(fig, method_name)(*SHAPE_HELPERS[method_name], **kwargs)
    tikz = fig.generate_tikz()

    for name, value in kwargs.items():
        option = f"{name.replace('_', ' ')}={value}"
        assert option in tikz, f"{method_name}: {name} was dropped"


@pytest.mark.parametrize("method_name", sorted(SHAPE_HELPERS))
def test_unset_style_options_are_dropped(method_name):
    """Options the caller omits do not show up in the generated TikZ."""
    fig = TikzFigure()
    getattr(fig, method_name)(*SHAPE_HELPERS[method_name], color="red")
    tikz = fig.generate_tikz()

    assert "color=red" in tikz
    for name in _style_params(method_name):
        if name != "color":
            assert f"{name.replace('_', ' ')}=" not in tikz


@pytest.mark.parametrize("method_name", sorted(SHAPE_HELPERS))
def test_kwargs_catch_all_still_works(method_name):
    """Unlisted TikZ options still pass through the ``**kwargs`` catch-all."""
    fig = TikzFigure()
    getattr(fig, method_name)(*SHAPE_HELPERS[method_name], some_unlisted_option="value")
    assert "some unlisted option=value" in fig.generate_tikz()


class TestCollectStyle:
    def test_drops_none_values(self):
        scope = {"color": "red", "fill": None, "opacity": 0.5}
        assert collect_style(scope) == {"color": "red", "opacity": 0.5}

    def test_ignores_non_style_names(self):
        scope = {"color": "red", "self": object(), "layer": 3, "verbose": True}
        assert collect_style(scope) == {"color": "red"}

    def test_falsy_but_set_values_are_kept(self):
        """0 and "" are real TikZ values, not "unset"."""
        assert collect_style({"opacity": 0, "rotate": 0.0}) == {
            "opacity": 0,
            "rotate": 0.0,
        }

    def test_extra_wins_over_scope(self):
        assert collect_style({"color": "red"}, {"color": "blue"}) == {"color": "blue"}

    def test_extra_keeps_none(self):
        """An explicitly passed ``**kwargs`` value is kept even when None."""
        assert collect_style({}, {"draw": None}) == {"draw": None}

    def test_canonical_ordering(self):
        """Options come out in STYLE_FIELDS order, not caller order."""
        scope = {"yscale": 1, "color": "red", "opacity": 0.5}
        assert list(collect_style(scope)) == ["color", "opacity", "yscale"]

    def test_empty_scope(self):
        assert collect_style({}) == {}


class TestStyleOptions:
    def test_as_kwargs_drops_unset(self):
        assert StyleOptions(color="red", line_width="2pt").as_kwargs() == {
            "color": "red",
            "line_width": "2pt",
        }

    def test_default_is_empty(self):
        assert StyleOptions().as_kwargs() == {}

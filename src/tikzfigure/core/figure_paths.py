from __future__ import annotations

from typing import Any

from tikzfigure.arrows import ArrowInput
from tikzfigure.colors import ColorInput
from tikzfigure.core.path import TikzPath
from tikzfigure.core.path_builder import NodePathBuilder, SegmentOption
from tikzfigure.core.types import (
    _Decoration,
    _LineCap,
    _LineJoin,
    _Mark,
    _Pattern,
    _Shading,
)
from tikzfigure.options import OptionInput, normalize_options


class FigurePathMixin:
    def _coerce_path_input(
        self,
        nodes: list | NodePathBuilder,
        segment_options: list[SegmentOption] | None = None,
    ) -> tuple[list[Any], list[SegmentOption] | None]:
        raise NotImplementedError

    def _add_path(self, *args: Any, **kwargs: Any) -> TikzPath:
        raise NotImplementedError

    def filldraw(
        self,
        nodes: list | NodePathBuilder,
        layer: int = 0,
        comment: str | None = None,
        center: bool = False,
        verbose: bool = False,
        options: OptionInput | None = None,
        cycle: bool = False,
        segment_options: list[SegmentOption] | None = None,
        color: ColorInput | None = None,
        fill: ColorInput | None = None,
        draw: ColorInput | None = None,
        text: ColorInput | None = None,
        opacity: float | None = None,
        draw_opacity: float | None = None,
        fill_opacity: float | None = None,
        text_opacity: float | None = None,
        line_width: str | None = None,
        line_cap: _LineCap = None,
        line_join: _LineJoin = None,
        miter_limit: float | None = None,
        dash_pattern: str | None = None,
        dash_phase: str | None = None,
        double: ColorInput | None = None,
        double_distance: str | None = None,
        rounded_corners: str | None = None,
        rotate: float | None = None,
        xshift: str | None = None,
        yshift: str | None = None,
        scale: float | None = None,
        xscale: float | None = None,
        yscale: float | None = None,
        xslant: float | None = None,
        yslant: float | None = None,
        bend_left: float | None = None,
        bend_right: float | None = None,
        in_angle: float | None = None,
        out_angle: float | None = None,
        looseness: float | None = None,
        in_looseness: float | None = None,
        out_looseness: float | None = None,
        min_distance: str | None = None,
        max_distance: str | None = None,
        tension: float | None = None,
        pattern: _Pattern = None,
        pattern_color: ColorInput | None = None,
        shading: _Shading = None,
        shading_angle: float | None = None,
        left_color: ColorInput | None = None,
        right_color: ColorInput | None = None,
        top_color: ColorInput | None = None,
        bottom_color: ColorInput | None = None,
        middle_color: ColorInput | None = None,
        inner_color: ColorInput | None = None,
        outer_color: ColorInput | None = None,
        ball_color: ColorInput | None = None,
        decoration: _Decoration = None,
        step: str | None = None,
        pos: float | None = None,
        arrows: ArrowInput | None = None,
        font: str | None = None,
        name_path: str | None = None,
        to_path: str | None = None,
        domain: str | None = None,
        samples: int | None = None,
        mark: _Mark = None,
        mark_size: str | None = None,
        **kwargs: Any,
    ) -> TikzPath:
        """Add a filled path connecting multiple nodes with ``\\filldraw``."""
        nodes, segment_options = self._coerce_path_input(nodes, segment_options)
        normalized_options = normalize_options(options)
        if arrows is not None:
            normalized_options.append(arrows)
        _params = locals().copy()
        _non_tikz = {
            "self",
            "nodes",
            "layer",
            "comment",
            "center",
            "verbose",
            "options",
            "cycle",
            "segment_options",
            "arrows",
            "normalized_options",
            "kwargs",
            "in_angle",
            "out_angle",
            "__class__",
        }
        tikz_kwargs = dict(kwargs)
        tikz_kwargs.update(
            {k: v for k, v in _params.items() if k not in _non_tikz and v is not None}
        )
        if in_angle is not None:
            tikz_kwargs["in"] = in_angle
        if out_angle is not None:
            tikz_kwargs["out"] = out_angle

        return self._add_path(
            nodes=nodes,
            layer=layer,
            comment=comment,
            center=center,
            tikz_command="filldraw",
            verbose=verbose,
            options=normalized_options,
            cycle=cycle,
            segment_options=segment_options,
            **tikz_kwargs,
        )

    def draw(
        self,
        nodes: list | NodePathBuilder,
        layer: int = 0,
        comment: str | None = None,
        center: bool = False,
        verbose: bool = False,
        options: OptionInput | None = None,
        cycle: bool = False,
        segment_options: list[SegmentOption] | None = None,
        color: ColorInput | None = None,
        fill: ColorInput | None = None,
        draw: ColorInput | None = None,
        text: ColorInput | None = None,
        opacity: float | None = None,
        draw_opacity: float | None = None,
        fill_opacity: float | None = None,
        text_opacity: float | None = None,
        line_width: str | int | float | None = None,
        line_cap: _LineCap = None,
        line_join: _LineJoin = None,
        miter_limit: float | None = None,
        dash_pattern: str | None = None,
        dash_phase: str | None = None,
        double: ColorInput | None = None,
        double_distance: str | None = None,
        rounded_corners: str | None = None,
        rotate: float | None = None,
        xshift: str | None = None,
        yshift: str | None = None,
        scale: float | None = None,
        xscale: float | None = None,
        yscale: float | None = None,
        xslant: float | None = None,
        yslant: float | None = None,
        bend_left: float | None = None,
        bend_right: float | None = None,
        in_angle: float | None = None,
        out_angle: float | None = None,
        looseness: float | None = None,
        in_looseness: float | None = None,
        out_looseness: float | None = None,
        min_distance: str | None = None,
        max_distance: str | None = None,
        tension: float | None = None,
        pattern: _Pattern = None,
        pattern_color: ColorInput | None = None,
        shading: _Shading = None,
        shading_angle: float | None = None,
        left_color: ColorInput | None = None,
        right_color: ColorInput | None = None,
        top_color: ColorInput | None = None,
        bottom_color: ColorInput | None = None,
        middle_color: ColorInput | None = None,
        inner_color: ColorInput | None = None,
        outer_color: ColorInput | None = None,
        ball_color: ColorInput | None = None,
        decoration: _Decoration = None,
        step: str | None = None,
        pos: float | None = None,
        arrows: ArrowInput | None = None,
        font: str | None = None,
        name_path: str | None = None,
        to_path: str | None = None,
        domain: str | None = None,
        samples: int | None = None,
        mark: _Mark = None,
        mark_size: str | None = None,
        **kwargs: Any,
    ) -> TikzPath:
        """Add a path connecting multiple nodes with ``\\draw``."""
        nodes, segment_options = self._coerce_path_input(nodes, segment_options)
        normalized_options = normalize_options(options)
        if arrows is not None:
            normalized_options.append(arrows)
        _params = locals().copy()
        _non_tikz = {
            "self",
            "nodes",
            "layer",
            "comment",
            "center",
            "verbose",
            "options",
            "cycle",
            "segment_options",
            "arrows",
            "normalized_options",
            "kwargs",
            "in_angle",
            "out_angle",
            "__class__",
        }
        tikz_kwargs = dict(kwargs)
        tikz_kwargs.update(
            {k: v for k, v in _params.items() if k not in _non_tikz and v is not None}
        )
        if in_angle is not None:
            tikz_kwargs["in"] = in_angle
        if out_angle is not None:
            tikz_kwargs["out"] = out_angle

        return self._add_path(
            nodes=nodes,
            layer=layer,
            comment=comment,
            center=center,
            tikz_command="draw",
            verbose=verbose,
            options=normalized_options,
            cycle=cycle,
            segment_options=segment_options,
            **tikz_kwargs,
        )

    def fill(
        self,
        nodes: list,
        layer: int = 0,
        comment: str | None = None,
        center: bool = False,
        verbose: bool = False,
        options: OptionInput | None = None,
        cycle: bool = False,
        segment_options: list[SegmentOption] | None = None,
        fill: ColorInput | None = None,
        fill_opacity: float | None = None,
        opacity: float | None = None,
        pattern: _Pattern = None,
        pattern_color: ColorInput | None = None,
        shading: _Shading = None,
        shading_angle: float | None = None,
        left_color: ColorInput | None = None,
        right_color: ColorInput | None = None,
        top_color: ColorInput | None = None,
        bottom_color: ColorInput | None = None,
        middle_color: ColorInput | None = None,
        inner_color: ColorInput | None = None,
        outer_color: ColorInput | None = None,
        ball_color: ColorInput | None = None,
        rotate: float | None = None,
        xshift: str | None = None,
        yshift: str | None = None,
        scale: float | None = None,
        xscale: float | None = None,
        yscale: float | None = None,
        even_odd_rule: bool = False,
        **kwargs: Any,
    ) -> TikzPath:
        """Fill a closed path with no stroke using ``\\fill``."""
        _params = locals().copy()
        _non_tikz = {
            "self",
            "nodes",
            "layer",
            "comment",
            "center",
            "verbose",
            "options",
            "cycle",
            "segment_options",
            "even_odd_rule",
            "kwargs",
            "__class__",
        }
        tikz_kwargs = dict(kwargs)
        tikz_kwargs.update(
            {k: v for k, v in _params.items() if k not in _non_tikz and v is not None}
        )
        options = normalize_options(options)
        if even_odd_rule:
            options = list(options) + ["even odd rule"]
        return self._add_path(
            nodes=nodes,
            layer=layer,
            comment=comment,
            center=center,
            tikz_command="fill",
            verbose=verbose,
            options=options,
            cycle=cycle,
            segment_options=segment_options,
            **tikz_kwargs,
        )

    def clip(
        self,
        nodes: list,
        layer: int = 0,
        comment: str | None = None,
        center: bool = False,
        verbose: bool = False,
        options: OptionInput | None = None,
        cycle: bool = False,
        segment_options: list[SegmentOption] | None = None,
        rotate: float | None = None,
        xshift: str | None = None,
        yshift: str | None = None,
        scale: float | None = None,
        rounded_corners: str | None = None,
        **kwargs: Any,
    ) -> TikzPath:
        """Add a clipping path using ``\\clip``."""
        _params = locals().copy()
        _non_tikz = {
            "self",
            "nodes",
            "layer",
            "comment",
            "center",
            "verbose",
            "options",
            "cycle",
            "segment_options",
            "kwargs",
            "__class__",
        }
        tikz_kwargs = dict(kwargs)
        tikz_kwargs.update(
            {k: v for k, v in _params.items() if k not in _non_tikz and v is not None}
        )
        return self._add_path(
            nodes=nodes,
            layer=layer,
            comment=comment,
            center=center,
            tikz_command="clip",
            verbose=verbose,
            options=options,
            cycle=cycle,
            segment_options=segment_options,
            **tikz_kwargs,
        )

    def path(
        self,
        nodes: list,
        layer: int = 0,
        comment: str | None = None,
        center: bool = False,
        verbose: bool = False,
        options: OptionInput | None = None,
        cycle: bool = False,
        segment_options: list[SegmentOption] | None = None,
        name_path: str | None = None,
        pos: float | None = None,
        rotate: float | None = None,
        xshift: str | None = None,
        yshift: str | None = None,
        scale: float | None = None,
        **kwargs: Any,
    ) -> TikzPath:
        """Add an invisible path using ``\\path``."""
        _params = locals().copy()
        _non_tikz = {
            "self",
            "nodes",
            "layer",
            "comment",
            "center",
            "verbose",
            "options",
            "cycle",
            "segment_options",
            "kwargs",
            "__class__",
        }
        tikz_kwargs = dict(kwargs)
        tikz_kwargs.update(
            {k: v for k, v in _params.items() if k not in _non_tikz and v is not None}
        )
        return self._add_path(
            nodes=nodes,
            layer=layer,
            comment=comment,
            center=center,
            tikz_command="path",
            verbose=verbose,
            options=options,
            cycle=cycle,
            segment_options=segment_options,
            **tikz_kwargs,
        )

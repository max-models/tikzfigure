from __future__ import annotations

from collections.abc import Mapping
from typing import Any

_SERIALIZED_TYPE_KEY = "__tikzfigure_serialized_type__"


def serialize_tikz_value(value: object) -> object:
    """Recursively serialize rich public wrapper values to plain structures."""
    from tikzfigure.arrows import TikzArrow
    from tikzfigure.colors import TikzColor
    from tikzfigure.decorations import TikzDecoration
    from tikzfigure.marks import TikzMark
    from tikzfigure.patterns import TikzPattern
    from tikzfigure.shapes import TikzShape
    from tikzfigure.styles import TikzStyle
    from tikzfigure.units import TikzDimension

    if isinstance(value, TikzArrow):
        return {
            _SERIALIZED_TYPE_KEY: "TikzArrow",
            "arrow_spec": value.arrow_spec,
        }
    if isinstance(value, TikzColor):
        return {
            _SERIALIZED_TYPE_KEY: "TikzColor",
            "color_spec": value.color_spec,
        }
    if isinstance(value, TikzPattern):
        return {
            _SERIALIZED_TYPE_KEY: "TikzPattern",
            "pattern_spec": value.pattern_spec,
        }
    if isinstance(value, TikzDecoration):
        return {
            _SERIALIZED_TYPE_KEY: "TikzDecoration",
            "decoration_spec": value.decoration_spec,
        }
    if isinstance(value, TikzMark):
        return {
            _SERIALIZED_TYPE_KEY: "TikzMark",
            "mark_spec": value.mark_spec,
        }
    if isinstance(value, TikzShape):
        return {
            _SERIALIZED_TYPE_KEY: "TikzShape",
            "shape_spec": value.shape_spec,
        }
    if isinstance(value, TikzStyle):
        return {
            _SERIALIZED_TYPE_KEY: "TikzStyle",
            "style_spec": value.style_spec,
        }
    if isinstance(value, TikzDimension):
        return {
            _SERIALIZED_TYPE_KEY: "TikzDimension",
            "value": value.value,
            "unit": value.unit,
        }
    if isinstance(value, list):
        return [serialize_tikz_value(item) for item in value]
    if isinstance(value, tuple):
        return tuple(serialize_tikz_value(item) for item in value)
    if isinstance(value, Mapping):
        return {key: serialize_tikz_value(item) for key, item in value.items()}
    return value


def deserialize_tikz_value(value: object) -> object:
    """Recursively restore rich public wrapper values from serialized structures."""
    from tikzfigure.arrows import TikzArrow
    from tikzfigure.colors import TikzColor
    from tikzfigure.decorations import TikzDecoration
    from tikzfigure.marks import TikzMark
    from tikzfigure.patterns import TikzPattern
    from tikzfigure.shapes import TikzShape
    from tikzfigure.styles import TikzStyle
    from tikzfigure.units import TikzDimension

    if isinstance(value, list):
        return [deserialize_tikz_value(item) for item in value]
    if isinstance(value, tuple):
        return tuple(deserialize_tikz_value(item) for item in value)
    if isinstance(value, Mapping):
        serialized_type = value.get(_SERIALIZED_TYPE_KEY)
        if serialized_type == "TikzArrow":
            return TikzArrow(str(value["arrow_spec"]))
        if serialized_type == "TikzColor":
            return TikzColor(str(value["color_spec"]))
        if serialized_type == "TikzPattern":
            return TikzPattern(str(value["pattern_spec"]))
        if serialized_type == "TikzDecoration":
            return TikzDecoration(str(value["decoration_spec"]))
        if serialized_type == "TikzMark":
            return TikzMark(str(value["mark_spec"]))
        if serialized_type == "TikzShape":
            return TikzShape(str(value["shape_spec"]))
        if serialized_type == "TikzStyle":
            return TikzStyle(str(value["style_spec"]))
        if serialized_type == "TikzDimension":
            return TikzDimension(
                value=value["value"],
                unit=str(value["unit"]),
            )
        if serialized_type is not None:
            raise ValueError(f"Unknown serialized TikZ value type: {serialized_type!r}")
        return {key: deserialize_tikz_value(item) for key, item in value.items()}
    return value


__all__ = ["deserialize_tikz_value", "serialize_tikz_value"]

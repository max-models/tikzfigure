"""Structured helpers for TikZ's ``spy`` library."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeAlias

from tikzfigure.core.base import TikzObject
from tikzfigure.core.coordinate import (
    Coordinate,
    CoordinateTuple2D,
    CoordinateTuple3D,
    TikzCoordinate,
)
from tikzfigure.core.node import Node
from tikzfigure.core.serialization import deserialize_tikz_value, serialize_tikz_value
from tikzfigure.options import OptionInput, normalize_options

SpyTargetInput: TypeAlias = (
    Node | Coordinate | TikzCoordinate | CoordinateTuple2D | CoordinateTuple3D | str
)
SpyScopeMode: TypeAlias = Literal["scope", "outlines", "overlays"]


def _format_tikz_value(value: object, output_unit: str | None = None) -> str:
    from tikzfigure.units import TikzDimension

    if isinstance(value, TikzDimension):
        return str(value.to(output_unit)) if output_unit is not None else str(value)
    return str(value)


def _format_option_mapping(
    options: OptionInput | None,
    kwargs: Mapping[str, Any],
    output_unit: str | None = None,
) -> str:
    parts = [str(option) for option in normalize_options(options)]
    for key, value in kwargs.items():
        if value is True:
            parts.append(key.replace("_", " "))
        else:
            parts.append(
                f"{key.replace('_', ' ')}={_format_tikz_value(value, output_unit)}"
            )
    return ", ".join(parts)


def _wrap_braces(value: str) -> str:
    stripped = value.strip()
    if stripped.startswith("{") and stripped.endswith("}"):
        return stripped
    return f"{{{value}}}"


def _serialize_spy_target(target: SpyTargetInput | None) -> object:
    if target is None:
        return None
    if isinstance(target, Node):
        return {"type": "NodeRef", "label": target.label}
    if isinstance(target, Coordinate):
        return {"type": "CoordinateRef", "label": target.label}
    if isinstance(target, TikzCoordinate):
        return {"type": "TikzCoordinate", "data": target.to_dict()}
    if isinstance(target, tuple):
        return {"type": "Tuple", "value": serialize_tikz_value(target)}
    if isinstance(target, str):
        return {"type": "RawString", "value": target}
    raise TypeError(f"Unsupported spy target type: {type(target)!r}")


def _deserialize_spy_target(
    target: object,
    node_lookup: Mapping[str, Node | Coordinate] | None = None,
) -> SpyTargetInput | None:
    if target is None:
        return None
    if not isinstance(target, Mapping):
        raise TypeError("Serialized spy targets must deserialize to mappings.")

    target_type = target.get("type")
    if target_type == "NodeRef" or target_type == "CoordinateRef":
        label = str(target["label"])
        if node_lookup is not None and label in node_lookup:
            return node_lookup[label]
        return label
    if target_type == "TikzCoordinate":
        data = target.get("data")
        if not isinstance(data, dict):
            raise TypeError("Serialized TikzCoordinate spy target must be a dict.")
        return TikzCoordinate.from_dict(data)
    if target_type == "Tuple":
        value = deserialize_tikz_value(target.get("value"))
        if not isinstance(value, tuple):
            raise TypeError("Serialized tuple spy target must deserialize to a tuple.")
        return value
    if target_type == "RawString":
        return str(target["value"])
    raise ValueError(f"Unknown serialized spy target type: {target_type!r}")


def format_spy_target(target: SpyTargetInput, output_unit: str | None = None) -> str:
    """Format a spy target as TikZ coordinate or node reference syntax."""
    if isinstance(target, (Node, Coordinate)):
        if target.label in (None, ""):
            raise ValueError(
                "Spy targets that reference nodes/coordinates need labels."
            )
        return f"({target.label})"
    if isinstance(target, TikzCoordinate):
        return target.to_tikz(output_unit)
    if isinstance(target, tuple):
        return TikzCoordinate(target).to_tikz(output_unit)
    stripped = target.strip()
    if stripped.startswith("(") and stripped.endswith(")"):
        return stripped
    return f"({stripped})"


def build_lens_value(
    lens: OptionInput | str | None = None,
    lens_kwargs: Mapping[str, Any] | None = None,
    output_unit: str | None = None,
) -> str | None:
    """Build the value for TikZ's ``lens={...}`` spy option."""
    if lens is None and not lens_kwargs:
        return None
    if isinstance(lens, str):
        return _wrap_braces(lens)
    lens_body = _format_option_mapping(lens, lens_kwargs or {}, output_unit)
    return _wrap_braces(lens_body)


def build_spy_command_parts(
    options: OptionInput | None = None,
    *,
    magnification: float | None = None,
    lens: OptionInput | str | None = None,
    lens_kwargs: Mapping[str, Any] | None = None,
    size: str | object | None = None,
    width: str | object | None = None,
    height: str | object | None = None,
    connect_spies: bool = False,
    **kwargs: Any,
) -> tuple[list[Any], dict[str, Any]]:
    """Split spy-command inputs into normalized option tokens and keyword options."""
    spy_options = list(normalize_options(options))
    if connect_spies:
        spy_options.append("connect spies")

    spy_kwargs = dict(kwargs)
    if magnification is not None:
        spy_kwargs["magnification"] = magnification
    if size is not None:
        spy_kwargs["size"] = size
    if width is not None:
        spy_kwargs["width"] = width
    if height is not None:
        spy_kwargs["height"] = height

    lens_value = build_lens_value(lens, lens_kwargs)
    if lens_value is not None:
        spy_kwargs["lens"] = lens_value

    return spy_options, spy_kwargs


def _format_style_value(
    options: OptionInput | None,
    style: Mapping[str, Any] | None,
    output_unit: str | None = None,
) -> str:
    return _format_option_mapping(options, style or {}, output_unit)


def build_spy_scope_parts(
    mode: SpyScopeMode = "scope",
    options: OptionInput | None = None,
    *,
    magnification: float | None = None,
    lens: OptionInput | str | None = None,
    lens_kwargs: Mapping[str, Any] | None = None,
    size: str | object | None = None,
    width: str | object | None = None,
    height: str | object | None = None,
    connect_spies: bool = False,
    every_spy_in_node_options: OptionInput | None = None,
    every_spy_in_node_style: Mapping[str, Any] | None = None,
    every_spy_on_node_options: OptionInput | None = None,
    every_spy_on_node_style: Mapping[str, Any] | None = None,
    spy_connection_path: str | None = None,
    **kwargs: Any,
) -> tuple[list[str], dict[str, str]]:
    """Build scope options for ``spy scope`` or preset spy-scope variants."""
    scope_options, scope_kwargs = build_spy_command_parts(
        options=options,
        magnification=magnification,
        lens=lens,
        lens_kwargs=lens_kwargs,
        size=size,
        width=width,
        height=height,
        connect_spies=connect_spies,
        **kwargs,
    )
    body = _format_option_mapping(scope_options, scope_kwargs)
    key = {
        "scope": "spy scope",
        "outlines": "spy using outlines",
        "overlays": "spy using overlays",
    }[mode]
    option_token = key if body == "" and mode == "scope" else f"{key}={{{body}}}"

    scope_style_kwargs: dict[str, str] = {}
    if every_spy_in_node_options is not None or every_spy_in_node_style is not None:
        scope_style_kwargs["every spy in node/.style"] = _wrap_braces(
            _format_style_value(
                every_spy_in_node_options,
                every_spy_in_node_style,
            )
        )
    if every_spy_on_node_options is not None or every_spy_on_node_style is not None:
        scope_style_kwargs["every spy on node/.style"] = _wrap_braces(
            _format_style_value(
                every_spy_on_node_options,
                every_spy_on_node_style,
            )
        )
    if spy_connection_path is not None:
        scope_style_kwargs["spy connection path"] = _wrap_braces(spy_connection_path)

    return [option_token], scope_style_kwargs


class Spy(TikzObject):
    """A structured TikZ ``\\spy`` command.

    ``Spy`` stores both the spy target (``on``) and the generated inset-node
    placement/styling (``at``, ``node_options``, ``node_style``). It is usually
    created through ``TikzFigure.spy(...)`` or ``Scope.spy(...)`` rather than
    instantiated directly.
    """

    def __init__(
        self,
        on: SpyTargetInput,
        at: SpyTargetInput | None = None,
        node_label: str | None = None,
        node_options: OptionInput | None = None,
        node_style: Mapping[str, Any] | None = None,
        label: str = "",
        comment: str | None = None,
        layer: int = 0,
        options: OptionInput | None = None,
        **kwargs: Any,
    ) -> None:
        self._on = on
        self._at = at
        self._node_label = node_label
        self._node_options = normalize_options(node_options)
        self._node_style = dict(node_style or {})
        super().__init__(
            label=label,
            comment=comment,
            layer=layer,
            options=options,
            **kwargs,
        )

    @property
    def on(self) -> SpyTargetInput:
        """Return the region or node being magnified."""
        return self._on

    @property
    def at(self) -> SpyTargetInput | None:
        """Return where the spy-in node is placed, if specified."""
        return self._at

    @property
    def node_label(self) -> str | None:
        """Return the optional TikZ label assigned to the spy-in node."""
        return self._node_label

    @property
    def node_options(self) -> list[Any]:
        """Return flag-style options applied to the spy-in node."""
        return list(self._node_options)

    @property
    def node_style(self) -> dict[str, Any]:
        """Return keyword-style options applied to the spy-in node."""
        return dict(self._node_style)

    def to_tikz(self, output_unit: str | None = None) -> str:
        """Render the spy command as TikZ source."""
        options = self.tikz_options(output_unit)
        option_block = f"[{options}]" if options else ""

        node_parts: list[str] = []
        if self._node_label:
            node_parts.append(f"({self._node_label})")
        node_option_block = _format_option_mapping(
            self._node_options,
            self._node_style,
            output_unit,
        )
        if node_option_block:
            node_parts.append(f"[{node_option_block}]")
        if self._at is not None:
            node_parts.append(f"at {format_spy_target(self._at, output_unit)}")

        node_spec = " ".join(node_parts)
        spy_str = (
            f"\\spy{option_block} on {format_spy_target(self._on, output_unit)} in node"
        )
        if node_spec:
            spy_str += f" {node_spec}"
        spy_str += ";\n"
        return self.add_comment(spy_str)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the spy command, preserving structured targets and styling."""
        d = super().to_dict()
        d.update(
            {
                "type": "Spy",
                "on": _serialize_spy_target(self._on),
                "at": _serialize_spy_target(self._at),
                "node_label": self._node_label,
                "node_options": serialize_tikz_value(self._node_options),
                "node_style": serialize_tikz_value(self._node_style),
            }
        )
        serialized = serialize_tikz_value(d)
        if not isinstance(serialized, dict):
            raise TypeError("Serialized spy data must remain a dict.")
        return serialized

    @classmethod
    def from_dict(
        cls,
        d: dict[str, Any],
        node_lookup: Mapping[str, Node | Coordinate] | None = None,
    ) -> "Spy":
        """Restore a ``Spy`` from serialized data."""
        restored = deserialize_tikz_value(d)
        if not isinstance(restored, dict):
            raise TypeError("Serialized spy data must deserialize to a dict.")

        node_style = restored.get("node_style", {})
        if not isinstance(node_style, Mapping):
            raise TypeError("Serialized spy node_style must deserialize to a mapping.")
        on = _deserialize_spy_target(restored.get("on"), node_lookup)
        if on is None:
            raise TypeError("Serialized spy data must include an 'on' target.")

        return cls(
            on=on,
            at=_deserialize_spy_target(restored.get("at"), node_lookup),
            node_label=restored.get("node_label"),
            node_options=restored.get("node_options"),
            node_style=dict(node_style),
            label=restored.get("label", ""),
            comment=restored.get("comment"),
            layer=restored.get("layer", 0),
            options=restored.get("options"),
            **restored.get("kwargs", {}),
        )

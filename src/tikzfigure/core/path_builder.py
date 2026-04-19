from __future__ import annotations

from copy import deepcopy
from typing import Any

from tikzfigure.core.node import Node
from tikzfigure.core.types import _Option
from tikzfigure.options import OptionInput, normalize_options
from tikzfigure.units import TikzDimension

SegmentOption = dict[str, Any] | _Option | None


class NodePathBuilder:
    """Internal fluent builder for chained path segments."""

    def __init__(self, start: Node) -> None:
        self._nodes: list[Node] = [start]
        self._segment_options: list[SegmentOption] = []

    @staticmethod
    def _normalize_segment_options(
        options: OptionInput | None = None,
        **kwargs: Any,
    ) -> SegmentOption:
        flag_options = normalize_options(options)

        if not flag_options and not kwargs:
            return None

        segment: dict[str, Any] = {}
        if flag_options:
            segment["options"] = flag_options
        segment.update(kwargs)
        return segment

    def to(
        self,
        target: Node,
        options: OptionInput | None = None,
        **kwargs: Any,
    ) -> NodePathBuilder:
        if not isinstance(target, Node):
            raise TypeError("NodePathBuilder.to() only supports Node targets in v1.")

        self._nodes.append(target)
        self._segment_options.append(
            self._normalize_segment_options(options=options, **kwargs)
        )
        return self

    def arc(
        self,
        start_angle: float,
        end_angle: float,
        radius: float | str | TikzDimension,
        options: OptionInput | None = None,
        **kwargs: Any,
    ) -> NodePathBuilder:
        self._segment_options.append(
            self._normalize_segment_options(
                options=options,
                connector="arc",
                start_angle=start_angle,
                end_angle=end_angle,
                radius=radius,
                **kwargs,
            )
        )
        return self

    @property
    def nodes(self) -> list[Node]:
        return list(self._nodes)

    @property
    def segment_options(self) -> list[SegmentOption] | None:
        if not self._segment_options:
            return None
        return deepcopy(self._segment_options)

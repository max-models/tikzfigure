from __future__ import annotations

from copy import deepcopy
from typing import Any

from tikzfigure.core.node import Node
from tikzfigure.core.types import _Option

SegmentOption = dict[str, Any] | _Option | None


class NodePathBuilder:
    """Internal fluent builder for node-to-node path segments."""

    def __init__(self, start: Node) -> None:
        self._nodes: list[Node] = [start]
        self._segment_options: list[SegmentOption] = []

    @staticmethod
    def _normalize_segment_options(
        options: list[_Option] | _Option | None = None,
        **kwargs: Any,
    ) -> SegmentOption:
        if options is None:
            flag_options: list[_Option] = []
        elif not isinstance(options, list):
            flag_options = [options]
        else:
            flag_options = list(options)

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
        options: list[_Option] | _Option | None = None,
        **kwargs: Any,
    ) -> NodePathBuilder:
        if not isinstance(target, Node):
            raise TypeError("NodePathBuilder.to() only supports Node targets in v1.")

        self._nodes.append(target)
        self._segment_options.append(
            self._normalize_segment_options(options=options, **kwargs)
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

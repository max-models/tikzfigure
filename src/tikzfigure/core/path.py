from typing import Any

from tikzfigure.core.base import TikzObject
from tikzfigure.core.coordinate import TikzCoordinate
from tikzfigure.core.node import Node


class TikzPath(TikzObject):
    """A TikZ path connecting nodes or coordinates with ``\\draw`` or ``\\filldraw``.

    Attributes:
        nodes: Ordered list of nodes or coordinates that define the path.
        cycle: Whether the path is closed with ``-- cycle``.
        center: Whether paths connect through node center anchors.
        tikz_command: The TikZ draw command (``"draw"`` or ``"filldraw"``).
        label_list: Rendered list of TikZ reference strings for each node.
        node_anchors: Per-node anchor overrides (e.g. ``["center", None]``).
        segment_options: Per-segment TikZ options dicts for each ``to``
            connector between nodes.
    """

    def __init__(
        self,
        nodes: list,
        cycle: bool = False,
        label: str = "",
        comment: str | None = None,
        layer: int = 0,
        center: bool = False,
        node_anchors: list[str | None] | None = None,
        segment_options: list[dict | str | None] | None = None,
        options: list | None = None,
        tikz_command: str = "draw",
        **kwargs: Any,
    ) -> None:
        """Initialize a TikzPath.

        Args:
            nodes: Ordered list of :class:`Node` or :class:`TikzCoordinate`
                objects defining the path waypoints.
            cycle: If ``True``, close the path with ``-- cycle``.
                Defaults to ``False``.
            label: Internal TikZ name for this path. Defaults to ``""``.
            comment: Optional comment prepended in the TikZ output.
            layer: Layer index. Defaults to ``0``.
            center: If ``True``, connect through ``.center`` anchors instead
                of the default anchor. Defaults to ``False``.
            node_anchors: Per-node anchor overrides. Each entry is an anchor
                string (e.g. ``"center"``, ``"north"``) or ``None`` to use
                the default or global *center* flag.  When provided, a
                per-node anchor takes precedence over *center*.
            segment_options: Per-segment TikZ options for each ``to``
                connector between consecutive nodes.  The list has at most
                ``len(nodes) - 1`` entries.  Each entry is either ``None``
                (plain ``to``), a raw options string, or a dict where the
                special key ``"options"`` holds a list of flag-style options
                and all other keys are keyword-style TikZ options
                (underscores become spaces).
            options: Flag-style TikZ options (e.g. ``["->", "thick"]``).
            tikz_command: The TikZ drawing command to use, either ``"draw"``
                or ``"filldraw"``. Defaults to ``"draw"``.
            **kwargs: Keyword-style TikZ options (e.g. ``color="red"``).
        """
        if options is None:
            options = []

        self._nodes = nodes
        self._cycle = cycle
        self._center = center
        self._node_anchors = node_anchors
        self._segment_options = segment_options
        self._tikz_command = tikz_command

        super().__init__(
            label=label,
            comment=comment,
            layer=layer,
            options=options,
            **kwargs,
        )

    @property
    def nodes(self) -> list[Node | TikzCoordinate]:
        """Ordered list of nodes or coordinates that define this path."""
        return self._nodes

    @property
    def cycle(self) -> bool:
        """Whether the path is closed with ``-- cycle``."""
        return self._cycle

    @property
    def center(self) -> bool:
        """Whether paths connect through node ``.center`` anchors."""
        return self._center

    @property
    def node_anchors(self) -> list[str | None] | None:
        """Per-node anchor overrides, or ``None`` if not set."""
        return self._node_anchors

    @property
    def segment_options(self) -> list[dict | str | None] | None:
        """Per-segment TikZ options for each ``to`` connector, or ``None``."""
        return self._segment_options

    @staticmethod
    def _format_segment_opts(opts: dict | str) -> str:
        """Render a segment-options entry as a TikZ options string.

        Args:
            opts: Either a raw string (used as-is) or a dict with an
                optional ``"options"`` key for flag-style items and
                remaining keys treated as keyword-style TikZ options
                (underscores converted to spaces).

        Returns:
            A comma-separated TikZ options string suitable for use inside
            ``to[...]``.
        """
        if isinstance(opts, str):
            return opts
        parts: list[str] = []
        flag_opts = opts.get("options", [])
        if flag_opts:
            parts.extend(flag_opts)
        for k, v in opts.items():
            if k == "options":
                continue
            parts.append(f"{k.replace('_', ' ')}={v}")
        return ", ".join(parts)

    @property
    def tikz_options(self) -> str:
        """Render all options as a single TikZ option string.

        Returns:
            A comma-separated string of TikZ options combining flag-style
            and keyword options.
        """
        parts = []
        if self.options:
            parts.append(", ".join(self.options))
        kwargs_str = ", ".join(
            f"{k.replace('_', ' ')}={v}" for k, v in self.kwargs.items()
        )
        if kwargs_str:
            parts.append(kwargs_str)
        return ", ".join(parts)

    @property
    def label_list(self) -> list[str]:
        """Rendered TikZ reference strings for each node in this path.

        Per-node anchors (from :attr:`node_anchors`) take precedence over
        the global :attr:`center` flag.

        Returns:
            A list of strings such as ``["(nodeA)", "(nodeB.center)"]`` or
            coordinate tuples for :class:`TikzCoordinate` waypoints.
        """
        label_list = []
        for i, node in enumerate(self.nodes):
            if isinstance(node, Node):
                assert node.label != "", (
                    "Trying to draw a path using a node without a label!"
                )
                anchor = (
                    self._node_anchors[i]
                    if self._node_anchors and i < len(self._node_anchors)
                    else None
                )
                if anchor is not None:
                    label_list.append(f"({node.label}.{anchor})")
                elif self.center:
                    label_list.append(f"({node.label}.center)")
                else:
                    label_list.append(f"({node.label})")
            elif isinstance(node, TikzCoordinate):
                parts = ", ".join(str(x) for x in node.coordinate)
                label_list.append(f"({parts})")
        return label_list

    @property
    def tikz_command(self) -> str:
        """The TikZ drawing command (``"draw"`` or ``"filldraw"``)."""
        return self._tikz_command

    def to_tikz(self) -> str:
        """Generate the TikZ path command for this path.

        Returns:
            A ``\\draw`` or ``\\filldraw`` command string ending with a
            newline, optionally preceded by a comment line.
        """
        options = self.tikz_options
        label_list = self.label_list

        if label_list:
            parts = [label_list[0]]
            for i in range(1, len(label_list)):
                seg_opts = (
                    self._segment_options[i - 1]
                    if self._segment_options and i - 1 < len(self._segment_options)
                    else None
                )
                if seg_opts is not None:
                    parts.append(f"to[{self._format_segment_opts(seg_opts)}]")
                else:
                    parts.append("to")
                parts.append(label_list[i])
            path_str = " ".join(parts)
        else:
            path_str = ""

        if self.cycle:
            path_str += " -- cycle"

        path_str = f"\\{self.tikz_command}[{options}] {path_str};\n"

        path_str = self.add_comment(path_str)

        return path_str

    def to_dict(self) -> dict[str, Any]:
        """Serialize this path to a plain dictionary.

        Returns:
            A dictionary with ``type``, ``nodes``, ``cycle``, ``center``,
            ``tikz_command``, and all base-class keys.
        """
        d = super().to_dict()
        serialized_nodes = []
        for node in self._nodes:
            if isinstance(node, Node):
                serialized_nodes.append({"type": "NodeRef", "label": node.label})
            elif isinstance(node, TikzCoordinate):
                serialized_nodes.append(node.to_dict())
        d.update(
            {
                "type": "Path",
                "nodes": serialized_nodes,
                "cycle": self._cycle,
                "center": self._center,
                "node_anchors": self._node_anchors,
                "segment_options": self._segment_options,
                "tikz_command": self._tikz_command,
            }
        )
        return d

    @classmethod
    def from_dict(
        cls, d: dict[str, Any], node_lookup: dict[str, Any] | None = None
    ) -> "TikzPath":
        """Reconstruct a TikzPath from a dictionary.

        Args:
            d: Dictionary as produced by :meth:`to_dict`.
            node_lookup: Mapping from node labels to :class:`Node` objects,
                used to resolve ``NodeRef`` entries. Defaults to ``None``
                (empty lookup).

        Returns:
            A new :class:`TikzPath` instance with nodes resolved.
        """
        node_lookup = node_lookup or {}
        nodes = []
        for node_data in d.get("nodes", []):
            if node_data["type"] == "NodeRef":
                nodes.append(node_lookup[node_data["label"]])
            elif node_data["type"] == "TikzCoordinate":
                nodes.append(TikzCoordinate.from_dict(node_data))
        kwargs = d.get("kwargs", {})
        return cls(
            nodes=nodes,
            cycle=d.get("cycle", False),
            label=d.get("label", ""),
            comment=d.get("comment"),
            layer=d.get("layer", 0),
            center=d.get("center", False),
            node_anchors=d.get("node_anchors"),
            segment_options=d.get("segment_options"),
            options=d.get("options"),
            tikz_command=d.get("tikz_command", "draw"),
            **kwargs,
        )

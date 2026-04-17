from typing import Any

from tikzfigure.core.base import TikzObject
from tikzfigure.core.constants import TAB
from tikzfigure.core.coordinate import Coordinate, TikzCoordinate
from tikzfigure.core.node import Node
from tikzfigure.core.path_builder import SegmentOption
from tikzfigure.core.types import _Option
from tikzfigure.options import OptionInput


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
        segment_options: list[SegmentOption] | None = None,
        options: OptionInput | None = None,
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
            segment_options: Per-segment options for each connector between
                consecutive nodes.  The list has at most ``len(nodes) - 1``
                entries.  Each entry is ``None`` (plain ``to``), a raw
                options string, or a dict recognising these special keys:

                * ``"connector"`` — the TikZ path operation to use between
                  the two waypoints.  Defaults to ``"to"``; other accepted
                  values are ``"--"``, ``".."``, ``"|-"``, ``"-|"``,
                  ``"sin"``, and ``"cos"``.  Only ``"to"`` supports bracket
                  options.
                * ``"node"`` — an inline node placed along the segment.
                  Either a raw string suffix (e.g. ``"[above] {text}"``)
                  or a dict with a ``"content"`` key and node-option keys.
                * ``"options"`` — list of flag-style TikZ options for ``to``.
                * Any other key is a keyword-style TikZ option for ``to``
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
    def nodes(self) -> list[Node | Coordinate | TikzCoordinate]:
        """Ordered list of nodes, named coordinates, or inline coordinates that define this path."""
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
    def segment_options(self) -> list[SegmentOption] | None:
        """Per-segment TikZ options for each ``to`` connector, or ``None``."""
        return self._segment_options

    #: Connector types that accept bracket options via ``to[...]``.
    _TO_CONNECTORS: frozenset[str] = frozenset({"to"})

    #: Connector types that are emitted as-is with no bracket options.
    _PLAIN_CONNECTORS: frozenset[str] = frozenset(
        {"--", "..", "|-", "-|", "sin", "cos"}
    )

    @staticmethod
    def _format_segment_opts(opts: dict | _Option) -> str:
        """Render a segment-options entry as a TikZ options string.

        Structural keys ``"connector"`` and ``"node"`` are skipped; they
        control the connector type and inline node label respectively and
        are not emitted as TikZ options.

        Args:
            opts: Either a raw string (used as-is) or a dict with an
                optional ``"options"`` key for flag-style items and
                remaining keys treated as keyword-style TikZ options
                (underscores converted to spaces).

        Returns:
            A comma-separated TikZ options string suitable for use inside
            ``to[...]``.
        """
        if not isinstance(opts, dict):
            return str(opts)
        _skip = frozenset({"options", "connector", "node"})
        parts: list[str] = []
        flag_opts = opts.get("options", [])
        if flag_opts:
            parts.extend(str(opt) for opt in flag_opts)
        for k, v in opts.items():
            if k in _skip:
                continue
            parts.append(f"{k.replace('_', ' ')}={v}")
        return ", ".join(parts)

    @staticmethod
    def _format_path_node(node_spec: dict | str) -> str:
        """Render a mid-path inline node specification.

        In TikZ, nodes can be placed along a path segment::

            \\draw (A) to node[above] {label} (B);

        Args:
            node_spec: Either a raw suffix string such as ``"[above] {text}"``
                (prepended with ``node`` verbatim), or a dict with a
                ``"content"`` key for the node text, an optional
                ``"options"`` key for flag-style node options, and any
                further keyword keys for TikZ node options.  Boolean values
                of ``True`` are treated as flag-style options.

        Returns:
            A ``node[...] {content}`` string fragment for insertion into a
            path command.
        """
        if isinstance(node_spec, str):
            return f"node{node_spec}"
        content = node_spec.get("content", "")
        flag_opts: list[str] = [str(opt) for opt in node_spec.get("options", [])]
        kw_parts: list[str] = []
        for k, v in node_spec.items():
            if k in ("content", "options"):
                continue
            if v is True:
                flag_opts.append(k.replace("_", " "))
            else:
                kw_parts.append(f"{k.replace('_', ' ')}={v}")
        all_opts = flag_opts + kw_parts
        opts_str = ", ".join(all_opts)
        if opts_str:
            return f"node[{opts_str}] {{{content}}}"
        return f"node {{{content}}}"

    def tikz_options(self, output_unit: str | None = None) -> str:
        """Render all options as a single TikZ option string.

        Args:
            output_unit: If provided, any :class:`~tikzfigure.units.TikzDimension`
                values are converted to this unit before rendering.

        Returns:
            A comma-separated string of TikZ options combining flag-style
            and keyword options.
        """
        from tikzfigure.units import TikzDimension

        def _fmt(v: object) -> str:
            if isinstance(v, TikzDimension):
                return str(v.to(output_unit)) if output_unit is not None else str(v)
            return str(v)

        parts = []
        if self.options:
            parts.append(", ".join(str(option) for option in self.options))
        kwargs_str = ", ".join(
            f"{k.replace('_', ' ')}={_fmt(v)}" for k, v in self.kwargs.items()
        )
        if kwargs_str:
            parts.append(kwargs_str)
        return ", ".join(parts)

    @property
    def label_list(self) -> list[str]:
        """Rendered TikZ reference strings for each node in this path.

        Per-node anchors (from :attr:`node_anchors`) take precedence over
        the global :attr:`center` flag.  :class:`Coordinate` objects are
        referenced by label exactly like :class:`Node` objects.

        Returns:
            A list of strings such as ``["(nodeA)", "(nodeB.center)"]``,
            ``["(coordA)"]``, or coordinate tuples for inline
            :class:`TikzCoordinate` waypoints.
        """
        return self._render_label_list()

    def _render_label_list(self, output_unit: str | None = None) -> list[str]:
        """Render path waypoints, converting inline dimensions when requested."""
        label_list = []
        for i, node in enumerate(self.nodes):
            if isinstance(node, (Node, Coordinate)):
                assert node.label != "", (
                    "Trying to draw a path using a node/coordinate without a label!"
                )
                anchor = (
                    self._node_anchors[i]
                    if self._node_anchors and i < len(self._node_anchors)
                    else None
                )
                if anchor is not None:
                    label_list.append(f"({node.label}.{anchor})")
                elif self.center and isinstance(node, Node):
                    label_list.append(f"({node.label}.center)")
                else:
                    label_list.append(f"({node.label})")
            elif isinstance(node, TikzCoordinate):
                parts = ", ".join(
                    TikzCoordinate._format_component(component, output_unit)
                    for component in node.coordinate
                )
                label_list.append(f"({parts})")
        return label_list

    @property
    def tikz_command(self) -> str:
        """The TikZ drawing command (``"draw"`` or ``"filldraw"``)."""
        return self._tikz_command

    def to_tikz(self, output_unit: str | None = None) -> str:
        """Generate the TikZ path command for this path.

        Returns:
            A ``\\draw``, ``\\fill``, ``\\clip``, ``\\path``, or
            ``\\filldraw`` command string ending with a newline, optionally
            preceded by a comment line.
        """
        options = self.tikz_options(output_unit)
        label_list = self._render_label_list(output_unit)

        if label_list:
            parts = [label_list[0]]
            for i in range(1, len(label_list)):
                seg = (
                    self._segment_options[i - 1]
                    if self._segment_options and i - 1 < len(self._segment_options)
                    else None
                )

                # --- connector type ---
                connector = "to"
                if isinstance(seg, dict):
                    connector = seg.get("connector", "to")

                # --- TikZ options for this segment ---
                if seg is not None and connector in self._TO_CONNECTORS:
                    opts_str = self._format_segment_opts(seg)
                    if opts_str:
                        parts.append(f"to[{opts_str}]")
                    else:
                        parts.append("to")
                else:
                    # plain connectors (--  ..  |-  -|  sin  cos) take no brackets
                    parts.append(connector)

                # --- optional inline node label ---
                if isinstance(seg, dict) and "node" in seg:
                    parts.append(self._format_path_node(seg["node"]))

                parts.append(label_list[i])

            # For short paths, keep everything on one line.
            # For longer paths, put connectors on separate lines for readability.
            if len(label_list) <= 3:
                path_str = " ".join(parts)
            else:
                path_str = parts[0]
                for ipart, part in enumerate(parts):
                    if ipart == 0:
                        continue
                    if ipart % 2 == 0:
                        # node label on same line
                        path_str += f" {part}"
                    else:
                        # connector on new line
                        path_str += f"\n{TAB}{part}"
                # path_str = "\n  ".join(parts)
        else:
            path_str = ""

        if self.cycle:
            path_str += " -- cycle"

        option_block = f"[{options}]" if options else ""
        path_str = f"\\{self.tikz_command}{option_block} {path_str};\n"

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
            elif isinstance(node, Coordinate):
                serialized_nodes.append({"type": "CoordinateRef", "label": node.label})
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
            if node_data["type"] in ("NodeRef", "CoordinateRef"):
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

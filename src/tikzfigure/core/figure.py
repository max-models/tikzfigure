import logging
import os
from typing import Any, overload

from tikzfigure.arrows import ArrowInput
from tikzfigure.colors import ColorInput
from tikzfigure.core.arc import Arc
from tikzfigure.core.axis import Axis2D
from tikzfigure.core.circle import Circle
from tikzfigure.core.color import Color
from tikzfigure.core.coordinate import Coordinate, PositionInput, TikzCoordinate
from tikzfigure.core.declared_function import DeclaredFunction
from tikzfigure.core.ellipse import Ellipse
from tikzfigure.core.figure_export import FigureExportMixin
from tikzfigure.core.figure_layout import FigureLayoutMixin
from tikzfigure.core.figure_parsing import FigureParsingMixin
from tikzfigure.core.figure_paths import FigurePathMixin
from tikzfigure.core.figure_render import FigureRenderMixin
from tikzfigure.core.grid import Grid
from tikzfigure.core.layer import LayerCollection
from tikzfigure.core.line import Line
from tikzfigure.core.loop import Loop
from tikzfigure.core.node import Node
from tikzfigure.core.parabola import Parabola
from tikzfigure.core.path import TikzPath
from tikzfigure.core.path_builder import NodePathBuilder, SegmentOption
from tikzfigure.core.plot import Plot3D, TikzPlot
from tikzfigure.core.polygon import Polygon, Square, Triangle
from tikzfigure.core.raw import RawTikz
from tikzfigure.core.rectangle import Rectangle
from tikzfigure.core.scope import Scope
from tikzfigure.core.serialization import deserialize_tikz_value, serialize_tikz_value
from tikzfigure.core.spy import (
    Spy,
    SpyScopeMode,
    build_spy_command_parts,
    build_spy_scope_parts,
)
from tikzfigure.core.types import (
    _Align,
    _Anchor,
    _Decoration,
    _LineCap,
    _LineJoin,
    _Mark,
    _Option,
    _Pattern,
    _Shading,
    _Shape,
    _TikzLibraryLiteral,
)
from tikzfigure.core.variable import Variable
from tikzfigure.options import OptionInput, normalize_options
from tikzfigure.styles import TikzStyle
from tikzfigure.units import TikzDimension

WEB_COMPILATION_ENV_VAR = "TIKZFIGURE_USE_WEB_COMPILATION"
logger = logging.getLogger(__name__)


def _normalize_tikz_libraries(*libraries: str) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()

    for raw_value in libraries:
        for part in raw_value.split(","):
            name = part.strip()
            if name == "":
                raise ValueError("TikZ library names must not be empty.")
            if name not in seen:
                seen.add(name)
                normalized.append(name)

    return normalized


class TikzFigure(
    FigureParsingMixin,
    FigurePathMixin,
    FigureLayoutMixin,
    FigureRenderMixin,
    FigureExportMixin,
):
    """Main entry point for building TikZ figures programmatically.

    Holds layers, variables, colors, and all TikZ primitives.  Call
    :meth:`generate_tikz` to obtain the LaTeX source, :meth:`compile_pdf`
    to compile it, and :meth:`savefig` / :meth:`show` to export or display
    the result.

    Compilation: By default, :meth:`compile_pdf`, :meth:`savefig`, and
    :meth:`show` use pdflatex if available on your system. If pdflatex is
    unavailable, tikzfigure automatically falls back to the latex-on-http
    web API for compilation. You can explicitly request web-based compilation
    by passing ``use_web_compilation=True`` to these methods. This allows
    figures to be compiled and rendered without requiring a local LaTeX
    installation. You can also force this behavior process-wide by setting
    the ``TIKZFIGURE_USE_WEB_COMPILATION=1`` environment variable. See
    https://github.com/max-models/tikzfigure for more details.

    Attributes:
        layers: The :class:`LayerCollection` holding all drawing layers.
        variables: List of :class:`Variable` objects defined in this figure.
        colors: List of ``(name, Color)`` pairs defined with
            :meth:`colorlet`.
        ndim: Number of spatial dimensions (``2`` or ``3``).
        document_setup: Custom LaTeX preamble inserted before
            ``\\begin{document}``.
        extra_packages: Extra LaTeX packages to include in the preamble.
    """

    # ------------------------------------------------------------- #
    # Private methods

    @staticmethod
    def _coerce_path_input(
        nodes: list[Any] | NodePathBuilder,
        segment_options: list[SegmentOption] | None = None,
    ) -> tuple[list[Any], list[SegmentOption] | None]:
        """Normalize draw/filldraw path input to nodes + segment options."""
        if isinstance(nodes, NodePathBuilder):
            if segment_options is not None:
                raise ValueError(
                    "segment_options cannot be passed to draw()/filldraw() "
                    "when using a NodePathBuilder."
                )
            return nodes.nodes, nodes.segment_options
        return nodes, segment_options

    @staticmethod
    def _env_requests_web_compilation() -> bool:
        """Return True when the environment forces web compilation."""
        value = os.environ.get(WEB_COMPILATION_ENV_VAR)
        if value is None:
            return False
        return value.strip().lower() in {"1", "true", "yes", "on"}

    def _resolve_use_web_compilation(self, use_web_compilation: bool) -> bool:
        """Resolve the effective web compilation setting."""
        return use_web_compilation or self._env_requests_web_compilation()

    def _add_path(
        self,
        nodes: list[Any],
        layer: int = 0,
        comment: str | None = None,
        center: bool = False,
        tikz_command: str = "draw",
        verbose: bool = False,
        options: OptionInput | None = None,
        cycle: bool = False,
        segment_options: list[SegmentOption] | None = None,
        **kwargs: Any,
    ) -> TikzPath:
        """Internal helper that creates and registers a :class:`TikzPath`.

        Resolves node labels to :class:`Node` objects and coordinate tuples
        to :class:`TikzCoordinate` objects before constructing the path.

        Node label strings may include an anchor suffix using TikZ dot
        notation (e.g. ``"n1.center"`` or ``"n1.north"``).  The suffix is
        resolved by first trying the full string as a node label, and
        falling back to splitting at the last ``.`` if no exact match is
        found.

        Args:
            nodes: Items to connect. Each element may be a :class:`Node`,
                :class:`Coordinate`, a node label string (optionally with a
                ``.anchor`` suffix), or an ``(x, y)`` / ``(x, y, z)``
                coordinate tuple.
            layer: Target layer index. Defaults to ``0``.
            comment: Optional comment prepended in the TikZ output.
            center: If ``True``, connect all nodes through ``.center``
                anchors (overridden per-node by dot-notation in *nodes*).
            tikz_command: TikZ drawing command (``"draw"`` or
                ``"filldraw"``). Defaults to ``"draw"``.
            verbose: If ``True``, print the resolved node list.
            options: Flag-style TikZ options (string or list).
            cycle: If ``True``, close the path with ``-- cycle``.
            segment_options: Per-segment TikZ options for each ``to``
                connector.  At most ``len(nodes) - 1`` entries.  Each
                entry is ``None`` (plain ``to``), a raw options string, or
                a dict (see :class:`TikzPath` for the dict format).
            **kwargs: Keyword-style TikZ path options.

        Returns:
            The newly created :class:`TikzPath`.

        Raises:
            ValueError: If *nodes* is not a list.
            NotImplementedError: If an element of *nodes* has an
                unrecognised type.
        """
        if not isinstance(nodes, list):
            raise ValueError("nodes parameter must be a list of node names.")

        nodes_cleaned: list[Node | Coordinate | TikzCoordinate] = []
        node_anchors: list[str | None] = []

        for node in nodes:
            if isinstance(node, (Node, Coordinate)):
                nodes_cleaned.append(node)
                node_anchors.append(None)
            elif isinstance(node, str):
                # Try exact label first; if not found and the string
                # contains a dot, split into label + anchor.
                try:
                    nodes_cleaned.append(self.layers.get_node(node))
                    node_anchors.append(None)
                except ValueError:
                    if "." in node:
                        label_part, anchor_part = node.rsplit(".", 1)
                        nodes_cleaned.append(self.layers.get_node(label_part))
                        node_anchors.append(anchor_part)
                    else:
                        raise
            elif isinstance(node, tuple) or isinstance(node, list):
                coords = tuple(node)
                nodes_cleaned.append(TikzCoordinate(*coords, layer=layer))  # type: ignore[misc]
                node_anchors.append(None)
            else:
                raise NotImplementedError(
                    f"{node =}, {type(node) =} is not a valid node type!",
                )

        if verbose:
            print(f"Creating a path with the following nodes {nodes_cleaned}")

        options = normalize_options(options)

        resolved_anchors = (
            node_anchors if any(a is not None for a in node_anchors) else None
        )

        path = TikzPath(
            nodes=nodes_cleaned,
            comment=comment,
            center=center,
            node_anchors=resolved_anchors,
            segment_options=segment_options,
            tikz_command=tikz_command,
            options=options,
            cycle=cycle,
            **kwargs,
        )
        self.layers.add_item(item=path, layer=layer, verbose=verbose)
        return path

    def __init__(
        self,
        ndim: int = 2,
        label: str | None = None,
        grid: bool = False,
        tikz_code: str | None = None,
        extra_packages: list | None = None,
        document_setup: str | None = None,
        figure_setup: str | None = None,
        figsize: tuple[float, float] = (10, 6),
        description: str | None = None,
        show_axes: bool = False,
        rows: int | None = None,
        cols: int | None = None,
    ) -> None:
        """Initialize a TikzFigure.

        Args:
            ndim: Number of spatial dimensions. Use ``2`` for standard
                figures and ``3`` for pgfplots 3-D axis figures.
                Defaults to ``2``.
            label: LaTeX ``\\label`` for the surrounding ``figure``
                environment. When set, the figure is wrapped in a
                ``figure`` environment.
            grid: If ``True``, draw a background grid. Defaults to
                ``False``.
            tikz_code: Existing TikZ code to parse and import. When
                provided, nodes and paths are reconstructed from the
                source. Defaults to ``None``.
            extra_packages: Additional LaTeX packages to include in the
                standalone preamble (e.g. ``["amsmath"]``).
            document_setup: Raw LaTeX to insert in the preamble after
                the standard packages.
            figure_setup: TikZ options string placed inside the opening
                ``\\begin{tikzpicture}[…]`` bracket.
            figsize: ``(width, height)`` in centimetres used as a hint
                for display backends. Defaults to ``(10, 6)``.
            description: Long description stored for documentation
                purposes (not emitted in TikZ output).
            show_axes: For 3-D figures, if ``True`` render the pgfplots
                axis lines and labels. Defaults to ``False``.
            rows: Number of rows in subfigure grid. Must be specified with cols.
                Defaults to None (no grid).
            cols: Number of columns in subfigure grid. Must be specified with rows.
                Defaults to None (no grid).
        """

        self._figsize: tuple[float, float] = figsize
        self._description: str | None = description
        self._label: str | None = label
        self._grid: bool = grid
        self._show_axes: bool = show_axes
        self._tikz_code: str | None = tikz_code
        self._figure_setup: str | None = figure_setup
        self._extra_packages: list[str] | None = (
            list(extra_packages) if extra_packages else None
        )
        self._tikz_libraries: list[str] = []
        self._named_styles: list[dict[str, Any]] = []
        self._document_setup: str | None = document_setup
        # Initialize lists to hold Node and Path objects
        # TODO: nodes, paths, layers should have @property and @setter methods
        self._layers: LayerCollection = LayerCollection()
        self._variables: list[Variable] = []
        self._declared_functions: list[DeclaredFunction] = []
        self._colors: list[tuple[str, Color]] = []
        self._ndim: int = ndim
        self._axes: list[Axis2D] = []
        # Subfigure axes with metadata (axis, width)
        self._subfigure_axes: list[tuple[Axis2D, float]] = []

        # Grid layout parameters
        self._subfigure_rows: int | None = rows
        self._subfigure_cols: int | None = cols
        # Grid stores either an axis cell or a bare subfigure cell.
        self._subfigure_grid: dict[
            tuple[int, int],
            tuple[Axis2D, float] | tuple["TikzFigure", float, str],
        ] = {}
        self._is_bare_subfigure: bool = False
        self._subfigure_position: int = 0

        # Validate grid parameters
        if (rows is None) != (cols is None):
            raise ValueError("Both rows and cols must be specified together")
        if rows is not None:
            # At this point, we know cols is also not None (from the check above)
            assert cols is not None  # Help mypy with type narrowing
            if rows < 1 or cols < 1:
                raise ValueError(
                    f"rows and cols must be positive integers, got rows={rows}, cols={cols}"
                )

        # Counter for unnamed nodes
        self._node_counter: int = 0

        if self._tikz_code:
            self._load_tikz_code(self._tikz_code)

    # ------------------------------------------------------------- #
    # Class methods

    def to_dict(self) -> dict[str, Any]:
        """Serialize this figure to a plain dictionary.

        Returns:
            A dictionary capturing all figure settings, layers, variables,
            and colors, suitable for round-tripping via :meth:`from_dict`.
        """
        layers_dict: dict[Any, list[dict[str, Any]]] = {}
        for layer_label, layer in self._layers.layers.items():
            layers_dict[layer_label] = [item.to_dict() for item in layer.items]
        serialized = serialize_tikz_value(
            {
                "type": "TikzFigure",
                "ndim": self._ndim,
                "label": self._label,
                "grid": self._grid,
                "show_axes": self._show_axes,
                "extra_packages": (
                    list(self._extra_packages) if self._extra_packages else None
                ),
                "tikz_libraries": list(self._tikz_libraries)
                if self._tikz_libraries
                else None,
                "named_styles": [
                    {
                        "name": style_def["name"],
                        "options": style_def["options"],
                        "kwargs": style_def["kwargs"],
                    }
                    for style_def in self._named_styles
                ]
                if self._named_styles
                else None,
                "document_setup": self._document_setup,
                "figure_setup": self._figure_setup,
                "figsize": list(self._figsize),
                "description": self._description,
                "subfigure_rows": self._subfigure_rows,
                "subfigure_cols": self._subfigure_cols,
                "layers": layers_dict,
                "variables": [v.to_dict() for v in self._variables],
                "declared_functions": [
                    function.to_dict() for function in self._declared_functions
                ],
                "colors": [
                    {"name": name, **color.to_dict()} for name, color in self._colors
                ],
                "axes": [axis.to_dict() for axis in self._axes],
            }
        )
        if not isinstance(serialized, dict):
            raise TypeError("Serialized figure data must remain a dict.")
        return serialized

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "TikzFigure":
        """Reconstruct a TikzFigure from a dictionary.

        Args:
            d: Dictionary as produced by :meth:`to_dict`.

        Returns:
            A fully restored :class:`TikzFigure` instance.
        """
        restored = deserialize_tikz_value(d)
        if not isinstance(restored, dict):
            raise TypeError("Serialized figure data must deserialize to a dict.")

        fig = cls(
            ndim=restored.get("ndim", 2),
            label=restored.get("label"),
            grid=restored.get("grid", False),
            extra_packages=restored.get("extra_packages"),
            document_setup=restored.get("document_setup"),
            figure_setup=restored.get("figure_setup"),
            figsize=tuple(restored.get("figsize", [10, 6])),
            description=restored.get("description"),
            show_axes=restored.get("show_axes", False),
            rows=restored.get("subfigure_rows"),
            cols=restored.get("subfigure_cols"),
        )

        for var_dict in restored.get("variables", []):
            fig._variables.append(Variable.from_dict(var_dict))

        for function_dict in restored.get("declared_functions", []):
            fig._declared_functions.append(DeclaredFunction.from_dict(function_dict))

        for color_entry in restored.get("colors", []):
            fig._colors.append((color_entry["name"], Color.from_dict(color_entry)))

        if restored.get("tikz_libraries"):
            fig._tikz_libraries = _normalize_tikz_libraries(*restored["tikz_libraries"])
        if restored.get("named_styles"):
            fig._named_styles = [
                {
                    "name": style_def["name"],
                    "options": normalize_options(style_def.get("options")),
                    "kwargs": dict(style_def.get("kwargs", {})),
                }
                for style_def in restored["named_styles"]
            ]

        # Build node/coordinate lookup across all layers for path deserialization
        layers_data: dict[Any, list[dict[str, Any]]] = restored.get("layers", {})
        node_lookup: dict[str, Node | Coordinate] = {}
        for items_data in layers_data.values():
            for item_data in items_data:
                if item_data.get("type") == "Node":
                    node = Node.from_dict(item_data)
                    if node.label is not None:
                        node_lookup[node.label] = node
                elif item_data.get("type") == "Coordinate":
                    coord = Coordinate.from_dict(item_data)
                    if coord.label:
                        node_lookup[coord.label] = coord

        # Reconstruct layers in order
        for layer_label, items_data in layers_data.items():
            for item_data in items_data:
                item_type = item_data.get("type")
                if item_type == "Node":
                    fig.layers.add_item(
                        node_lookup[item_data["label"]], layer=layer_label
                    )
                elif item_type == "Coordinate":
                    fig.layers.add_item(
                        node_lookup[item_data["label"]], layer=layer_label
                    )
                elif item_type == "Path":
                    fig.layers.add_item(
                        TikzPath.from_dict(item_data, node_lookup=node_lookup),
                        layer=layer_label,
                    )
                elif item_type == "Plot3D":
                    fig.layers.add_item(Plot3D.from_dict(item_data), layer=layer_label)
                elif item_type == "TikzPlot":
                    fig.layers.add_item(
                        TikzPlot.from_dict(item_data), layer=layer_label
                    )
                elif item_type == "Loop":
                    fig.layers.add_item(
                        Loop.from_dict(item_data, node_lookup=node_lookup),
                        layer=layer_label,
                    )
                elif item_type == "Scope":
                    fig.layers.add_item(
                        Scope.from_dict(item_data, node_lookup=node_lookup),
                        layer=layer_label,
                    )
                elif item_type == "Spy":
                    fig.layers.add_item(
                        Spy.from_dict(item_data, node_lookup=node_lookup),
                        layer=layer_label,
                    )
                elif item_type == "RawTikz":
                    fig.layers.add_item(RawTikz.from_dict(item_data), layer=layer_label)
                elif item_type == "Arc":
                    fig.layers.add_item(Arc.from_dict(item_data), layer=layer_label)
                elif item_type == "Circle":
                    fig.layers.add_item(Circle.from_dict(item_data), layer=layer_label)
                elif item_type == "Rectangle":
                    fig.layers.add_item(
                        Rectangle.from_dict(item_data), layer=layer_label
                    )
                elif item_type == "Ellipse":
                    fig.layers.add_item(Ellipse.from_dict(item_data), layer=layer_label)
                elif item_type == "Grid":
                    fig.layers.add_item(Grid.from_dict(item_data), layer=layer_label)
                elif item_type == "Parabola":
                    fig.layers.add_item(
                        Parabola.from_dict(item_data), layer=layer_label
                    )
                elif item_type == "Line":
                    fig.layers.add_item(Line.from_dict(item_data), layer=layer_label)
                elif item_type == "Polygon":
                    fig.layers.add_item(Polygon.from_dict(item_data), layer=layer_label)
                elif item_type == "Triangle":
                    fig.layers.add_item(
                        Triangle.from_dict(item_data), layer=layer_label
                    )
                elif item_type == "Square":
                    fig.layers.add_item(Square.from_dict(item_data), layer=layer_label)

        # Keep node counter consistent with restored nodes
        max_auto = -1
        for label in node_lookup:
            if label.startswith("node"):
                try:
                    max_auto = max(max_auto, int(label[4:]))
                except ValueError:
                    pass
        if max_auto >= 0:
            fig._node_counter = max_auto + 1

        # Reconstruct axes
        for axis_data in restored.get("axes", []):
            axis = Axis2D.from_dict(axis_data)
            fig.axes.append(axis)

        return fig

    def _check(self, output_unit: str | None = None) -> "TikzFigure":
        """Round-trip through dict/TikZ serialization and verify equivalence."""
        data = self.to_dict()
        restored = type(self).from_dict(data)
        if restored.to_dict() != data:
            raise AssertionError(
                "TikzFigure changed after to_dict()/from_dict() round-trip."
            )

        original_tikz = self.generate_tikz(output_unit=output_unit)
        restored_tikz = restored.generate_tikz(output_unit=output_unit)
        if original_tikz != restored_tikz:
            raise AssertionError("TikzFigure changed after generate_tikz() round-trip.")

        return restored

    @staticmethod
    def _copy_value(value: Any) -> Any:
        return deserialize_tikz_value(serialize_tikz_value(value))

    def copy(self, **overrides: Any) -> "TikzFigure":
        """Return a deep copy of this figure with optional figure-level overrides."""
        clone = type(self).from_dict(self.to_dict())
        remaining = {key: self._copy_value(value) for key, value in overrides.items()}

        if "ndim" in remaining:
            clone._ndim = remaining.pop("ndim")
        if "label" in remaining:
            clone._label = remaining.pop("label")
        if "grid" in remaining:
            clone._grid = remaining.pop("grid")
        if "show_axes" in remaining:
            clone._show_axes = remaining.pop("show_axes")
        if "extra_packages" in remaining:
            value = remaining.pop("extra_packages")
            clone._extra_packages = None if value is None else list(value)
        if "tikz_libraries" in remaining:
            value = remaining.pop("tikz_libraries")
            clone._tikz_libraries = (
                [] if value is None else _normalize_tikz_libraries(*value)
            )
        if "named_styles" in remaining:
            value = remaining.pop("named_styles")
            clone._named_styles = [] if value is None else list(value)
        if "document_setup" in remaining:
            clone._document_setup = remaining.pop("document_setup")
        if "figure_setup" in remaining:
            clone._figure_setup = remaining.pop("figure_setup")
        if "figsize" in remaining:
            clone._figsize = tuple(remaining.pop("figsize"))
        if "description" in remaining:
            clone._description = remaining.pop("description")
        if "rows" in remaining:
            clone._subfigure_rows = remaining.pop("rows")
        if "cols" in remaining:
            clone._subfigure_cols = remaining.pop("cols")

        if remaining:
            invalid = ", ".join(sorted(remaining))
            raise TypeError(f"TikzFigure.copy() got unexpected override(s): {invalid}")

        return clone

    # ------------------------------------------------------------- #
    # Public methods

    def _sync_node_counter_from_label(self, label: str | None) -> None:
        """Advance the auto-label counter past an existing ``node<N>`` label."""
        if label is None or not label.startswith("node"):
            return
        try:
            self._node_counter = max(self._node_counter, int(label[4:]) + 1)
        except ValueError:
            return

    def _assign_auto_node_label(self, node: Node) -> None:
        """Assign the next auto-generated node label when needed."""
        if node.label == "":
            node._label = f"node{self._node_counter}"
            self._node_counter += 1

    def _append_figure_setup_items(self, items: list[str]) -> None:
        cleaned = [item.strip() for item in items if item.strip()]
        if not cleaned:
            return
        if self._figure_setup is None or self._figure_setup.strip() == "":
            self._figure_setup = ", ".join(cleaned)
            return
        self._figure_setup = f"{self._figure_setup}, " + ", ".join(cleaned)

    def _figure_has_spy_scope(self) -> bool:
        if self._figure_setup is None:
            return False
        return any(
            key in self._figure_setup
            for key in ("spy scope", "spy using outlines", "spy using overlays")
        )

    def _ensure_figure_spy_scope(self) -> None:
        """Ensure the figure loads the spy library and has a usable top-level scope."""
        self.usetikzlibrary("spy")
        if not self._figure_has_spy_scope():
            self._append_figure_setup_items(["spy scope"])

    def configure_spy_scope(
        self,
        *,
        mode: SpyScopeMode = "scope",
        options: OptionInput | None = None,
        magnification: float | None = None,
        lens: OptionInput | str | None = None,
        lens_kwargs: dict[str, Any] | None = None,
        size: str | object | None = None,
        width: str | object | None = None,
        height: str | object | None = None,
        connect_spies: bool = False,
        every_spy_in_node_options: OptionInput | None = None,
        every_spy_in_node_style: dict[str, Any] | None = None,
        every_spy_on_node_options: OptionInput | None = None,
        every_spy_on_node_style: dict[str, Any] | None = None,
        spy_connection_path: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Append figure-wide defaults for subsequent spy commands.

        This updates ``figure_setup`` with a top-level spy scope configuration,
        which is useful when several ``fig.spy(...)`` calls should share the
        same magnification, lens, node styling, or connection-path settings.
        """
        self.usetikzlibrary("spy")
        scope_options, scope_kwargs = build_spy_scope_parts(
            mode=mode,
            options=options,
            magnification=magnification,
            lens=lens,
            lens_kwargs=lens_kwargs,
            size=size,
            width=width,
            height=height,
            connect_spies=connect_spies,
            every_spy_in_node_options=every_spy_in_node_options,
            every_spy_in_node_style=every_spy_in_node_style,
            every_spy_on_node_options=every_spy_on_node_options,
            every_spy_on_node_style=every_spy_on_node_style,
            spy_connection_path=spy_connection_path,
            **kwargs,
        )
        figure_items = scope_options + [
            f"{key}={value}" for key, value in scope_kwargs.items()
        ]
        self._append_figure_setup_items(figure_items)

    def add_spy(
        self,
        on: Any,
        *,
        layer: int = 0,
        comment: str | None = None,
        verbose: bool = False,
        options: OptionInput | None = None,
        magnification: float | None = None,
        lens: OptionInput | str | None = None,
        lens_kwargs: dict[str, Any] | None = None,
        size: str | object | None = None,
        width: str | object | None = None,
        height: str | object | None = None,
        connect_spies: bool = False,
        at: Any = None,
        node_label: str | None = None,
        node_options: OptionInput | None = None,
        node_style: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Spy:
        """Add a top-level ``\\spy`` command to the figure.

        If the figure does not yet have any spy-scope configuration, this
        method enables a bare ``spy scope`` automatically so the generated
        command works without extra setup.
        """
        self._ensure_figure_spy_scope()
        spy_options, spy_kwargs = build_spy_command_parts(
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
        spy = Spy(
            on=on,
            at=at,
            node_label=node_label,
            node_options=node_options,
            node_style=node_style,
            comment=comment,
            layer=layer,
            options=spy_options,
            **spy_kwargs,
        )
        self.layers.add_item(item=spy, layer=layer, verbose=verbose)
        return spy

    def add_spy_scope(
        self,
        layer: int = 0,
        comment: str | None = None,
        verbose: bool = False,
        mode: SpyScopeMode = "scope",
        options: OptionInput | None = None,
        magnification: float | None = None,
        lens: OptionInput | str | None = None,
        lens_kwargs: dict[str, Any] | None = None,
        size: str | object | None = None,
        width: str | object | None = None,
        height: str | object | None = None,
        connect_spies: bool = False,
        every_spy_in_node_options: OptionInput | None = None,
        every_spy_in_node_style: dict[str, Any] | None = None,
        every_spy_on_node_options: OptionInput | None = None,
        every_spy_on_node_style: dict[str, Any] | None = None,
        spy_connection_path: str | None = None,
        **kwargs: Any,
    ) -> Scope:
        """Create a nested scope with local spy defaults.

        Use this when spy behavior should apply only to a region of the figure,
        or when you want nested spy configurations such as an outer
        ``outlines`` scope with an inner ``overlays`` scope.
        """
        self.usetikzlibrary("spy")
        scope_options, scope_kwargs = build_spy_scope_parts(
            mode=mode,
            options=options,
            magnification=magnification,
            lens=lens,
            lens_kwargs=lens_kwargs,
            size=size,
            width=width,
            height=height,
            connect_spies=connect_spies,
            every_spy_in_node_options=every_spy_in_node_options,
            every_spy_in_node_style=every_spy_in_node_style,
            every_spy_on_node_options=every_spy_on_node_options,
            every_spy_on_node_style=every_spy_on_node_style,
            spy_connection_path=spy_connection_path,
            **kwargs,
        )
        scope_obj = Scope(
            layer=layer,
            comment=comment,
            options=scope_options,
            node_resolver=self.layers.get_node,
            library_loader=self.usetikzlibrary,
            **scope_kwargs,
        )
        self.layers.add_item(item=scope_obj, layer=layer, verbose=verbose)
        return scope_obj

    def add_copy(self, node: Node, verbose: bool = False, **overrides: Any) -> Node:
        """Copy a node into this figure, applying optional constructor-style overrides.

        If the source node has an explicit label and no ``label=...`` override is
        provided, the copied node keeps that label and a warning is logged. Nodes
        whose label was auto-generated by a figure are treated as unlabeled here
        and receive a fresh ``node<N>`` label from this figure.
        """
        copied = node.copy(**overrides)

        if "label" in overrides:
            copied._user_supplied_label = copied.label != ""
        elif copied._user_supplied_label:
            logger.warning(
                "TikzFigure.add_copy() preserved explicit label %r on copied node; pass label=... to override it.",
                copied.label,
            )
        else:
            copied._label = ""

        copied._user_supplied_label = copied.label != ""
        self._assign_auto_node_label(copied)
        self._sync_node_counter_from_label(copied.label)
        self.layers.add_item(item=copied, layer=copied.layer or 0, verbose=verbose)
        return copied

    def add(
        self, items: list | tuple | Node, layer: int = 0, verbose: bool = False
    ) -> None:
        """Add one or more pre-built items to the figure.

        Args:
            items: A single :class:`Node` or a list/tuple of items to add.
            layer: Target layer index. Defaults to ``0``.
            verbose: If ``True``, print a debug message for each insertion.
        """
        if not isinstance(items, list | tuple):
            items = [items]

        for item in items:
            if isinstance(item, Node):
                self._assign_auto_node_label(item)
                self._sync_node_counter_from_label(item.label)
                self.layers.add_item(item=item, layer=layer, verbose=verbose)

    def colorlet(
        self,
        name: str,
        color_spec: ColorInput,
        layer: int = 0,
    ) -> Color:
        """Define a named color with ``\\colorlet``.

        Args:
            name: The name to assign to the color in LaTeX.
            color_spec: A TikZ color specification (e.g. ``"blue!20"``).
            layer: Layer index (currently unused). Defaults to ``0``.

        Returns:
            The :class:`Color` object that was registered.
        """
        color = Color(color_spec=color_spec)

        self._colors.append((name, color))
        return color

    def add_package(self, package: str) -> None:
        """Add a LaTeX package to the standalone preamble.

        Examples:
            >>> fig = TikzFigure()
            >>> fig.add_package("amsmath")
        """
        package_name = package.strip()
        if package_name == "":
            raise ValueError("Package names must not be empty.")

        if self._extra_packages is None:
            self._extra_packages = []
        if package_name not in self._extra_packages:
            self._extra_packages.append(package_name)

    def add_style(
        self,
        name: str,
        options: OptionInput | None = None,
        **kwargs: Any,
    ) -> TikzStyle:
        """Define or update a named TikZ style at figure scope.

        Examples:
            >>> fig = TikzFigure()
            >>> axes = fig.add_style("axes")
            >>> fig.add_style("important line", options=["very thick"])
            >>> fig.add_style("information text", fill="red!10", inner_sep="1ex")
            >>> fig.draw([(0, 0), (1, 0)], options=[axes])
        """
        style_name = name.strip()
        if style_name == "":
            raise ValueError("Style names must not be empty.")

        style_def = {
            "name": style_name,
            "options": normalize_options(options),
            "kwargs": dict(kwargs),
        }
        for index, existing in enumerate(self._named_styles):
            if existing["name"] == style_name:
                self._named_styles[index] = style_def
                break
        else:
            self._named_styles.append(style_def)
        return TikzStyle(style_name)

    @overload
    def usetikzlibrary(self, *libraries: _TikzLibraryLiteral) -> None: ...

    @overload
    def usetikzlibrary(self, *libraries: str) -> None: ...

    def usetikzlibrary(self, *libraries: str) -> None:
        """Register TikZ libraries for standalone output and compilation.

        Examples:
            >>> fig = TikzFigure()
            >>> fig.usetikzlibrary("calc", "intersections")
            >>> fig.usetikzlibrary("positioning,quotes")
        """
        for library in _normalize_tikz_libraries(*libraries):
            if library not in self._tikz_libraries:
                self._tikz_libraries.append(library)

    def add_node(
        self,
        x: (
            float
            | int
            | str
            | tuple[float | int | str, float | int | str]
            | tuple[float | int | str, float | int | str, float | int | str]
            | Node
            | TikzCoordinate
            | None
        ) = None,
        y: float | int | str | None = None,
        z: float | int | str | None = None,
        label: str | None = None,
        content: str = "",
        layer: int = 0,
        comment: str | None = None,
        options: OptionInput | None = None,
        verbose: bool = False,
        # Shape
        shape: _Shape = None,
        # Color
        color: ColorInput | None = None,
        fill: ColorInput | None = None,
        draw: ColorInput | None = None,
        text: ColorInput | None = None,
        # Opacity
        opacity: float | None = None,
        fill_opacity: float | None = None,
        draw_opacity: float | None = None,
        text_opacity: float | None = None,
        # Size
        minimum_width: str | TikzDimension | None = None,
        minimum_height: str | TikzDimension | None = None,
        minimum_size: str | TikzDimension | None = None,
        # Separation
        inner_sep: str | TikzDimension | None = None,
        inner_xsep: str | TikzDimension | None = None,
        inner_ysep: str | TikzDimension | None = None,
        outer_sep: str | TikzDimension | None = None,
        outer_xsep: str | TikzDimension | None = None,
        outer_ysep: str | TikzDimension | None = None,
        # Line
        line_width: str | TikzDimension | None = None,
        # Text
        font: str | None = None,
        text_width: str | TikzDimension | None = None,
        text_height: str | TikzDimension | None = None,
        text_depth: str | TikzDimension | None = None,
        align: _Align = None,
        # Anchor
        anchor: _Anchor = None,
        # Positioning (relative)
        above: str | None = None,
        below: str | None = None,
        left: str | None = None,
        right: str | None = None,
        above_left: str | None = None,
        above_right: str | None = None,
        below_left: str | None = None,
        below_right: str | None = None,
        above_of: str | None = None,
        below_of: str | None = None,
        left_of: str | None = None,
        right_of: str | None = None,
        node_distance: str | TikzDimension | None = None,
        # Transformations
        rotate: float | None = None,
        xshift: str | TikzDimension | None = None,
        yshift: str | TikzDimension | None = None,
        scale: float | None = None,
        xscale: float | None = None,
        yscale: float | None = None,
        xslant: float | None = None,
        yslant: float | None = None,
        # Border
        rounded_corners: str | TikzDimension | None = None,
        double: ColorInput | None = None,
        double_distance: str | TikzDimension | None = None,
        dash_pattern: str | None = None,
        dash_phase: str | None = None,
        # Pattern / shading
        pattern: _Pattern = None,
        pattern_color: ColorInput | None = None,
        shading: _Shading = None,
        shading_angle: float | None = None,
        left_color: ColorInput | None = None,
        right_color: ColorInput | None = None,
        top_color: ColorInput | None = None,
        bottom_color: ColorInput | None = None,
        inner_color: ColorInput | None = None,
        outer_color: ColorInput | None = None,
        ball_color: ColorInput | None = None,
        # Shape-specific
        regular_polygon_sides: int | None = None,
        star_points: int | None = None,
        star_point_ratio: float | None = None,
        star_point_height: str | None = None,
        # Shadow
        shadow_xshift: str | None = None,
        shadow_yshift: str | None = None,
        shadow_color: ColorInput | None = None,
        shadow_opacity: float | None = None,
        shadow_scale: float | None = None,
        # Pin / label on node
        pin: str | None = None,
        # Catch-all for unlisted TikZ options
        **kwargs: Any,
    ) -> Node:
        """Add a node to the TikZ figure.

        Args:
            x: X-coordinate, a ``(x, y)`` / ``(x, y, z)`` tuple, or a
                :class:`TikzCoordinate`. Use ``None`` for relatively
                positioned nodes.
            y: Y-coordinate. Use ``None`` when ``x`` already provides the
                full position.
            z: Z-coordinate for 3-D figures. Use ``None`` when ``x`` already
                provides the full position.
            label: Internal TikZ name. Auto-assigned when ``None``.
            content: Text or LaTeX content displayed inside the node.
            layer: Target layer index. Defaults to ``0``.
            comment: Optional comment prepended in the TikZ output.
            options: Flag-style TikZ options
                (e.g. ``["draw", "thick"]``).
            verbose: If ``True``, print a debug message.
            shape: Node shape
                (e.g. ``"circle"``, ``"rectangle"``, ``"diamond"``).
            color: Text color (e.g. ``"red"``, ``"blue!50"``).
            fill: Fill color.
            draw: Border/stroke color. Use ``"none"`` to hide the border.
            text: Alias for text color.
            opacity: Overall opacity (0–1).
            fill_opacity: Fill opacity (0–1).
            draw_opacity: Border opacity (0–1).
            text_opacity: Text opacity (0–1).
            minimum_width: Minimum node width (e.g. ``"2cm"``).
            minimum_height: Minimum node height.
            minimum_size: Minimum size in both dimensions.
            inner_sep: Inner separation between content and border.
            inner_xsep: Horizontal inner separation.
            inner_ysep: Vertical inner separation.
            outer_sep: Outer separation between border and anchors.
            outer_xsep: Horizontal outer separation.
            outer_ysep: Vertical outer separation.
            line_width: Border line width (e.g. ``"1pt"``).
            font: Font specification (e.g. ``"\\\\tiny"``).
            text_width: Text width for automatic line wrapping.
            text_height: Explicit text height.
            text_depth: Explicit text depth.
            align: Text alignment (``"left"``, ``"center"``, ``"right"``).
            anchor: Anchor point
                (e.g. ``"center"``, ``"north"``, ``"south west"``).
            above: Place above, with optional offset (e.g. ``"5pt"``).
            below: Place below.
            left: Place left.
            right: Place right.
            above_left: Place above-left.
            above_right: Place above-right.
            below_left: Place below-left.
            below_right: Place below-right.
            above_of: Place above a named node.
            below_of: Place below a named node.
            left_of: Place left of a named node.
            right_of: Place right of a named node.
            node_distance: Distance for relative positioning
                (e.g. ``"1cm"``).
            rotate: Rotation angle in degrees.
            xshift: Horizontal shift (e.g. ``"1cm"``).
            yshift: Vertical shift.
            scale: Uniform scaling factor.
            xscale: Horizontal scaling factor.
            yscale: Vertical scaling factor.
            xslant: Horizontal slant factor.
            yslant: Vertical slant factor.
            rounded_corners: Corner rounding radius (e.g. ``"3pt"``).
            double: Inner color for double borders.
            double_distance: Distance between double borders.
            dash_pattern: Custom dash pattern (e.g. ``"on 2pt off 3pt"``).
            dash_phase: Dash pattern starting offset.
            pattern: Fill pattern (e.g. ``"north east lines"``).
            pattern_color: Color for the fill pattern.
            shading: Shading type
                (``"axis"``, ``"radial"``, or ``"ball"``).
            shading_angle: Angle for axis shading.
            left_color: Left color for axis shading.
            right_color: Right color for axis shading.
            top_color: Top color for axis shading.
            bottom_color: Bottom color for axis shading.
            inner_color: Inner color for radial shading.
            outer_color: Outer color for radial shading.
            ball_color: Ball color for ball shading.
            regular_polygon_sides: Number of sides for
                ``shape="regular polygon"``.
            star_points: Number of points for ``shape="star"``.
            star_point_ratio: Inner-to-outer radius ratio for stars.
            star_point_height: Height of star points.
            shadow_xshift: Horizontal shadow shift.
            shadow_yshift: Vertical shadow shift.
            shadow_color: Shadow color.
            shadow_opacity: Shadow opacity (0–1).
            shadow_scale: Shadow scale factor.
            pin: Pin label specification (e.g. ``"above:text"``).
            **kwargs: Additional TikZ options. Underscores in keys become
                spaces (e.g. ``signal_from`` → ``signal from``).

        Returns:
            The :class:`Node` object that was added.
        """
        if isinstance(x, Node):
            has_extra_args = (
                y is not None
                or z is not None
                or label is not None
                or content != ""
                or layer != 0
                or comment is not None
                or options is not None
                or verbose
                or any(
                    value is not None
                    for value in (
                        shape,
                        color,
                        fill,
                        draw,
                        text,
                        opacity,
                        fill_opacity,
                        draw_opacity,
                        text_opacity,
                        minimum_width,
                        minimum_height,
                        minimum_size,
                        inner_sep,
                        inner_xsep,
                        inner_ysep,
                        outer_sep,
                        outer_xsep,
                        outer_ysep,
                        line_width,
                        font,
                        text_width,
                        text_height,
                        text_depth,
                        align,
                        anchor,
                        above,
                        below,
                        left,
                        right,
                        above_left,
                        above_right,
                        below_left,
                        below_right,
                        above_of,
                        below_of,
                        left_of,
                        right_of,
                        node_distance,
                        rotate,
                        xshift,
                        yshift,
                        scale,
                        xscale,
                        yscale,
                        xslant,
                        yslant,
                        rounded_corners,
                        double,
                        double_distance,
                        dash_pattern,
                        dash_phase,
                        pattern,
                        pattern_color,
                        shading,
                        shading_angle,
                        left_color,
                        right_color,
                        top_color,
                        bottom_color,
                        inner_color,
                        outer_color,
                        ball_color,
                        regular_polygon_sides,
                        star_points,
                        star_point_ratio,
                        star_point_height,
                        shadow_xshift,
                        shadow_yshift,
                        shadow_color,
                        shadow_opacity,
                        shadow_scale,
                        pin,
                    )
                )
                or bool(kwargs)
            )
            if has_extra_args:
                raise ValueError(
                    "When passing an existing Node to add_node(), do not also provide node-construction arguments."
                )
            node = x
            self._assign_auto_node_label(node)
            self._sync_node_counter_from_label(node.label)
            self.layers.add_item(item=node, layer=node.layer or 0, verbose=verbose)
            return node

        _params = locals().copy()
        _non_tikz = {
            "self",
            "x",
            "y",
            "z",
            "label",
            "content",
            "layer",
            "comment",
            "options",
            "verbose",
            "kwargs",
            "__class__",
        }

        tikz_kwargs = dict(kwargs)
        tikz_kwargs.update(
            {k: v for k, v in _params.items() if k not in _non_tikz and v is not None}
        )

        if options is None:
            options = []

        if isinstance(options, str):
            options = [options]

        label_from_x = label is None and isinstance(x, str) and y is None and z is None
        explicit_label = label not in (None, "")

        if label_from_x:
            assert isinstance(x, str)
            label = x
            x = None
            explicit_label = True

        if label is None:
            label = f"node{self._node_counter}"
            explicit_label = False
        node = Node(
            x=x,
            y=y,
            z=z,
            label=label,
            layer=layer,
            content=content,
            comment=comment,
            options=options,
            **tikz_kwargs,
        )
        node._user_supplied_label = explicit_label
        self._node_counter += 1
        self.layers.add_item(item=node, layer=layer, verbose=verbose)
        return node

    def midpoint(
        self,
        node1: "Node | str",
        node2: "Node | str",
        label: str | None = None,
        layer: int = 0,
        content: str = "",
        **kwargs: Any,
    ) -> Node:
        """Add a node at the midpoint between two existing nodes.

        Args:
            node1: First node object or its label string.
            node2: Second node object or its label string.
            label: Label for the new midpoint node. Auto-assigned when
                ``None``.
            layer: Target layer index. Defaults to ``0``.
            content: Text content for the midpoint node.
            **kwargs: Additional options forwarded to :meth:`add_node`.

        Returns:
            The new :class:`Node` placed at the computed midpoint.

        Raises:
            ValueError: If either node lacks explicit numeric coordinates.
        """
        node1_obj: Node | Coordinate = (
            self.layers.get_node(node1) if isinstance(node1, str) else node1
        )
        node2_obj: Node | Coordinate = (
            self.layers.get_node(node2) if isinstance(node2, str) else node2
        )

        if node1_obj.x is None or node1_obj.y is None:
            raise ValueError(
                f"Node '{node1_obj.label}' does not have explicit coordinates."
            )
        if node2_obj.x is None or node2_obj.y is None:
            raise ValueError(
                f"Node '{node2_obj.label}' does not have explicit coordinates."
            )

        mid_x = (node1_obj.x + node2_obj.x) / 2  # type: ignore[operator]
        mid_y = (node1_obj.y + node2_obj.y) / 2  # type: ignore[operator]

        if node1_obj.z is not None and node2_obj.z is not None:
            mid_z = (node1_obj.z + node2_obj.z) / 2  # type: ignore[operator]
        else:
            mid_z = None

        return self.add_node(
            x=mid_x,
            y=mid_y,
            z=mid_z,
            label=label,
            layer=layer,
            content=content,
            **kwargs,
        )

    def add_coordinate(
        self,
        label: str,
        x: (
            float
            | int
            | str
            | tuple[float | int | str, float | int | str]
            | tuple[float | int | str, float | int | str, float | int | str]
            | TikzCoordinate
            | None
        ) = None,
        y: float | int | str | None = None,
        z: float | int | str | None = None,
        at: str | None = None,
        layer: int = 0,
        comment: str | None = None,
        verbose: bool = False,
    ) -> Coordinate:
        """Add a named coordinate point using ``\\coordinate``.

        A coordinate is an invisible named point — lighter than a
        :class:`~tikzfigure.core.node.Node` because it has no box, content,
        or visible styling.  Use it to define reusable anchor points,
        midpoints, or expression-based positions that you can reference in
        paths and other commands.

        Either provide explicit coordinates, or a raw TikZ coordinate
        expression via ``at``.

        Examples::

            # Fixed point
            fig.add_coordinate("origin", (0, 0))
            fig.draw(["origin", "A"])

            # Midpoint using calc (add "calc" to extra_packages)
            fig.add_coordinate("mid", at="$(A)!0.5!(B)$")
            fig.draw(["A", "mid", "B"])

            # At a node anchor
            fig.add_coordinate("atip", at="A.north")

        Args:
            label: TikZ name for this coordinate.  Used when referencing
                it in path lists (e.g. ``["A", "mid", "B"]``).
            x: X-coordinate value, a ``(x, y)`` / ``(x, y, z)`` tuple, or a
                :class:`TikzCoordinate`. Must be provided together with ``y``
                when passed as a scalar. Mutually exclusive with ``at``.
            y: Y-coordinate value when passing explicit scalar coordinates.
                Mutually exclusive with ``at``.
            z: Z-coordinate value when passing explicit scalar coordinates.
                Mutually exclusive with ``at``.
            at: Raw TikZ coordinate expression.  Examples:

                * ``"$(A)!0.5!(B)$"`` — midpoint via ``calc`` library
                * ``"A.north"`` — at a node anchor
                * ``"30:2cm"`` — polar coordinates

                Parentheses are added automatically if absent.
                Mutually exclusive with ``x``/``y``.
            layer: Target layer index. Defaults to ``0``.
            comment: Optional comment prepended in the TikZ output.
            verbose: If ``True``, print a debug message after insertion.

        Returns:
            The newly created :class:`Coordinate` object.
        """
        coord = Coordinate(
            label=label,
            x=x,
            y=y,
            z=z,
            at=at,
            layer=layer,
            comment=comment,
        )
        self.layers.add_item(item=coord, layer=layer, verbose=verbose)
        return coord

    def add_variable(
        self,
        label: str,
        value: int | float | str,
        layer: int | None = 0,
        comment: str | None = None,
        verbose: bool = False,
    ) -> Variable:
        """Add a pgfmath variable (``\\pgfmathsetmacro``) to the figure.

        Variables are emitted at the top of the ``tikzpicture`` environment
        so they can be referenced anywhere in the figure.

        Args:
            label: Variable name (without the leading backslash).
            value: Numeric value or PGF math expression string to assign
                (e.g. ``5``, ``"sqrt(2)"``, ``"sin(60)"``).
            layer: Layer index (currently unused). Defaults to ``0``.
            comment: Optional comment prepended in the TikZ output.
            verbose: Unused; reserved for future debug output.

        Returns:
            The :class:`Variable` object that was added.
        """
        variable = Variable(
            label=label,
            value=value,
            layer=layer,
            comment=comment,
        )
        self._variables.append(variable)

        # TODO: Allow for special variables in each layer
        # self.layers.add_item(item=variable, layer=layer, verbose=verbose)
        return variable

    def declare_function(
        self,
        name: str,
        args: str | list[str] | tuple[str, ...],
        body: Any,
        comment: str | None = None,
        verbose: bool = False,
    ) -> DeclaredFunction:
        """Declare a reusable PGF math function for this figure."""
        declared = DeclaredFunction(name=name, args=args, body=body, comment=comment)
        self._declared_functions.append(declared)
        if verbose:
            print(f"Declared PGF function {name}")
        return declared

    def add_plot(
        self,
        x: Any,
        y: Any | None = None,
        *,
        variable: str = "x",
        domain: tuple[Any, Any] | str | None = None,
        samples: int | None = None,
        smooth: bool = False,
        layer: int = 0,
        comment: str | None = None,
        verbose: bool = False,
        options: OptionInput | None = None,
        tikz_command: str = "draw",
        **kwargs: Any,
    ) -> TikzPlot:
        """Add a plain TikZ expression plot outside a pgfplots axis."""
        plot = TikzPlot(
            x=x,
            y=y,
            variable=variable,
            domain=domain,
            samples=samples,
            smooth=smooth,
            layer=layer,
            comment=comment,
            options=options,
            tikz_command=tikz_command,
            **kwargs,
        )
        self.layers.add_item(item=plot, layer=layer, verbose=verbose)
        return plot

    def add_raw(
        self,
        tikz_code: str,
        layer: int = 0,
        verbose: bool = False,
    ) -> RawTikz:
        """Insert a verbatim TikZ code block into the figure.

        Args:
            tikz_code: Raw TikZ source to include verbatim.
            layer: Target layer index. Defaults to ``0``.
            verbose: If ``True``, print a debug message after insertion.

        Returns:
            The :class:`RawTikz` object that was added.
        """
        raw_tikz = RawTikz(tikz_code=tikz_code)

        self.layers.add_item(
            item=raw_tikz,
            layer=layer,
            verbose=verbose,
        )
        return raw_tikz

    def arc(
        self,
        start: PositionInput,
        start_angle: float,
        end_angle: float,
        radius: float | str,
        layer: int = 0,
        comment: str | None = None,
        verbose: bool = False,
        # Color
        color: ColorInput | None = None,
        fill: ColorInput | None = None,
        draw: ColorInput | None = None,
        text: ColorInput | None = None,
        # Opacity
        opacity: float | None = None,
        draw_opacity: float | None = None,
        fill_opacity: float | None = None,
        text_opacity: float | None = None,
        # Line width
        line_width: str | None = None,
        # Line style
        line_cap: _LineCap = None,
        line_join: _LineJoin = None,
        miter_limit: float | None = None,
        # Dash
        dash_pattern: str | None = None,
        dash_phase: str | None = None,
        # Arrow specification
        arrows: ArrowInput | None = None,
        # Transformations
        rotate: float | None = None,
        xshift: str | None = None,
        yshift: str | None = None,
        scale: float | None = None,
        xscale: float | None = None,
        yscale: float | None = None,
        # Catch-all for unlisted TikZ options
        **kwargs: Any,
    ) -> Arc:
        """Add an arc to the figure.

        Args:
            start: Starting coordinate as an ``(x, y)`` / ``(x, y, z)`` tuple or
                :class:`TikzCoordinate`.
            start_angle: Start angle in degrees.
            end_angle: End angle in degrees.
            radius: Radius of the arc (e.g. ``"3mm"``, ``0.5``).
            layer: Target layer index. Defaults to ``0``.
            comment: Optional comment prepended in the TikZ output.
            verbose: If ``True``, print a debug message.
            color: Line color (e.g. ``"red"``, ``"blue!50"``).
            fill: Fill color for the enclosed area.
            draw: Stroke color when different from *color*.
            text: Text color.
            opacity: Overall opacity (0–1).
            draw_opacity: Stroke opacity (0–1).
            fill_opacity: Fill opacity (0–1).
            text_opacity: Text opacity (0–1).
            line_width: Line width (e.g. ``"1pt"``).
            line_cap: Line cap style: ``"butt"``, ``"rect"``, or
                ``"round"``.
            line_join: Line join style: ``"miter"``, ``"bevel"``, or
                ``"round"``.
            miter_limit: Miter limit factor for miter joins.
            dash_pattern: Custom dash pattern (e.g. ``"on 2pt off 3pt"``).
            dash_phase: Dash pattern starting offset (e.g. ``"2pt"``).
            arrows: Arrow specification (e.g. ``"->"``, ``"<->"``, ``"*-*"``).
            rotate: Rotation angle in degrees.
            xshift: Horizontal shift (e.g. ``"1cm"``).
            yshift: Vertical shift (e.g. ``"1cm"``).
            scale: Uniform scaling factor.
            xscale: Horizontal scaling factor.
            yscale: Vertical scaling factor.
            **kwargs: Catch-all for unlisted TikZ options.

        Returns:
            The :class:`Arc` object that was added.
        """
        options: list[_Option] = []
        if arrows:
            options.append(arrows)

        arc_kwargs: dict[str, Any] = {}
        if color is not None:
            arc_kwargs["color"] = color
        if fill is not None:
            arc_kwargs["fill"] = fill
        if draw is not None:
            arc_kwargs["draw"] = draw
        if text is not None:
            arc_kwargs["text"] = text
        if opacity is not None:
            arc_kwargs["opacity"] = opacity
        if draw_opacity is not None:
            arc_kwargs["draw_opacity"] = draw_opacity
        if fill_opacity is not None:
            arc_kwargs["fill_opacity"] = fill_opacity
        if text_opacity is not None:
            arc_kwargs["text_opacity"] = text_opacity
        if line_width is not None:
            arc_kwargs["line_width"] = line_width
        if line_cap is not None:
            arc_kwargs["line_cap"] = line_cap
        if line_join is not None:
            arc_kwargs["line_join"] = line_join
        if miter_limit is not None:
            arc_kwargs["miter_limit"] = miter_limit
        if dash_pattern is not None:
            arc_kwargs["dash_pattern"] = dash_pattern
        if dash_phase is not None:
            arc_kwargs["dash_phase"] = dash_phase
        if rotate is not None:
            arc_kwargs["rotate"] = rotate
        if xshift is not None:
            arc_kwargs["xshift"] = xshift
        if yshift is not None:
            arc_kwargs["yshift"] = yshift
        if scale is not None:
            arc_kwargs["scale"] = scale
        if xscale is not None:
            arc_kwargs["xscale"] = xscale
        if yscale is not None:
            arc_kwargs["yscale"] = yscale

        arc_kwargs.update(kwargs)

        arc = Arc(
            start=start,
            start_angle=start_angle,
            end_angle=end_angle,
            radius=radius,
            comment=comment,
            layer=layer,
            options=options,
            **arc_kwargs,
        )

        self.layers.add_item(item=arc, layer=layer, verbose=verbose)
        return arc

    def circle(
        self,
        center: PositionInput,
        radius: float | str,
        layer: int = 0,
        comment: str | None = None,
        verbose: bool = False,
        # Color
        color: ColorInput | None = None,
        fill: ColorInput | None = None,
        draw: ColorInput | None = None,
        text: ColorInput | None = None,
        # Opacity
        opacity: float | None = None,
        draw_opacity: float | None = None,
        fill_opacity: float | None = None,
        text_opacity: float | None = None,
        # Line width
        line_width: str | None = None,
        # Line style
        line_cap: _LineCap = None,
        line_join: _LineJoin = None,
        miter_limit: float | None = None,
        # Dash
        dash_pattern: str | None = None,
        dash_phase: str | None = None,
        # Transformations
        rotate: float | None = None,
        xshift: str | None = None,
        yshift: str | None = None,
        scale: float | None = None,
        xscale: float | None = None,
        yscale: float | None = None,
        # Catch-all for unlisted TikZ options
        **kwargs: Any,
    ) -> Circle:
        """Add a circle to the figure.

        Args:
            center: Center coordinate as an ``(x, y)`` / ``(x, y, z)`` tuple or
                :class:`TikzCoordinate`.
            radius: Radius of the circle (e.g. ``"5mm"``, ``1.0``).
            layer: Target layer index. Defaults to ``0``.
            comment: Optional comment prepended in the TikZ output.
            verbose: If ``True``, print a debug message.
            color: Line color (e.g. ``"red"``, ``"blue!50"``).
            fill: Fill color for the circle.
            draw: Stroke color when different from *color*.
            text: Text color.
            opacity: Overall opacity (0–1).
            draw_opacity: Stroke opacity (0–1).
            fill_opacity: Fill opacity (0–1).
            text_opacity: Text opacity (0–1).
            line_width: Line width (e.g. ``"1pt"``).
            line_cap: Line cap style: ``"butt"``, ``"rect"``, or
                ``"round"``.
            line_join: Line join style: ``"miter"``, ``"bevel"``, or
                ``"round"``.
            miter_limit: Miter limit factor for miter joins.
            dash_pattern: Custom dash pattern (e.g. ``"on 2pt off 3pt"``).
            dash_phase: Dash pattern starting offset (e.g. ``"2pt"``).
            rotate: Rotation angle in degrees.
            xshift: Horizontal shift (e.g. ``"1cm"``).
            yshift: Vertical shift (e.g. ``"1cm"``).
            scale: Uniform scaling factor.
            xscale: Horizontal scaling factor.
            yscale: Vertical scaling factor.
            **kwargs: Catch-all for unlisted TikZ options.

        Returns:
            The :class:`Circle` object that was added.
        """
        circle_kwargs: dict[str, Any] = {}
        if color is not None:
            circle_kwargs["color"] = color
        if fill is not None:
            circle_kwargs["fill"] = fill
        if draw is not None:
            circle_kwargs["draw"] = draw
        if text is not None:
            circle_kwargs["text"] = text
        if opacity is not None:
            circle_kwargs["opacity"] = opacity
        if draw_opacity is not None:
            circle_kwargs["draw_opacity"] = draw_opacity
        if fill_opacity is not None:
            circle_kwargs["fill_opacity"] = fill_opacity
        if text_opacity is not None:
            circle_kwargs["text_opacity"] = text_opacity
        if line_width is not None:
            circle_kwargs["line_width"] = line_width
        if line_cap is not None:
            circle_kwargs["line_cap"] = line_cap
        if line_join is not None:
            circle_kwargs["line_join"] = line_join
        if miter_limit is not None:
            circle_kwargs["miter_limit"] = miter_limit
        if dash_pattern is not None:
            circle_kwargs["dash_pattern"] = dash_pattern
        if dash_phase is not None:
            circle_kwargs["dash_phase"] = dash_phase
        if rotate is not None:
            circle_kwargs["rotate"] = rotate
        if xshift is not None:
            circle_kwargs["xshift"] = xshift
        if yshift is not None:
            circle_kwargs["yshift"] = yshift
        if scale is not None:
            circle_kwargs["scale"] = scale
        if xscale is not None:
            circle_kwargs["xscale"] = xscale
        if yscale is not None:
            circle_kwargs["yscale"] = yscale

        circle_kwargs.update(kwargs)

        circle = Circle(
            center=center,
            radius=radius,
            comment=comment,
            layer=layer,
            options=[],
            **circle_kwargs,
        )

        self.layers.add_item(item=circle, layer=layer, verbose=verbose)
        return circle

    def rectangle(
        self,
        corner1: PositionInput,
        corner2: PositionInput,
        layer: int = 0,
        comment: str | None = None,
        verbose: bool = False,
        # Color
        color: ColorInput | None = None,
        fill: ColorInput | None = None,
        draw: ColorInput | None = None,
        text: ColorInput | None = None,
        # Opacity
        opacity: float | None = None,
        draw_opacity: float | None = None,
        fill_opacity: float | None = None,
        text_opacity: float | None = None,
        # Line width
        line_width: str | None = None,
        # Line style
        line_cap: _LineCap = None,
        line_join: _LineJoin = None,
        miter_limit: float | None = None,
        # Dash
        dash_pattern: str | None = None,
        dash_phase: str | None = None,
        # Rounded corners
        rounded_corners: str | None = None,
        # Transformations
        rotate: float | None = None,
        xshift: str | None = None,
        yshift: str | None = None,
        scale: float | None = None,
        xscale: float | None = None,
        yscale: float | None = None,
        # Catch-all for unlisted TikZ options
        **kwargs: Any,
    ) -> Rectangle:
        """Add a rectangle to the figure.

        Args:
            corner1: First corner as an ``(x, y)`` / ``(x, y, z)`` tuple or
                :class:`TikzCoordinate`.
            corner2: Opposite corner as an ``(x, y)`` / ``(x, y, z)`` tuple or
                :class:`TikzCoordinate`.
            layer: Target layer index. Defaults to ``0``.
            comment: Optional comment prepended in the TikZ output.
            verbose: If ``True``, print a debug message.
            color: Line color (e.g. ``"red"``, ``"blue!50"``).
            fill: Fill color for the rectangle.
            draw: Stroke color when different from *color*.
            text: Text color.
            opacity: Overall opacity (0–1).
            draw_opacity: Stroke opacity (0–1).
            fill_opacity: Fill opacity (0–1).
            text_opacity: Text opacity (0–1).
            line_width: Line width (e.g. ``"1pt"``).
            line_cap: Line cap style: ``"butt"``, ``"rect"``, or ``"round"``.
            line_join: Line join style: ``"miter"``, ``"bevel"``, or ``"round"``.
            miter_limit: Miter limit factor for miter joins.
            dash_pattern: Custom dash pattern (e.g. ``"on 2pt off 3pt"``).
            dash_phase: Dash pattern starting offset (e.g. ``"2pt"``).
            rounded_corners: Corner rounding radius (e.g. ``"5pt"``).
            rotate: Rotation angle in degrees.
            xshift: Horizontal shift (e.g. ``"1cm"``).
            yshift: Vertical shift (e.g. ``"1cm"``).
            scale: Uniform scaling factor.
            xscale: Horizontal scaling factor.
            yscale: Vertical scaling factor.
            **kwargs: Catch-all for unlisted TikZ options.

        Returns:
            The :class:`Rectangle` object that was added.
        """
        rect_kwargs: dict[str, Any] = {}
        if color is not None:
            rect_kwargs["color"] = color
        if fill is not None:
            rect_kwargs["fill"] = fill
        if draw is not None:
            rect_kwargs["draw"] = draw
        if text is not None:
            rect_kwargs["text"] = text
        if opacity is not None:
            rect_kwargs["opacity"] = opacity
        if draw_opacity is not None:
            rect_kwargs["draw_opacity"] = draw_opacity
        if fill_opacity is not None:
            rect_kwargs["fill_opacity"] = fill_opacity
        if text_opacity is not None:
            rect_kwargs["text_opacity"] = text_opacity
        if line_width is not None:
            rect_kwargs["line_width"] = line_width
        if line_cap is not None:
            rect_kwargs["line_cap"] = line_cap
        if line_join is not None:
            rect_kwargs["line_join"] = line_join
        if miter_limit is not None:
            rect_kwargs["miter_limit"] = miter_limit
        if dash_pattern is not None:
            rect_kwargs["dash_pattern"] = dash_pattern
        if dash_phase is not None:
            rect_kwargs["dash_phase"] = dash_phase
        if rounded_corners is not None:
            rect_kwargs["rounded_corners"] = rounded_corners
        if rotate is not None:
            rect_kwargs["rotate"] = rotate
        if xshift is not None:
            rect_kwargs["xshift"] = xshift
        if yshift is not None:
            rect_kwargs["yshift"] = yshift
        if scale is not None:
            rect_kwargs["scale"] = scale
        if xscale is not None:
            rect_kwargs["xscale"] = xscale
        if yscale is not None:
            rect_kwargs["yscale"] = yscale

        rect_kwargs.update(kwargs)

        rectangle = Rectangle(
            corner1=corner1,
            corner2=corner2,
            comment=comment,
            layer=layer,
            options=[],
            **rect_kwargs,
        )

        self.layers.add_item(item=rectangle, layer=layer, verbose=verbose)
        return rectangle

    def ellipse(
        self,
        center: PositionInput,
        x_radius: float | str,
        y_radius: float | str,
        layer: int = 0,
        comment: str | None = None,
        verbose: bool = False,
        # Color
        color: ColorInput | None = None,
        fill: ColorInput | None = None,
        draw: ColorInput | None = None,
        text: ColorInput | None = None,
        # Opacity
        opacity: float | None = None,
        draw_opacity: float | None = None,
        fill_opacity: float | None = None,
        text_opacity: float | None = None,
        # Line width
        line_width: str | None = None,
        # Line style
        line_cap: _LineCap = None,
        line_join: _LineJoin = None,
        miter_limit: float | None = None,
        # Dash
        dash_pattern: str | None = None,
        dash_phase: str | None = None,
        # Transformations
        rotate: float | None = None,
        xshift: str | None = None,
        yshift: str | None = None,
        scale: float | None = None,
        xscale: float | None = None,
        yscale: float | None = None,
        # Catch-all for unlisted TikZ options
        **kwargs: Any,
    ) -> Ellipse:
        """Add an ellipse to the figure.

        Args:
            center: Center coordinate as an ``(x, y)`` / ``(x, y, z)`` tuple or
                :class:`TikzCoordinate`.
            x_radius: Horizontal radius (e.g. ``"2cm"``, ``1.5``).
            y_radius: Vertical radius (e.g. ``"1cm"``, ``0.75``).
            layer: Target layer index. Defaults to ``0``.
            comment: Optional comment prepended in the TikZ output.
            verbose: If ``True``, print a debug message.
            color: Line color (e.g. ``"red"``, ``"blue!50"``).
            fill: Fill color for the ellipse.
            draw: Stroke color when different from *color*.
            text: Text color.
            opacity: Overall opacity (0–1).
            draw_opacity: Stroke opacity (0–1).
            fill_opacity: Fill opacity (0–1).
            text_opacity: Text opacity (0–1).
            line_width: Line width (e.g. ``"1pt"``).
            line_cap: Line cap style: ``"butt"``, ``"rect"``, or ``"round"``.
            line_join: Line join style: ``"miter"``, ``"bevel"``, or ``"round"``.
            miter_limit: Miter limit factor for miter joins.
            dash_pattern: Custom dash pattern (e.g. ``"on 2pt off 3pt"``).
            dash_phase: Dash pattern starting offset (e.g. ``"2pt"``).
            rotate: Rotation angle in degrees.
            xshift: Horizontal shift (e.g. ``"1cm"``).
            yshift: Vertical shift (e.g. ``"1cm"``).
            scale: Uniform scaling factor.
            xscale: Horizontal scaling factor.
            yscale: Vertical scaling factor.
            **kwargs: Catch-all for unlisted TikZ options.

        Returns:
            The :class:`Ellipse` object that was added.
        """
        ellipse_kwargs: dict[str, Any] = {}
        if color is not None:
            ellipse_kwargs["color"] = color
        if fill is not None:
            ellipse_kwargs["fill"] = fill
        if draw is not None:
            ellipse_kwargs["draw"] = draw
        if text is not None:
            ellipse_kwargs["text"] = text
        if opacity is not None:
            ellipse_kwargs["opacity"] = opacity
        if draw_opacity is not None:
            ellipse_kwargs["draw_opacity"] = draw_opacity
        if fill_opacity is not None:
            ellipse_kwargs["fill_opacity"] = fill_opacity
        if text_opacity is not None:
            ellipse_kwargs["text_opacity"] = text_opacity
        if line_width is not None:
            ellipse_kwargs["line_width"] = line_width
        if line_cap is not None:
            ellipse_kwargs["line_cap"] = line_cap
        if line_join is not None:
            ellipse_kwargs["line_join"] = line_join
        if miter_limit is not None:
            ellipse_kwargs["miter_limit"] = miter_limit
        if dash_pattern is not None:
            ellipse_kwargs["dash_pattern"] = dash_pattern
        if dash_phase is not None:
            ellipse_kwargs["dash_phase"] = dash_phase
        if rotate is not None:
            ellipse_kwargs["rotate"] = rotate
        if xshift is not None:
            ellipse_kwargs["xshift"] = xshift
        if yshift is not None:
            ellipse_kwargs["yshift"] = yshift
        if scale is not None:
            ellipse_kwargs["scale"] = scale
        if xscale is not None:
            ellipse_kwargs["xscale"] = xscale
        if yscale is not None:
            ellipse_kwargs["yscale"] = yscale

        ellipse_kwargs.update(kwargs)

        ellipse = Ellipse(
            center=center,
            x_radius=x_radius,
            y_radius=y_radius,
            comment=comment,
            layer=layer,
            options=[],
            **ellipse_kwargs,
        )

        self.layers.add_item(item=ellipse, layer=layer, verbose=verbose)
        return ellipse

    def grid(
        self,
        corner1: PositionInput,
        corner2: PositionInput,
        step: str | None = None,
        layer: int = 0,
        comment: str | None = None,
        verbose: bool = False,
        # Color
        color: ColorInput | None = None,
        # Opacity
        opacity: float | None = None,
        draw_opacity: float | None = None,
        # Line width
        line_width: str | None = None,
        # Line style
        line_cap: _LineCap = None,
        line_join: _LineJoin = None,
        # Dash
        dash_pattern: str | None = None,
        dash_phase: str | None = None,
        # Transformations
        rotate: float | None = None,
        xshift: str | None = None,
        yshift: str | None = None,
        scale: float | None = None,
        xscale: float | None = None,
        yscale: float | None = None,
        # Catch-all for unlisted TikZ options
        **kwargs: Any,
    ) -> Grid:
        """Add a grid to the figure.

        Args:
            corner1: First corner as an ``(x, y)`` / ``(x, y, z)`` tuple or
                :class:`TikzCoordinate`.
            corner2: Opposite corner as an ``(x, y)`` / ``(x, y, z)`` tuple or
                :class:`TikzCoordinate`.
            step: Grid step size (e.g. ``"1cm"`` for uniform, or
                ``"0.5cm,1cm"`` for different x/y steps). Defaults to ``None``
                (TikZ default of 1cm).
            layer: Target layer index. Defaults to ``0``.
            comment: Optional comment prepended in the TikZ output.
            verbose: If ``True``, print a debug message.
            color: Line color (e.g. ``"red"``, ``"gray!30"``).
            opacity: Overall opacity (0–1).
            draw_opacity: Stroke opacity (0–1).
            line_width: Line width (e.g. ``"0.5pt"``).
            line_cap: Line cap style: ``"butt"``, ``"rect"``, or ``"round"``.
            line_join: Line join style: ``"miter"``, ``"bevel"``, or ``"round"``.
            dash_pattern: Custom dash pattern (e.g. ``"on 1pt off 1pt"``).
            dash_phase: Dash pattern starting offset (e.g. ``"1pt"``).
            rotate: Rotation angle in degrees.
            xshift: Horizontal shift (e.g. ``"1cm"``).
            yshift: Vertical shift (e.g. ``"1cm"``).
            scale: Uniform scaling factor.
            xscale: Horizontal scaling factor.
            yscale: Vertical scaling factor.
            **kwargs: Catch-all for unlisted TikZ options.

        Returns:
            The :class:`Grid` object that was added.
        """
        grid_kwargs: dict[str, Any] = {}
        if color is not None:
            grid_kwargs["color"] = color
        if opacity is not None:
            grid_kwargs["opacity"] = opacity
        if draw_opacity is not None:
            grid_kwargs["draw_opacity"] = draw_opacity
        if line_width is not None:
            grid_kwargs["line_width"] = line_width
        if line_cap is not None:
            grid_kwargs["line_cap"] = line_cap
        if line_join is not None:
            grid_kwargs["line_join"] = line_join
        if dash_pattern is not None:
            grid_kwargs["dash_pattern"] = dash_pattern
        if dash_phase is not None:
            grid_kwargs["dash_phase"] = dash_phase
        if rotate is not None:
            grid_kwargs["rotate"] = rotate
        if xshift is not None:
            grid_kwargs["xshift"] = xshift
        if yshift is not None:
            grid_kwargs["yshift"] = yshift
        if scale is not None:
            grid_kwargs["scale"] = scale
        if xscale is not None:
            grid_kwargs["xscale"] = xscale
        if yscale is not None:
            grid_kwargs["yscale"] = yscale

        grid_kwargs.update(kwargs)

        grid_obj = Grid(
            corner1=corner1,
            corner2=corner2,
            step=step,
            comment=comment,
            layer=layer,
            options=[],
            **grid_kwargs,
        )

        self.layers.add_item(item=grid_obj, layer=layer, verbose=verbose)
        return grid_obj

    def parabola(
        self,
        start: PositionInput,
        end: PositionInput,
        bend: PositionInput | None = None,
        layer: int = 0,
        comment: str | None = None,
        verbose: bool = False,
        # Color
        color: ColorInput | None = None,
        fill: ColorInput | None = None,
        draw: ColorInput | None = None,
        text: ColorInput | None = None,
        # Opacity
        opacity: float | None = None,
        draw_opacity: float | None = None,
        fill_opacity: float | None = None,
        text_opacity: float | None = None,
        # Line width
        line_width: str | None = None,
        # Line style
        line_cap: _LineCap = None,
        line_join: _LineJoin = None,
        miter_limit: float | None = None,
        # Dash
        dash_pattern: str | None = None,
        dash_phase: str | None = None,
        # Arrow specification
        arrows: ArrowInput | None = None,
        # Transformations
        rotate: float | None = None,
        xshift: str | None = None,
        yshift: str | None = None,
        scale: float | None = None,
        xscale: float | None = None,
        yscale: float | None = None,
        # Catch-all for unlisted TikZ options
        **kwargs: Any,
    ) -> Parabola:
        """Add a parabola to the figure.

        Args:
            start: Starting coordinate as an ``(x, y)`` / ``(x, y, z)`` tuple or
                :class:`TikzCoordinate`.
            end: Ending coordinate as an ``(x, y)`` / ``(x, y, z)`` tuple or
                :class:`TikzCoordinate`.
            bend: Bend point as an ``(x, y)`` / ``(x, y, z)`` tuple or
                :class:`TikzCoordinate`. If None, uses TikZ default.
            layer: Target layer index. Defaults to ``0``.
            comment: Optional comment prepended in the TikZ output.
            verbose: If ``True``, print a debug message.
            color: Line color (e.g. ``"red"``, ``"blue!50"``).
            fill: Fill color for the parabola.
            draw: Stroke color when different from *color*.
            text: Text color.
            opacity: Overall opacity (0–1).
            draw_opacity: Stroke opacity (0–1).
            fill_opacity: Fill opacity (0–1).
            text_opacity: Text opacity (0–1).
            line_width: Line width (e.g. ``"1pt"``).
            line_cap: Line cap style: ``"butt"``, ``"rect"``, or ``"round"``.
            line_join: Line join style: ``"miter"``, ``"bevel"``, or ``"round"``.
            miter_limit: Miter limit factor for miter joins.
            dash_pattern: Custom dash pattern (e.g. ``"on 2pt off 3pt"``).
            dash_phase: Dash pattern starting offset (e.g. ``"2pt"``).
            arrows: Arrow specification (e.g. ``"->"``, ``"<->"``, ``"*-*"``).
            rotate: Rotation angle in degrees.
            xshift: Horizontal shift (e.g. ``"1cm"``).
            yshift: Vertical shift (e.g. ``"1cm"``).
            scale: Uniform scaling factor.
            xscale: Horizontal scaling factor.
            yscale: Vertical scaling factor.
            **kwargs: Catch-all for unlisted TikZ options.

        Returns:
            The :class:`Parabola` object that was added.
        """
        options: list[_Option] = []
        if arrows:
            options.append(arrows)

        parabola_kwargs: dict[str, Any] = {}
        if color is not None:
            parabola_kwargs["color"] = color
        if fill is not None:
            parabola_kwargs["fill"] = fill
        if draw is not None:
            parabola_kwargs["draw"] = draw
        if text is not None:
            parabola_kwargs["text"] = text
        if opacity is not None:
            parabola_kwargs["opacity"] = opacity
        if draw_opacity is not None:
            parabola_kwargs["draw_opacity"] = draw_opacity
        if fill_opacity is not None:
            parabola_kwargs["fill_opacity"] = fill_opacity
        if text_opacity is not None:
            parabola_kwargs["text_opacity"] = text_opacity
        if line_width is not None:
            parabola_kwargs["line_width"] = line_width
        if line_cap is not None:
            parabola_kwargs["line_cap"] = line_cap
        if line_join is not None:
            parabola_kwargs["line_join"] = line_join
        if miter_limit is not None:
            parabola_kwargs["miter_limit"] = miter_limit
        if dash_pattern is not None:
            parabola_kwargs["dash_pattern"] = dash_pattern
        if dash_phase is not None:
            parabola_kwargs["dash_phase"] = dash_phase
        if rotate is not None:
            parabola_kwargs["rotate"] = rotate
        if xshift is not None:
            parabola_kwargs["xshift"] = xshift
        if yshift is not None:
            parabola_kwargs["yshift"] = yshift
        if scale is not None:
            parabola_kwargs["scale"] = scale
        if xscale is not None:
            parabola_kwargs["xscale"] = xscale
        if yscale is not None:
            parabola_kwargs["yscale"] = yscale

        parabola_kwargs.update(kwargs)

        parabola = Parabola(
            start=start,
            end=end,
            bend=bend,
            comment=comment,
            layer=layer,
            options=options,
            **parabola_kwargs,
        )

        self.layers.add_item(item=parabola, layer=layer, verbose=verbose)
        return parabola

    def line(
        self,
        start: PositionInput,
        end: PositionInput,
        layer: int = 0,
        comment: str | None = None,
        verbose: bool = False,
        options: OptionInput | None = None,
        # Color
        color: ColorInput | None = None,
        text: ColorInput | None = None,
        # Opacity
        opacity: float | None = None,
        draw_opacity: float | None = None,
        # Line width
        line_width: str | None = None,
        # Line style
        line_cap: _LineCap = None,
        line_join: _LineJoin = None,
        miter_limit: float | None = None,
        # Dash
        dash_pattern: str | None = None,
        dash_phase: str | None = None,
        # Arrow specification
        arrows: ArrowInput | None = None,
        # Transformations
        rotate: float | None = None,
        xshift: str | None = None,
        yshift: str | None = None,
        scale: float | None = None,
        xscale: float | None = None,
        yscale: float | None = None,
        # Catch-all for unlisted TikZ options
        **kwargs: Any,
    ) -> Line:
        """Add a line segment to the figure.

        Args:
            start: Starting point as an ``(x, y)`` / ``(x, y, z)`` tuple or
                :class:`TikzCoordinate`.
            end: Ending point as an ``(x, y)`` / ``(x, y, z)`` tuple or
                :class:`TikzCoordinate`.
            layer: Target layer index. Defaults to ``0``.
            comment: Optional comment prepended in the TikZ output.
            verbose: If ``True``, print a debug message.
            options: Flag-style TikZ options without values
                (e.g. ``["dashed", "thick"]``).
            color: Line color (e.g. ``"red"``, ``"blue!50"``).
            text: Text color.
            opacity: Overall opacity (0–1).
            draw_opacity: Stroke opacity (0–1).
            line_width: Line width (e.g. ``"1pt"``).
            line_cap: Line cap style: ``"butt"``, ``"rect"``, or ``"round"``.
            line_join: Line join style: ``"miter"``, ``"bevel"``, or ``"round"``.
            miter_limit: Miter limit factor for miter joins.
            dash_pattern: Custom dash pattern (e.g. ``"on 2pt off 3pt"``).
            dash_phase: Dash pattern starting offset (e.g. ``"2pt"``).
            arrows: Arrow specification (e.g. ``"->"``, ``"<->"``, ``"*-*"``).
            rotate: Rotation angle in degrees.
            xshift: Horizontal shift (e.g. ``"1cm"``).
            yshift: Vertical shift (e.g. ``"1cm"``).
            scale: Uniform scaling factor.
            xscale: Horizontal scaling factor.
            yscale: Vertical scaling factor.
            **kwargs: Catch-all for unlisted TikZ options.

        Returns:
            The :class:`Line` object that was added.
        """
        normalized_options = normalize_options(options)
        if arrows:
            normalized_options.append(arrows)

        line_kwargs: dict[str, Any] = {}
        if color is not None:
            line_kwargs["color"] = color
        if text is not None:
            line_kwargs["text"] = text
        if opacity is not None:
            line_kwargs["opacity"] = opacity
        if draw_opacity is not None:
            line_kwargs["draw_opacity"] = draw_opacity
        if line_width is not None:
            line_kwargs["line_width"] = line_width
        if line_cap is not None:
            line_kwargs["line_cap"] = line_cap
        if line_join is not None:
            line_kwargs["line_join"] = line_join
        if miter_limit is not None:
            line_kwargs["miter_limit"] = miter_limit
        if dash_pattern is not None:
            line_kwargs["dash_pattern"] = dash_pattern
        if dash_phase is not None:
            line_kwargs["dash_phase"] = dash_phase
        if rotate is not None:
            line_kwargs["rotate"] = rotate
        if xshift is not None:
            line_kwargs["xshift"] = xshift
        if yshift is not None:
            line_kwargs["yshift"] = yshift
        if scale is not None:
            line_kwargs["scale"] = scale
        if xscale is not None:
            line_kwargs["xscale"] = xscale
        if yscale is not None:
            line_kwargs["yscale"] = yscale

        line_kwargs.update(kwargs)

        line = Line(
            start=start,
            end=end,
            comment=comment,
            layer=layer,
            options=normalized_options,
            **line_kwargs,
        )

        self.layers.add_item(item=line, layer=layer, verbose=verbose)
        return line

    def polygon(
        self,
        center: PositionInput,
        radius: float | str,
        sides: int,
        rotation: float = 0,
        layer: int = 0,
        comment: str | None = None,
        verbose: bool = False,
        # Color
        color: ColorInput | None = None,
        fill: ColorInput | None = None,
        draw: ColorInput | None = None,
        text: ColorInput | None = None,
        # Opacity
        opacity: float | None = None,
        draw_opacity: float | None = None,
        fill_opacity: float | None = None,
        text_opacity: float | None = None,
        # Line width
        line_width: str | None = None,
        # Line style
        line_cap: _LineCap = None,
        line_join: _LineJoin = None,
        miter_limit: float | None = None,
        # Dash
        dash_pattern: str | None = None,
        dash_phase: str | None = None,
        # Transformations
        rotate: float | None = None,
        xshift: str | None = None,
        yshift: str | None = None,
        scale: float | None = None,
        xscale: float | None = None,
        yscale: float | None = None,
        # Catch-all for unlisted TikZ options
        **kwargs: Any,
    ) -> Polygon:
        """Add a regular polygon to the figure.

        Args:
            center: Center coordinate as an ``(x, y)`` / ``(x, y, z)`` tuple or
                :class:`TikzCoordinate`.
            radius: Distance from center to vertices.
            sides: Number of sides (must be >= 3).
            rotation: Rotation angle in degrees. Defaults to ``0``.
            layer: Target layer index. Defaults to ``0``.
            comment: Optional comment prepended in the TikZ output.
            verbose: If ``True``, print a debug message.
            color: Line color (e.g. ``"red"``, ``"blue!50"``).
            fill: Fill color for the polygon.
            draw: Stroke color when different from *color*.
            text: Text color.
            opacity: Overall opacity (0–1).
            draw_opacity: Stroke opacity (0–1).
            fill_opacity: Fill opacity (0–1).
            text_opacity: Text opacity (0–1).
            line_width: Line width (e.g. ``"1pt"``).
            line_cap: Line cap style: ``"butt"``, ``"rect"``, or ``"round"``.
            line_join: Line join style: ``"miter"``, ``"bevel"``, or ``"round"``.
            miter_limit: Miter limit factor for miter joins.
            dash_pattern: Custom dash pattern (e.g. ``"on 2pt off 3pt"``).
            dash_phase: Dash pattern starting offset (e.g. ``"2pt"``).
            rotate: Rotation angle in degrees.
            xshift: Horizontal shift (e.g. ``"1cm"``).
            yshift: Vertical shift (e.g. ``"1cm"``).
            scale: Uniform scaling factor.
            xscale: Horizontal scaling factor.
            yscale: Vertical scaling factor.
            **kwargs: Catch-all for unlisted TikZ options.

        Returns:
            The :class:`Polygon` object that was added.
        """
        if sides < 3:
            raise ValueError("Polygon must have at least 3 sides")

        polygon_kwargs: dict[str, Any] = {}
        if color is not None:
            polygon_kwargs["color"] = color
        if fill is not None:
            polygon_kwargs["fill"] = fill
        if draw is not None:
            polygon_kwargs["draw"] = draw
        if text is not None:
            polygon_kwargs["text"] = text
        if opacity is not None:
            polygon_kwargs["opacity"] = opacity
        if draw_opacity is not None:
            polygon_kwargs["draw_opacity"] = draw_opacity
        if fill_opacity is not None:
            polygon_kwargs["fill_opacity"] = fill_opacity
        if text_opacity is not None:
            polygon_kwargs["text_opacity"] = text_opacity
        if line_width is not None:
            polygon_kwargs["line_width"] = line_width
        if line_cap is not None:
            polygon_kwargs["line_cap"] = line_cap
        if line_join is not None:
            polygon_kwargs["line_join"] = line_join
        if miter_limit is not None:
            polygon_kwargs["miter_limit"] = miter_limit
        if dash_pattern is not None:
            polygon_kwargs["dash_pattern"] = dash_pattern
        if dash_phase is not None:
            polygon_kwargs["dash_phase"] = dash_phase
        if rotate is not None:
            polygon_kwargs["rotate"] = rotate
        if xshift is not None:
            polygon_kwargs["xshift"] = xshift
        if yshift is not None:
            polygon_kwargs["yshift"] = yshift
        if scale is not None:
            polygon_kwargs["scale"] = scale
        if xscale is not None:
            polygon_kwargs["xscale"] = xscale
        if yscale is not None:
            polygon_kwargs["yscale"] = yscale

        polygon_kwargs.update(kwargs)

        polygon = Polygon(
            center=center,
            radius=radius,
            sides=sides,
            rotation=rotation,
            comment=comment,
            layer=layer,
            options=[],
            **polygon_kwargs,
        )

        self.layers.add_item(item=polygon, layer=layer, verbose=verbose)
        return polygon

    def triangle(
        self,
        center: PositionInput,
        radius: float | str,
        rotation: float = 0,
        layer: int = 0,
        comment: str | None = None,
        verbose: bool = False,
        # Color
        color: ColorInput | None = None,
        fill: ColorInput | None = None,
        draw: ColorInput | None = None,
        text: ColorInput | None = None,
        # Opacity
        opacity: float | None = None,
        draw_opacity: float | None = None,
        fill_opacity: float | None = None,
        text_opacity: float | None = None,
        # Line width
        line_width: str | None = None,
        # Catch-all for unlisted TikZ options
        **kwargs: Any,
    ) -> Triangle:
        """Add an equilateral triangle to the figure.

        Args:
            center: Center coordinate as an ``(x, y)`` / ``(x, y, z)`` tuple or
                :class:`TikzCoordinate`.
            radius: Distance from center to vertices.
            rotation: Rotation angle in degrees. Defaults to ``0``.
            layer: Target layer index. Defaults to ``0``.
            comment: Optional comment prepended in the TikZ output.
            verbose: If ``True``, print a debug message.
            color: Line color (e.g. ``"red"``, ``"blue!50"``).
            fill: Fill color for the triangle.
            draw: Stroke color when different from *color*.
            text: Text color.
            opacity: Overall opacity (0–1).
            draw_opacity: Stroke opacity (0–1).
            fill_opacity: Fill opacity (0–1).
            text_opacity: Text opacity (0–1).
            line_width: Line width (e.g. ``"1pt"``).
            **kwargs: Catch-all for unlisted TikZ options.

        Returns:
            The :class:`Triangle` object that was added.
        """
        triangle_kwargs: dict[str, Any] = {}
        if color is not None:
            triangle_kwargs["color"] = color
        if fill is not None:
            triangle_kwargs["fill"] = fill
        if draw is not None:
            triangle_kwargs["draw"] = draw
        if text is not None:
            triangle_kwargs["text"] = text
        if opacity is not None:
            triangle_kwargs["opacity"] = opacity
        if draw_opacity is not None:
            triangle_kwargs["draw_opacity"] = draw_opacity
        if fill_opacity is not None:
            triangle_kwargs["fill_opacity"] = fill_opacity
        if text_opacity is not None:
            triangle_kwargs["text_opacity"] = text_opacity
        if line_width is not None:
            triangle_kwargs["line_width"] = line_width

        triangle_kwargs.update(kwargs)

        triangle = Triangle(
            center=center,
            radius=radius,
            rotation=rotation,
            comment=comment,
            layer=layer,
            options=[],
            **triangle_kwargs,
        )

        self.layers.add_item(item=triangle, layer=layer, verbose=verbose)
        return triangle

    def square(
        self,
        center: PositionInput,
        radius: float | str,
        rotation: float = 45,
        layer: int = 0,
        comment: str | None = None,
        verbose: bool = False,
        # Color
        color: ColorInput | None = None,
        fill: ColorInput | None = None,
        draw: ColorInput | None = None,
        text: ColorInput | None = None,
        # Opacity
        opacity: float | None = None,
        draw_opacity: float | None = None,
        fill_opacity: float | None = None,
        text_opacity: float | None = None,
        # Line width
        line_width: str | None = None,
        # Catch-all for unlisted TikZ options
        **kwargs: Any,
    ) -> Square:
        """Add a square to the figure.

        Args:
            center: Center coordinate as an ``(x, y)`` / ``(x, y, z)`` tuple or
                :class:`TikzCoordinate`.
            radius: Distance from center to vertices (corner-to-center distance).
            rotation: Rotation angle in degrees. Defaults to ``45`` (axis-aligned).
            layer: Target layer index. Defaults to ``0``.
            comment: Optional comment prepended in the TikZ output.
            verbose: If ``True``, print a debug message.
            color: Line color (e.g. ``"red"``, ``"blue!50"``).
            fill: Fill color for the square.
            draw: Stroke color when different from *color*.
            text: Text color.
            opacity: Overall opacity (0–1).
            draw_opacity: Stroke opacity (0–1).
            fill_opacity: Fill opacity (0–1).
            text_opacity: Text opacity (0–1).
            line_width: Line width (e.g. ``"1pt"``).
            **kwargs: Catch-all for unlisted TikZ options.

        Returns:
            The :class:`Square` object that was added.
        """
        square_kwargs: dict[str, Any] = {}
        if color is not None:
            square_kwargs["color"] = color
        if fill is not None:
            square_kwargs["fill"] = fill
        if draw is not None:
            square_kwargs["draw"] = draw
        if text is not None:
            square_kwargs["text"] = text
        if opacity is not None:
            square_kwargs["opacity"] = opacity
        if draw_opacity is not None:
            square_kwargs["draw_opacity"] = draw_opacity
        if fill_opacity is not None:
            square_kwargs["fill_opacity"] = fill_opacity
        if text_opacity is not None:
            square_kwargs["text_opacity"] = text_opacity
        if line_width is not None:
            square_kwargs["line_width"] = line_width

        square_kwargs.update(kwargs)

        square = Square(
            center=center,
            radius=radius,
            rotation=rotation,
            comment=comment,
            layer=layer,
            options=[],
            **square_kwargs,
        )

        self.layers.add_item(item=square, layer=layer, verbose=verbose)
        return square

    def plot3d(
        self,
        x: list[float],
        y: list[float],
        z: list[float],
        layer: int = 0,
        comment: str | None = None,
        center: bool = False,
        verbose: bool = False,
        **kwargs: Any,
    ) -> Plot3D:
        """Add a 3-D data plot with ``\\addplot3``.

        Args:
            x: List of x-coordinate values.
            y: List of y-coordinate values.
            z: List of z-coordinate values.
            layer: Target layer index. Defaults to ``0``.
            comment: Optional comment prepended in the TikZ output.
            center: If ``True``, connect through ``.center`` anchors.
            verbose: If ``True``, print a debug message.
            **kwargs: Additional pgfplots options (e.g. ``mark="*"``).

        Returns:
            The :class:`Plot3D` object that was added.
        """
        plot = Plot3D(
            x=x,
            y=y,
            z=z,
            comment=comment,
            center=center,
            **kwargs,
        )

        self.layers.add_item(item=plot, layer=layer, verbose=verbose)
        return plot

    def axis2d(
        self,
        xlabel: str = "",
        ylabel: str = "",
        xlim: tuple[float, float] | None = None,
        ylim: tuple[float, float] | None = None,
        grid: bool | str = True,
        width: str | int | float | None = None,
        height: str | int | float | None = None,
        layer: int = 0,
        comment: str | None = None,
        **kwargs: Any,
    ) -> Axis2D:
        """Create and register a 2D axis.

        Args:
            xlabel: Label for x-axis. Defaults to "".
            ylabel: Label for y-axis. Defaults to "".
            xlim: (min, max) tuple for x-axis limits, or None for auto.
            ylim: (min, max) tuple for y-axis limits, or None for auto.
            grid: Enable grid lines. Pass ``True`` / ``False`` for the usual
                pgfplots values or a string such as ``"major"``.
            width: Width of the axis as a string (e.g., "8cm"), number in cm,
                or None for auto. Defaults to None.
            height: Height of the axis as a string (e.g., "6cm"), number in cm,
                or None for auto. Defaults to None.
            layer: Layer index (for metadata; axes render after all layers).
            comment: Optional comment prepended in TikZ output.
            **kwargs: Additional pgfplots axis options.

        Returns:
            The newly created Axis2D object.
        """
        axis = Axis2D(
            xlabel=xlabel,
            ylabel=ylabel,
            xlim=xlim,
            ylim=ylim,
            grid=grid,
            width=width,
            height=height,
            label="",
            comment=comment,
            layer=layer,
            library_loader=self.usetikzlibrary,
            spy_scope_enabler=self._ensure_figure_spy_scope,
            **kwargs,
        )
        self.axes.append(axis)
        return axis

    def add_loop(
        self,
        variable: str,
        values: list[Any] | tuple[Any, ...] | range,
        layer: int = 0,
        comment: str | None = None,
        verbose: bool = False,
    ) -> Loop:
        """Add a ``\\foreach`` loop to the figure.

        Args:
            variable: Loop variable name (without the leading backslash),
                e.g. ``"i"`` produces ``\\foreach \\i in {...}``.
            values: Sequence of values to iterate over.
            layer: Target layer index. Defaults to ``0``.
            comment: Optional comment prepended in the TikZ output.
            verbose: If ``True``, print a debug message.

        Returns:
            The :class:`Loop` context manager. Add nodes and paths inside a
            ``with`` block or by calling methods on the returned object.
        """
        loop_obj = Loop(
            variable=variable,
            values=values,
            layer=layer,
            comment=comment,
        )

        self.layers.add_item(item=loop_obj, layer=layer, verbose=verbose)
        return loop_obj

    def add_scope(
        self,
        layer: int = 0,
        comment: str | None = None,
        options: OptionInput | None = None,
        verbose: bool = False,
        **kwargs: Any,
    ) -> Scope:
        """Add a TikZ ``scope`` block with local options to the figure."""
        scope_obj = Scope(
            layer=layer,
            comment=comment,
            options=options,
            node_resolver=self.layers.get_node,
            library_loader=self.usetikzlibrary,
            **kwargs,
        )
        self.layers.add_item(item=scope_obj, layer=layer, verbose=verbose)
        return scope_obj

    # ---------------------------------------------------------------- #
    # Properties

    @property
    def document_setup(self) -> str | None:
        """Raw LaTeX inserted in the preamble before ``\\begin{document}``."""
        return self._document_setup

    @property
    def extra_packages(self) -> list[str] | None:
        """Extra LaTeX packages included in the standalone preamble."""
        return list(self._extra_packages) if self._extra_packages is not None else None

    @property
    def named_styles(self) -> list[dict[str, Any]]:
        """Named TikZ styles defined at figure scope."""
        return [
            {
                "name": style_def["name"],
                "options": list(style_def["options"]),
                "kwargs": dict(style_def["kwargs"]),
            }
            for style_def in self._named_styles
        ]

    @property
    def tikz_libraries(self) -> list[str]:
        """TikZ libraries loaded in standalone output via ``\\usetikzlibrary``."""
        return list(self._tikz_libraries)

    @property
    def ndim(self) -> int:
        """Number of spatial dimensions (``2`` or ``3``)."""
        return self._ndim

    @property
    def layers(self) -> LayerCollection:
        """The :class:`LayerCollection` holding all drawing layers."""
        return self._layers

    @property
    def colors(self) -> list[tuple[str, Color]]:
        """List of ``(name, Color)`` pairs defined with :meth:`colorlet`."""
        return self._colors

    @property
    def variables(self) -> list:
        """List of :class:`Variable` objects defined in this figure."""
        return self._variables

    @property
    def declared_functions(self) -> list[DeclaredFunction]:
        """List of declared PGF functions available in this figure."""
        return self._declared_functions

    @property
    def axes(self) -> list[Axis2D]:
        """List of :class:`Axis2D` objects created in this figure."""
        return self._axes

    @property
    def subfigure_axes(self) -> list[tuple[Axis2D, float]]:
        """List of subfigure axes with widths."""
        return self._subfigure_axes

    # Short public aliases for the add_* helpers.
    node = add_node
    coordinate = add_coordinate
    variable = add_variable
    function = declare_function
    raw = add_raw
    plot = add_plot
    spy = add_spy
    spy_scope = add_spy_scope
    subfigure = FigureLayoutMixin.add_subfigure
    loop = add_loop
    scope = add_scope

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TikzFigure):
            return NotImplemented
        return self.to_dict() == other.to_dict()

    # ------------------------------------------------------------- #
    def __repr__(self) -> str:
        """Return the generated TikZ source as the object representation."""
        return self.generate_tikz()

    def __str__(self) -> str:
        """Return the generated TikZ source as a string."""
        return self.generate_tikz()

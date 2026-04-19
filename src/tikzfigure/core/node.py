from typing import TYPE_CHECKING, Any

from tikzfigure.colors import ColorInput
from tikzfigure.core.base import TikzObject
from tikzfigure.core.coordinate import (
    Coordinate,
    CoordinateTuple2D,
    CoordinateTuple3D,
    CoordinateValue,
    TikzCoordinate,
    TikzVector,
    VectorInput,
)
from tikzfigure.core.types import _Align, _Anchor, _Option, _Pattern, _Shading, _Shape
from tikzfigure.options import OptionInput

if TYPE_CHECKING:
    from tikzfigure.core.path_builder import NodePathBuilder


class Node(TikzObject):
    """A TikZ node with an optional position, content, and styling options.

    Accepts the same TikZ options as :meth:`TikzFigure.add_node`. Refer to
    that method for the full parameter reference.

    Attributes:
        x: X-coordinate of the node, or ``None`` for relatively positioned
            nodes.
        y: Y-coordinate of the node, or ``None`` for relatively positioned
            nodes.
        z: Z-coordinate for 3-D figures, or ``None`` for 2-D figures.
        ndim: Number of spatial dimensions (``2`` or ``3``).
        content: Text or LaTeX content displayed inside the node.
    """

    def __init__(
        self,
        x: CoordinateValue
        | CoordinateTuple2D
        | CoordinateTuple3D
        | TikzCoordinate
        | None = None,
        y: CoordinateValue | None = None,
        z: CoordinateValue | None = None,
        label: str = "",
        content: str = "",
        comment: str | None = None,
        layer: int = 0,
        options: OptionInput | None = None,
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
        minimum_width: str | None = None,
        minimum_height: str | None = None,
        minimum_size: str | None = None,
        # Separation
        inner_sep: str | None = None,
        inner_xsep: str | None = None,
        inner_ysep: str | None = None,
        outer_sep: str | None = None,
        outer_xsep: str | None = None,
        outer_ysep: str | None = None,
        # Line
        line_width: str | None = None,
        # Text
        font: str | None = None,
        text_width: str | None = None,
        text_height: str | None = None,
        text_depth: str | None = None,
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
        node_distance: str | None = None,
        # Transformations
        rotate: float | None = None,
        xshift: str | None = None,
        yshift: str | None = None,
        scale: float | None = None,
        xscale: float | None = None,
        yscale: float | None = None,
        xslant: float | None = None,
        yslant: float | None = None,
        # Border
        rounded_corners: str | None = None,
        double: ColorInput | None = None,
        double_distance: str | None = None,
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
    ) -> None:
        """Initialize a Node.

        Accepts the same TikZ options as :meth:`TikzFigure.add_node`.
        Refer to that method for the full parameter reference.

        Args:
            x: X-coordinate, a ``(x, y)`` / ``(x, y, z)`` tuple, or a
                :class:`TikzCoordinate`. Use ``None`` for relatively
                positioned nodes.
            y: Y-coordinate. Use ``None`` when ``x`` already provides the
                full position.
            z: Z-coordinate for 3-D figures. Use ``None`` when ``x`` already
                provides the full position.
            label: Internal TikZ name for this node. Defaults to ``""``.
            content: Text or LaTeX content displayed inside the node.
            comment: Optional comment prepended in the TikZ output.
            layer: Layer index. Defaults to ``0``.
            options: Flag-style TikZ options (e.g. ``["draw", "thick"]``).
            shape: Node shape (e.g. ``"circle"``, ``"rectangle"``).
            color: Text color.
            fill: Fill color.
            draw: Border/stroke color.
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
            anchor: Anchor point (e.g. ``"center"``, ``"north"``).
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
            node_distance: Distance for relative positioning (e.g. ``"1cm"``).
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
            shading: Shading type (``"axis"``, ``"radial"``, ``"ball"``).
            shading_angle: Angle for axis shading.
            left_color: Left color for axis shading.
            right_color: Right color for axis shading.
            top_color: Top color for axis shading.
            bottom_color: Bottom color for axis shading.
            inner_color: Inner color for radial shading.
            outer_color: Outer color for radial shading.
            ball_color: Ball color for ball shading.
            regular_polygon_sides: Number of sides for ``shape="regular polygon"``.
            star_points: Number of points for ``shape="star"``.
            star_point_ratio: Inner-to-outer radius ratio for stars.
            star_point_height: Height of star points.
            shadow_xshift: Horizontal shadow shift.
            shadow_yshift: Vertical shadow shift.
            shadow_color: Shadow color.
            shadow_opacity: Shadow opacity (0–1).
            shadow_scale: Shadow scale factor.
            pin: Pin label specification (e.g. ``"above:text"``).
            **kwargs: Additional TikZ options not listed above. Underscores
                in keys become spaces in the output.
        """
        # Capture all parameters for TikZ option generation, excluding internal and base-class keys
        _params = locals().copy()
        _non_tikz = {
            "self",
            "x",
            "y",
            "z",
            "label",
            "content",
            "comment",
            "layer",
            "options",
            "kwargs",
            "__class__",
        }

        tikz_kwargs = dict(kwargs)
        tikz_kwargs.update(
            {k: v for k, v in _params.items() if k not in _non_tikz and v is not None}
        )

        if options is None:
            options = []

        if x is None and y is None and z is None:
            self._coordinate = None
        else:
            if x is None:
                raise ValueError(
                    "Provide both x and y coordinates, or pass a coordinate tuple/TikzCoordinate."
                )
            self._coordinate = TikzCoordinate(x=x, y=y, z=z, layer=layer)

        self._content = content
        super().__init__(
            label=label,
            comment=comment,
            layer=layer,
            options=options,
            **tikz_kwargs,
        )

    @property
    def x(self) -> CoordinateValue | None:
        """X-coordinate, or ``None`` for relatively positioned nodes."""
        if self.coordinate is None:
            return None
        return self.coordinate.x

    @property
    def y(self) -> CoordinateValue | None:
        """Y-coordinate, or ``None`` for relatively positioned nodes."""
        if self.coordinate is None:
            return None
        return self.coordinate.y

    @property
    def z(self) -> CoordinateValue | None:
        """Z-coordinate for 3-D figures, or ``None`` for 2-D figures."""
        if self.coordinate is None:
            return None
        return self.coordinate.z

    @property
    def coordinate(self) -> TikzCoordinate | None:
        """TikzCoordinate for this node, or ``None`` for relatively positioned nodes."""
        return self._coordinate

    @property
    def position(self) -> TikzCoordinate | None:
        """Alias for :attr:`coordinate` for geometric operations."""
        return self.coordinate

    @property
    def ndim(self) -> int:
        """Number of spatial dimensions (``2`` or ``3``)."""
        if self.coordinate is None:
            return 2
        return self.coordinate.ndim

    @property
    def center(self) -> str:
        """Anchor point for the center of the node."""
        return f"{self.label}.center"

    @property
    def content(self) -> str:
        """Text or LaTeX content displayed inside this node."""
        return self._content

    def _require_coordinate(self) -> TikzCoordinate:
        """Return the absolute position or raise for relatively positioned nodes."""
        if self.coordinate is None:
            raise ValueError(
                "This node does not have explicit coordinates, so geometric operations are unavailable."
            )
        return self.coordinate

    @staticmethod
    def _coerce_coordinate(other: "Node | TikzCoordinate") -> TikzCoordinate:
        """Normalize a node-or-coordinate operand to a coordinate."""
        if isinstance(other, Node):
            return other._require_coordinate()
        return other

    def to_vector(self) -> TikzVector:
        """Interpret this node position as a vector from the origin."""
        return self._require_coordinate().to_vector()

    def vector_to(self, other: "Node | TikzCoordinate") -> TikzVector:
        """Return the vector from this node to another node or point."""
        return self._require_coordinate().vector_to(self._coerce_coordinate(other))

    def distance_to(self, other: "Node | TikzCoordinate") -> float:
        """Return the Euclidean distance to another node or point."""
        return self._require_coordinate().distance_to(self._coerce_coordinate(other))

    def translate(self, vector: VectorInput) -> TikzCoordinate:
        """Return the translated point for this node."""
        return self._require_coordinate().translate(TikzVector(vector))

    def to(
        self,
        target: "Node | Coordinate",
        options: OptionInput | None = None,
        **kwargs: Any,
    ) -> "NodePathBuilder":
        """Create a path builder for a segment from this node to ``target``.

        The returned builder always starts with ``self`` and records the segment
        options for the edge from ``self`` to ``target``. Chain additional
        ``.to(...)`` or ``.arc(...)`` calls on the builder to add more path
        segments. Only :class:`Node` and :class:`Coordinate` targets are
        accepted by ``.to(...)``.
        """
        from tikzfigure.core.path_builder import NodePathBuilder

        return NodePathBuilder(self).to(target, options=options, **kwargs)

    def to_tikz(self, output_unit: str | None = None) -> str:
        """Generate the TikZ ``\\node`` command for this node.

        Returns:
            A TikZ ``\\node`` command string ending with a newline, optionally
            preceded by a comment line.
        """
        options = self.tikz_options(output_unit)
        if options:
            options = f"[{options}]"
        if self.coordinate is None:
            node_string = f"\\node{options} ({self.label}) {{{self.content}}};\n"
        else:
            node_string = (
                f"\\node{options} ({self.label}) at {self.coordinate.to_tikz(output_unit)} "
                f"{{{self.content}}};\n"
            )

        node_string = self.add_comment(node_string)
        return node_string

    def to_dict(self) -> dict[str, Any]:
        """Serialize this node to a plain dictionary.

        Returns:
            A dictionary with ``type``, ``x``, ``y``, ``z``, ``content``,
            and all base-class keys.
        """
        d = super().to_dict()
        d.update(
            {
                "type": "Node",
                "x": self.x,
                "y": self.y,
                "z": self.z,
                "content": self._content,
            }
        )
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Node":
        """Reconstruct a Node from a dictionary.

        Args:
            d: Dictionary as produced by :meth:`to_dict`.

        Returns:
            A new :class:`Node` instance.
        """
        kwargs = d.get("kwargs", {})
        return cls(
            x=d.get("x"),
            y=d.get("y"),
            z=d.get("z"),
            label=d.get("label", ""),
            content=d.get("content", ""),
            comment=d.get("comment"),
            layer=d.get("layer", 0),
            options=d.get("options"),
            **kwargs,
        )

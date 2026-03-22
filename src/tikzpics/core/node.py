from tikzpics.core.base import TikzObject


class Node(TikzObject):
    def __init__(
        self,
        x: float | int | None = None,
        y: float | int | None = None,
        z: float | int | None = None,
        label: str = "",
        content: str = "",
        comment: str | None = None,
        layer: int = 0,
        options: list | None = None,
        # Shape
        shape: str | None = None,
        # Color
        color: str | None = None,
        fill: str | None = None,
        draw: str | None = None,
        text: str | None = None,
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
        align: str | None = None,
        # Anchor
        anchor: str | None = None,
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
        double: str | None = None,
        double_distance: str | None = None,
        dash_pattern: str | None = None,
        dash_phase: str | None = None,
        # Pattern / shading
        pattern: str | None = None,
        pattern_color: str | None = None,
        shading: str | None = None,
        shading_angle: float | None = None,
        left_color: str | None = None,
        right_color: str | None = None,
        top_color: str | None = None,
        bottom_color: str | None = None,
        inner_color: str | None = None,
        outer_color: str | None = None,
        ball_color: str | None = None,
        # Shape-specific
        regular_polygon_sides: int | None = None,
        star_points: int | None = None,
        star_point_ratio: float | None = None,
        star_point_height: str | None = None,
        # Shadow
        shadow_xshift: str | None = None,
        shadow_yshift: str | None = None,
        shadow_color: str | None = None,
        shadow_opacity: float | None = None,
        shadow_scale: float | None = None,
        # Pin / label on node
        pin: str | None = None,
        # Catch-all for unlisted TikZ options
        **kwargs,
    ):
        """Represents a TikZ node.

        Accepts the same TikZ options as :meth:`TikzFigure.add_node`.
        """
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

        self._x = x
        self._y = y
        self._z = z
        if z is None:
            self._ndim = 2
        else:
            self._ndim = 3

        self._content = content
        super().__init__(
            label=label,
            comment=comment,
            layer=layer,
            options=options,
            **tikz_kwargs,
        )

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def z(self):
        return self._z

    @property
    def ndim(self):
        return self._ndim

    @property
    def content(self):
        return self._content

    def to_tikz(self):
        """
        Generate the TikZ code for this node.

        Returns:
        - tikz_str (str): TikZ code string for the node.
        """

        # options = ", ".join(
        #     f"{k.replace('_', ' ')}={v}" for k, v in self.options.items()
        # )
        options = self.tikz_options
        if options:
            options = f"[{options}]"
        if self.x is None and self.y is None:
            node_string = f"\\node{options} ({self.label}) {{{self.content}}};\n"
        elif self.ndim == 2:
            node_string = f"\\node{options} ({self.label}) at ({self.x}, {self.y}) {{{self.content}}};\n"
        else:
            node_string = f"\\node{options} ({self.label}) at (axis cs:{self.x}, {self.y}, {self.z}) {{{self.content}}};\n"

        node_string = self.add_comment(node_string)
        return node_string

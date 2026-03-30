import re


class Linestyle:
    """Represents a TikZ line style and its Matplotlib equivalent.

    Parses a TikZ-style line specification and converts it to the format
    expected by Matplotlib for rendering previews.

    Attributes:
        style_spec: The original TikZ line-style string.
        matplotlib_style: The equivalent Matplotlib linestyle, either a
            named string (e.g. ``"dashed"``) or a dash-offset tuple
            ``(offset, (on, off))``.
    """

    def _parse_style(self, style_spec: str) -> str | tuple[int, tuple[float, float]]:
        """Parse a TikZ style string into a Matplotlib linestyle.

        Args:
            style_spec: A TikZ line-style string.

        Returns:
            A Matplotlib linestyle string (e.g. ``"dashed"``) for predefined
            styles, or a dash-offset tuple ``(0, (on, off))`` for custom
            ``dash pattern=on Xpt off Ypt`` patterns. Falls back to
            ``"solid"`` for unrecognised input.
        """
        linestyle_mapping = {
            "solid": "solid",
            "dashed": "dashed",
            "dotted": "dotted",
            "dashdot": "dashdot",
        }

        if style_spec in linestyle_mapping:
            return linestyle_mapping[style_spec]
        else:
            match = re.match(r"dash pattern=on ([\d.]+)pt off ([\d.]+)pt", style_spec)
            if match:
                on_length = float(match.group(1))
                off_length = float(match.group(2))
                return (0, (on_length, off_length))
            else:
                print(f"Unknown line style: '{style_spec}', defaulting to 'solid'")
                return "solid"

    def __init__(self, style_spec: str) -> None:
        """Initialize a Linestyle.

        Args:
            style_spec: A TikZ line-style string such as ``"solid"``,
                ``"dashed"``, ``"dotted"``, ``"dashdot"``, or a custom
                dash pattern like ``"dash pattern=on 5pt off 2pt"``.
        """
        self.style_spec: str = style_spec
        self.matplotlib_style: str | tuple[int, tuple[float, float]] = (
            self._parse_style(style_spec)
        )

    def to_matplotlib(self) -> str | tuple[int, tuple[float, float]]:
        """Return the line style in Matplotlib format.

        Returns:
            A Matplotlib linestyle string (e.g. ``"dashed"``) or a
            dash-offset tuple ``(offset, (on, off))``.
        """
        return self.matplotlib_style

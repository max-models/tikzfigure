from typing import Any

from tikzfigure.core.base import TikzObject
from tikzfigure.core.coordinate import (
    CoordinateTuple2D,
    CoordinateTuple3D,
    CoordinateValue,
    TikzCoordinate,
)
from tikzfigure.core.serialization import deserialize_tikz_value, serialize_tikz_value
from tikzfigure.core.tikz_library import TikzLibrary
from tikzfigure.options import OptionInput, normalize_options

MatrixCell = str | dict[str, Any] | None


class MatrixLibrary(TikzLibrary):
    """The ``matrix`` library, used to lay out a grid of nodes.

    Owns the matrix library's node-naming convention, so
    :class:`Matrix` and any other caller can derive a cell's TikZ node
    name without duplicating the ``"<label>-<row>-<col>"`` format.
    """

    name = "matrix"

    @staticmethod
    def cell_name(label: str, row: int, col: int) -> str:
        """Return the TikZ node name the matrix library assigns a cell."""
        return f"{label}-{row}-{col}"


class Matrix(TikzObject):
    """A TikZ matrix of nodes, built with the ``matrix`` library.

    Provides a first-class way to lay out a grid of nodes (``\\matrix``)
    without hand-writing raw TikZ. Each cell may be a plain string (node
    content) or a dict with a ``content`` key plus per-cell styling
    options/kwargs, rendered using the ``|[options]| content`` shortcut.

    Cells are addressable via :meth:`cell`, which returns the TikZ node
    name TikZ auto-generates for each entry (``"<label>-<row>-<col>"``,
    1-indexed). Use that name with :meth:`TikzFigure.add_coordinate`'s
    ``at=`` parameter to reference a cell in paths, e.g.::

        m = fig.add_matrix([["A", "B"], ["C", "D"]], label="m")
        fig.add_coordinate("c11", at=m.cell(1, 1))
        fig.add_coordinate("c22", at=m.cell(2, 2))
        fig.draw(["c11", "c22"])

    Attributes:
        rows: The grid of cells, as a list of rows of :data:`MatrixCell`.
        row_sep: Row separation TikZ value, or ``None``.
        column_sep: Column separation TikZ value, or ``None``.
        cell_style: Shared style applied to every cell node
            (rendered as ``nodes={<cell_style>}``), or ``None``.
    """

    def __init__(
        self,
        rows: list[list[MatrixCell]],
        x: (
            CoordinateValue
            | CoordinateTuple2D
            | CoordinateTuple3D
            | TikzCoordinate
            | None
        ) = None,
        y: CoordinateValue | None = None,
        z: CoordinateValue | None = None,
        label: str = "",
        comment: str | None = None,
        layer: int = 0,
        options: OptionInput | None = None,
        row_sep: str | None = None,
        column_sep: str | None = None,
        cell_style: str | list[str] | None = None,
        anchor: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize a Matrix.

        Args:
            rows: Grid of cells, given row by row. Each cell is either a
                plain string (node content), a dict of
                ``{"content": str, "options": ..., **node_kwargs}`` for
                per-cell styling, or ``None`` for an empty cell.
            x: X-coordinate, a ``(x, y)`` / ``(x, y, z)`` tuple, or a
                :class:`TikzCoordinate` giving the matrix's anchor
                position. Use ``None`` to let TikZ place it at the origin.
            y: Y-coordinate. Use ``None`` when ``x`` already provides the
                full position.
            z: Z-coordinate for 3-D figures.
            label: Internal TikZ name for this matrix. Required to address
                individual cells with :meth:`cell`.
            comment: Optional comment prepended in the TikZ output.
            layer: Layer index. Defaults to ``0``.
            options: Flag-style TikZ options for the matrix node itself.
            row_sep: Row separation (e.g. ``"5pt"`` or ``"1em plus 1pt"``).
            column_sep: Column separation (e.g. ``"1cm"``).
            cell_style: Shared TikZ style(s) applied to every cell node,
                rendered as ``nodes={<cell_style>}`` (e.g.
                ``"draw, minimum size=8mm, anchor=center"``).
            anchor: Anchor point for the whole matrix node.
            **kwargs: Additional matrix-level TikZ options. Underscores in
                keys become spaces (e.g. ``nodes_in_empty_cells=True``).
        """
        self._rows: list[list[MatrixCell]] = [list(row) for row in rows]

        if x is None and y is None and z is None:
            self._coordinate = None
        else:
            if x is None:
                raise ValueError(
                    "Provide both x and y coordinates, or pass a coordinate tuple/TikzCoordinate."
                )
            self._coordinate = TikzCoordinate(x=x, y=y, z=z, layer=layer)

        self._row_sep = row_sep
        self._column_sep = column_sep
        self._cell_style = cell_style

        tikz_kwargs = dict(kwargs)
        if row_sep is not None:
            tikz_kwargs["row_sep"] = row_sep
        if column_sep is not None:
            tikz_kwargs["column_sep"] = column_sep
        if anchor is not None:
            tikz_kwargs["anchor"] = anchor

        matrix_options = list(normalize_options(options))
        if cell_style is not None:
            style_str = (
                ", ".join(str(s) for s in cell_style)
                if isinstance(cell_style, (list, tuple))
                else str(cell_style)
            )
            matrix_options.append(f"nodes={{{style_str}}}")

        super().__init__(
            label=label,
            comment=comment,
            layer=layer,
            options=matrix_options,
            **tikz_kwargs,
        )

    @property
    def x(self) -> CoordinateValue | None:
        """X-coordinate of the matrix anchor, or ``None``."""
        if self.coordinate is None:
            return None
        return self.coordinate.x

    @property
    def y(self) -> CoordinateValue | None:
        """Y-coordinate of the matrix anchor, or ``None``."""
        if self.coordinate is None:
            return None
        return self.coordinate.y

    @property
    def z(self) -> CoordinateValue | None:
        """Z-coordinate of the matrix anchor, or ``None``."""
        if self.coordinate is None:
            return None
        return self.coordinate.z

    @property
    def coordinate(self) -> TikzCoordinate | None:
        """TikzCoordinate for this matrix's anchor, or ``None``."""
        return self._coordinate

    @property
    def rows(self) -> list[list[MatrixCell]]:
        """The grid of cells, as a list of rows."""
        return self._rows

    @property
    def num_rows(self) -> int:
        """Number of rows in the matrix."""
        return len(self._rows)

    @property
    def num_cols(self) -> int:
        """Number of columns in the matrix (width of the widest row)."""
        return max((len(row) for row in self._rows), default=0)

    @property
    def row_sep(self) -> str | None:
        """Row separation TikZ value, or ``None``."""
        return self._row_sep

    @property
    def column_sep(self) -> str | None:
        """Column separation TikZ value, or ``None``."""
        return self._column_sep

    @property
    def cell_style(self) -> str | list[str] | None:
        """Shared style applied to every cell node, or ``None``."""
        return self._cell_style

    def cell(self, row: int, col: int) -> str:
        """Return the TikZ node name for a cell (1-indexed).

        The matrix library auto-names every cell node
        ``"<label>-<row>-<col>"``. Use the returned string with
        :meth:`TikzFigure.add_coordinate`'s ``at=`` parameter to reference
        the cell in paths.

        Args:
            row: 1-indexed row number.
            col: 1-indexed column number.

        Returns:
            The TikZ node name for the given cell.

        Raises:
            ValueError: If this matrix has no label, or the cell is out of
                range.
        """
        if not self.label:
            raise ValueError("Matrix must have a label to address cells.")
        if row < 1 or row > self.num_rows or col < 1 or col > self.num_cols:
            raise ValueError(
                f"Cell ({row}, {col}) is out of range for a "
                f"{self.num_rows}x{self.num_cols} matrix."
            )
        return MatrixLibrary.cell_name(self.label, row, col)

    @staticmethod
    def _cell_to_tikz(cell: MatrixCell) -> str:
        """Render a single cell to its TikZ representation."""
        if cell is None:
            return ""
        if isinstance(cell, str):
            return cell
        if isinstance(cell, dict):
            content = cell.get("content", "")
            cell_options = normalize_options(cell.get("options"))
            cell_kwargs = {
                k: v for k, v in cell.items() if k not in ("content", "options")
            }
            parts = [str(option) for option in cell_options]
            parts.extend(f"{k.replace('_', ' ')}={v}" for k, v in cell_kwargs.items())
            opts_str = ", ".join(parts)
            if opts_str:
                return f"|[{opts_str}]| {content}"
            return str(content)
        raise TypeError(
            f"Matrix cell must be a str, dict, or None, got {type(cell)!r}."
        )

    def to_tikz(self, output_unit: str | None = None) -> str:
        """Generate the TikZ ``\\matrix`` command for this matrix.

        Returns:
            A TikZ ``\\matrix`` command string ending with a newline,
            optionally preceded by a comment line.
        """
        options = self.tikz_options(output_unit)
        options_str = f"[{options}]" if options else ""
        label_str = f" ({self.label})" if self.label else ""
        at_str = (
            f" at {self.coordinate.to_tikz(output_unit)}"
            if self.coordinate is not None
            else ""
        )

        row_strings = [
            " & ".join(self._cell_to_tikz(cell) for cell in row) + r" \\"
            for row in self._rows
        ]
        body = "\n  ".join(row_strings)

        matrix_string = f"\\matrix{options_str}{label_str}{at_str} {{\n  {body}\n}};\n"
        matrix_string = self.add_comment(matrix_string)
        return matrix_string

    def to_dict(self) -> dict[str, Any]:
        """Serialize this matrix to a plain dictionary.

        Returns:
            A dictionary with ``type``, ``rows``, ``x``, ``y``, ``z``,
            ``row_sep``, ``column_sep``, ``cell_style``, and all
            base-class keys.
        """
        d = super().to_dict()
        d.update(
            {
                "type": "Matrix",
                "rows": self._rows,
                "x": self.x,
                "y": self.y,
                "z": self.z,
                "row_sep": self._row_sep,
                "column_sep": self._column_sep,
                "cell_style": self._cell_style,
            }
        )
        serialized = serialize_tikz_value(d)
        if not isinstance(serialized, dict):
            raise TypeError("Serialized matrix data must remain a dict.")
        return serialized

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Matrix":
        """Reconstruct a Matrix from a dictionary.

        Args:
            d: Dictionary as produced by :meth:`to_dict`.

        Returns:
            A new :class:`Matrix` instance.
        """
        restored = deserialize_tikz_value(d)
        if not isinstance(restored, dict):
            raise TypeError("Serialized matrix data must deserialize to a dict.")
        kwargs = restored.get("kwargs", {})
        if not isinstance(kwargs, dict):
            raise TypeError("Serialized matrix kwargs must deserialize to a dict.")
        # row_sep/column_sep/anchor are folded into kwargs by __init__; avoid
        # passing them twice.
        kwargs = dict(kwargs)
        kwargs.pop("row_sep", None)
        kwargs.pop("column_sep", None)
        options = restored.get("options")
        if isinstance(options, list) and restored.get("cell_style") is not None:
            style_str = restored["cell_style"]
            style_str = (
                ", ".join(str(s) for s in style_str)
                if isinstance(style_str, (list, tuple))
                else str(style_str)
            )
            marker = f"nodes={{{style_str}}}"
            options = [o for o in options if o != marker]
        return cls(
            rows=restored.get("rows", []),
            x=restored.get("x"),
            y=restored.get("y"),
            z=restored.get("z"),
            label=restored.get("label", ""),
            comment=restored.get("comment"),
            layer=restored.get("layer", 0),
            options=options,
            row_sep=restored.get("row_sep"),
            column_sep=restored.get("column_sep"),
            cell_style=restored.get("cell_style"),
            **kwargs,
        )

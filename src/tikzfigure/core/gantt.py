"""Structured support for charts from the LaTeX ``pgfgantt`` package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, TypeAlias

from tikzfigure.core.base import TikzObject
from tikzfigure.options import OptionInput, normalize_options

GanttRow: TypeAlias = Mapping[str, Any]


def _options(options: OptionInput | None, kwargs: Mapping[str, Any]) -> str:
    parts = [str(option) for option in normalize_options(options)]
    parts.extend(
        key.replace("_", " ") if value is True else f"{key.replace('_', ' ')}={value}"
        for key, value in kwargs.items()
    )
    return ", ".join(parts)


def _bracket_options(options: OptionInput | None, kwargs: Mapping[str, Any]) -> str:
    rendered = _options(options, kwargs)
    return f"[{rendered}]" if rendered else ""


class GanttChart(TikzObject):
    """A ``pgfgantt`` chart containing declarative rows.

    Rows are dictionaries with a ``type`` key. Supported types are
    ``title``, ``titlelist``, ``group``, ``bar``, ``milestone``, ``link``,
    and ``raw``. The convenience methods on :class:`TikzFigure` accept the
    same dictionaries, or rows can be assembled directly with this class.
    """

    def __init__(
        self,
        start: int | str,
        end: int | str,
        rows: Sequence[GanttRow] = (),
        *,
        label: str | None = None,
        comment: str | None = None,
        layer: int = 0,
        options: OptionInput | None = None,
        **kwargs: Any,
    ) -> None:
        if str(start).strip() == "" or str(end).strip() == "":
            raise ValueError("Gantt chart bounds must not be empty.")
        self._start = start
        self._end = end
        self._rows = [dict(row) for row in rows]
        super().__init__(
            label=label,
            comment=comment,
            layer=layer,
            options=options,
            **kwargs,
        )

    @property
    def start(self) -> int | str:
        return self._start

    @property
    def end(self) -> int | str:
        return self._end

    @property
    def rows(self) -> list[dict[str, Any]]:
        return self._rows

    def add_row(self, row_type: str, **row: Any) -> GanttChart:
        """Append a row and return this chart for fluent construction."""
        row = dict(row)
        row["type"] = row_type
        self._rows.append(row)
        return self

    @staticmethod
    def _row_to_tikz(row: Mapping[str, Any]) -> str:
        row = dict(row)
        row_type = row.pop("type", None)

        def take(*keys: str, default: Any = None) -> Any:
            for key in keys:
                if key in row:
                    return row.pop(key)
            return default

        if row_type == "raw":
            return str(take("code", "content", default=""))
        if row_type == "title":
            content = take("content", "label", default="")
            width = take("width", default=1)
            return f"\\gantttitle{_bracket_options(row.pop('options', None), row)}{{{content}}}{{{width}}}"
        if row_type == "titlelist":
            content = take("content", "labels", default="")
            width = take("width", default=1)
            return f"\\gantttitlelist{_bracket_options(row.pop('options', None), row)}{{{content}}}{{{width}}}"
        if row_type in {"group", "bar"}:
            command = "ganttgroup" if row_type == "group" else "ganttbar"
            content = take("content", "label", default="")
            start = take("start")
            end = take("end")
            if start is None or end is None:
                raise ValueError(f"{row_type!r} rows require start and end.")
            return f"\\{command}{_bracket_options(row.pop('options', None), row)}{{{content}}}{{{start}}}{{{end}}}"
        if row_type == "milestone":
            content = take("content", "label", default="")
            at = take("at", "start")
            if at is None:
                raise ValueError("'milestone' rows require at or start.")
            return f"\\ganttmilestone{_bracket_options(row.pop('options', None), row)}{{{content}}}{{{at}}}"
        if row_type == "link":
            source = take("source", "from")
            target = take("target", "to")
            if source is None or target is None:
                raise ValueError("'link' rows require source/from and target/to.")
            return f"\\ganttlink{_bracket_options(row.pop('options', None), row)}{{{source}}}{{{target}}}"
        raise ValueError(f"Unknown Gantt row type: {row_type!r}")

    def to_tikz(self, output_unit: str | None = None) -> str:
        chart_options = self.tikz_options(output_unit)
        opening = f"\\begin{{ganttchart}}{f'[{chart_options}]' if chart_options else ''}{{{self.start}}}{{{self.end}}}"
        rendered_rows = []
        for row in self.rows:
            rendered_row = self._row_to_tikz(row)
            if row.get("type") not in {"link", "raw"}:
                rendered_row += "\\\\"
            rendered_rows.append(rendered_row)
        body = "\n".join(rendered_rows)
        rendered = f"{opening}\n{body}\n\\end{{ganttchart}}\n"
        return self.add_comment(rendered)

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data.update(
            {
                "type": "GanttChart",
                "start": self.start,
                "end": self.end,
                "rows": self.rows,
            }
        )
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GanttChart:
        restored = cls._copy_value(data)
        if not isinstance(restored, dict):
            raise TypeError("Serialized Gantt chart data must be a dict.")
        kwargs = restored.get("kwargs", {})
        if not isinstance(kwargs, dict):
            raise TypeError("Serialized Gantt chart kwargs must be a dict.")
        return cls(
            start=restored["start"],
            end=restored["end"],
            rows=restored.get("rows", []),
            label=restored.get("label"),
            comment=restored.get("comment"),
            layer=restored.get("layer", 0),
            options=restored.get("options"),
            **kwargs,
        )

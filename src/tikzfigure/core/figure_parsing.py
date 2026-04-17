from __future__ import annotations

import re
from typing import Any, Self

from tikzfigure.core.layer import LayerCollection
from tikzfigure.core.path import TikzPath


class FigureParsingMixin:
    @property
    def layers(self) -> LayerCollection:
        raise NotImplementedError

    def add_node(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    def _add_path(self, *args: Any, **kwargs: Any) -> TikzPath:
        raise NotImplementedError

    def _load_tikz_code(self, tikz_code: str) -> None:
        lines = tikz_code.split("\n")
        lines = [line.lstrip().rstrip() for line in lines]
        lines = [line for line in lines if line not in ["", "\n"]]
        lines = [line for line in lines if not line[0] == "%"]

        merged_lines: list[str] = []
        multiline_command: str | None = None
        for line in lines:
            if multiline_command is not None:
                multiline_command = f"{multiline_command} {line.strip()}"
                if line.endswith(";"):
                    merged_lines.append(multiline_command)
                    multiline_command = None
                continue

            if line.startswith(
                ("\\draw", "\\filldraw", "\\path", "\\fill")
            ) and not line.endswith(";"):
                multiline_command = line
                continue

            merged_lines.append(line)

        if multiline_command is not None:
            merged_lines.append(multiline_command)

        lines = merged_lines

        assert lines[0] == "\\begin{tikzpicture}", f"Found: {lines[0]}"
        assert lines[-1] == "\\end{tikzpicture}", f"Found: {lines[-1]}"

        current_layer = 0
        for line in lines[1:-1]:
            line = re.sub(r" +", " ", line)

            match_pgfdeclarelayer = re.search(r"\\pgfdeclarelayer\{(\d+)\}", line)
            if match_pgfdeclarelayer:
                layer = int(match_pgfdeclarelayer.group(1))
                self.layers.add_layer(layer)

            match_begin_pgfonlayer = re.search(
                r"\\begin\{pgfonlayer\}\{(\d+)\}",
                line,
            )
            if match_begin_pgfonlayer:
                current_layer = int(match_begin_pgfonlayer.group(1))

            match_end_pgfonlayer = re.search(r"\\end\{pgfonlayer\}\{(\d+)\}", line)
            if match_end_pgfonlayer:
                current_layer = 0

            match_node = re.search(
                r"\\node(?:\[([^\]]+)\])? \((\w+)\) at \(([^)]+)\) \{(.*)\};",
                line,
            )
            if match_node:
                attributes = match_node.group(1)
                attributes = [
                    attribute.lstrip().rstrip() for attribute in attributes.split(",")
                ]
                attributes = [
                    attribute for attribute in attributes if not attribute == ""
                ]
                attributes_dict = dict(attr.split("=") for attr in attributes)
                node_name = match_node.group(2)
                coordinates_str = match_node.group(3)
                coordinates = [c.strip() for c in coordinates_str.split(",")]
                parsed_coords: list[int | float | str] = []
                for c in coordinates:
                    if c.startswith("{") and c.endswith("}"):
                        c = c[1:-1]
                    parsed: int | float | str
                    try:
                        parsed = int(c) if "." not in c else float(c)
                    except ValueError:
                        parsed = c
                    parsed_coords.append(parsed)
                coordinates = parsed_coords
                content = match_node.group(4)

                self.add_node(
                    x=coordinates[0],
                    y=coordinates[1],
                    label=node_name,
                    layer=current_layer,
                    content=content,
                    **attributes_dict,
                )

            match_draw = re.search(
                r"\\draw(?:\[([^\]]+)\])? ((?:\(\w+\.*\) to )+\(\w+\.*\));",
                line,
            )
            if match_draw:
                attributes = match_draw.group(1)
                attributes = [
                    attribute.lstrip().rstrip() for attribute in attributes.split(",")
                ]
                attributes = [
                    attribute for attribute in attributes if not attribute == ""
                ]
                path = match_draw.group(2)
                nodes = re.findall(r"\((\w+)\.*\)", path)

                attrs_kwargs = {}
                attrs_options = []
                for attr in attributes:
                    if "=" in attr:
                        k, v = attr.split("=", 1)
                        attrs_kwargs[k.strip().replace(" ", "_")] = v.strip()
                    else:
                        attrs_options.append(attr)
                self._add_path(
                    nodes,
                    options=attrs_options or None,
                    layer=current_layer,
                    **attrs_kwargs,
                )

    @classmethod
    def from_tikz_code(cls, tikz_code: str, **kwargs: Any) -> Self:
        """Create a TikzFigure by parsing existing TikZ source code.

        Args:
            tikz_code: A string containing a ``tikzpicture`` environment.
            **kwargs: Additional keyword arguments forwarded to
                :meth:`__init__`.

        Returns:
            A new :class:`TikzFigure` with nodes and paths reconstructed
            from *tikz_code*.
        """
        return cls(tikz_code=tikz_code, **kwargs)  # type: ignore[call-arg]

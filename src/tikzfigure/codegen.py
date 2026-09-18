"""Generate Python code that rebuilds a :class:`~tikzfigure.TikzFigure`.

This is the counterpart of :mod:`tikzfigure.parser`: where the parser turns
TikZ source into a figure, this module turns a figure back into the
``fig.add_node(...)`` / ``fig.draw(...)`` calls that would create it. Together
they convert existing TikZ code into a tikzfigure script::

    python -m tikzfigure.codegen figure.tikz

By default the generated code is executed and its TikZ output compared with
the original figure, so the result is verified rather than merely plausible.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

from tikzfigure.core.circle import Circle
from tikzfigure.core.coordinate import Coordinate, TikzCoordinate
from tikzfigure.core.loop import Loop
from tikzfigure.core.node import Node
from tikzfigure.core.path import TikzPath
from tikzfigure.core.raw import RawTikz
from tikzfigure.core.rectangle import Rectangle
from tikzfigure.core.scope import Scope
from tikzfigure.units import TikzDimension

if TYPE_CHECKING:
    from tikzfigure.core.figure import TikzFigure

INDENT = "    "

#: Path commands with a dedicated TikzFigure method.
_PATH_METHODS = {
    "draw": "draw",
    "fill": "fill",
    "filldraw": "filldraw",
    "clip": "clip",
    "path": "path",
}


class CodegenError(RuntimeError):
    """Raised when a figure cannot be turned into equivalent Python code."""


def literal(value: Any) -> str:
    """Render *value* as Python source.

    Strings containing backslashes become raw strings, which keeps generated
    TikZ readable (``r"\\draw (0,0);"`` rather than escaped backslashes).
    """
    if isinstance(value, TikzDimension):
        return f"TikzDimension({literal(value.value)}, {literal(value.unit)})"
    if isinstance(value, TikzCoordinate):
        inner = ", ".join(literal(component) for component in value.coordinate)
        return f"TikzCoordinate({inner})"
    if isinstance(value, str):
        if "\\" in value and '"' not in value and not value.endswith("\\"):
            if "\n" in value:
                return f'r"""{value}"""' if '"""' not in value else repr(value)
            return f'r"{value}"'
        return repr(value)
    if isinstance(value, dict):
        inner = ", ".join(f"{literal(k)}: {literal(v)}" for k, v in value.items())
        return "{" + inner + "}"
    if isinstance(value, (list, tuple)):
        inner = ", ".join(literal(v) for v in value)
        if isinstance(value, tuple):
            return f"({inner},)" if len(value) == 1 else f"({inner})"
        return f"[{inner}]"
    if isinstance(value, (bool, int, float)) or value is None:
        return repr(value)
    # Option/spec wrappers (arrows, styles, colors, ...) render as their spec.
    spec = getattr(value, "spec", None)
    if isinstance(spec, str):
        return literal(spec)
    raise CodegenError(f"cannot render {type(value).__name__} as Python source")


def call(target: str, method: str, *args: str, **kwargs: Any) -> str:
    """Render ``target.method(args..., key=value...)``, skipping empty kwargs."""
    parts = list(args)
    parts.extend(f"{key}={literal(value)}" for key, value in kwargs.items())
    return f"{target}.{method}({', '.join(parts)})"


@dataclass
class _Writer:
    lines: list[str] = field(default_factory=list)
    imports: set[str] = field(default_factory=set)
    counters: dict[str, int] = field(default_factory=dict)

    def write(self, text: str, depth: int = 0) -> None:
        self.lines.append(f"{INDENT * depth}{text}" if text else "")

    def name(self, prefix: str) -> str:
        self.counters[prefix] = self.counters.get(prefix, 0) + 1
        return f"{prefix}_{self.counters[prefix]}"


def _option_kwargs(item: Any) -> dict[str, Any]:
    kwargs: dict[str, Any] = {}
    if item.options:
        kwargs["options"] = list(item.options)
    return kwargs


def _common_kwargs(item: Any, layer: int | None, in_container: bool) -> dict[str, Any]:
    kwargs: dict[str, Any] = {}
    if item.comment is not None:
        kwargs["comment"] = item.comment
    if not in_container and layer:
        kwargs["layer"] = layer
    return kwargs


def _waypoint(node: Any, anchor: str | None) -> Any:
    """Render one path waypoint as a label string or coordinate tuple."""
    if isinstance(node, (Node, Coordinate)):
        label = node.label
        if not label:
            raise CodegenError("path refers to a node without a label")
        return f"{label}.{anchor}" if anchor else label
    if isinstance(node, TikzCoordinate):
        if anchor:
            raise CodegenError("anchor on an inline coordinate")
        return tuple(node.coordinate)
    raise CodegenError(f"unsupported path waypoint {type(node).__name__}")


class _FigureCodegen:
    """Emit Python statements rebuilding a figure."""

    def __init__(self, figure: TikzFigure, name: str) -> None:
        self.figure = figure
        self.name = name
        self.writer = _Writer()

    # ------------------------------------------------------------------ #
    # Items

    def emit_item(self, item: Any, target: str, layer: int, depth: int) -> None:
        in_container = target != self.name
        for kind, emitter in (
            (Node, self._emit_node),
            (Coordinate, self._emit_coordinate),
            (TikzPath, self._emit_path),
            ((Circle, Rectangle), self._emit_shape),
            (RawTikz, self._emit_raw),
            (Scope, self._emit_scope),
            (Loop, self._emit_loop),
        ):
            if isinstance(item, kind):
                emitter(item, target, layer, depth, in_container)
                return
        self._emit_generic(item, target, layer, depth, in_container)

    def _call_reproduces(
        self,
        method: str,
        args: list[Any],
        kwargs: dict[str, Any],
        item: Any,
        referenced: list[Any] | None = None,
    ) -> bool:
        """Check that a TikzFigure method really rebuilds *item*.

        Methods such as :meth:`TikzFigure.draw` and :meth:`add_node` accept
        some TikZ options as named parameters and re-emit them in their own
        order (``arrows="->"`` even becomes a flag option), so a keyword
        round trip is not always faithful. Containers build their objects
        directly and need no such check.
        """
        from tikzfigure.core.figure import TikzFigure

        scratch = TikzFigure()
        for node in referenced or []:
            scratch.layers.add_item(item=node, layer=0)
        try:
            rebuilt = getattr(scratch, method)(*args, **kwargs)
        except (TypeError, ValueError):
            return False
        if isinstance(item, Scope):
            return bool(rebuilt.tikz_options() == item.tikz_options())
        return bool(rebuilt.to_tikz() == item.to_tikz())

    def _emit_node(
        self, node: Node, target: str, layer: int, depth: int, in_container: bool
    ) -> None:
        args = []
        if node.coordinate is not None:
            args = [literal(value) for value in node.coordinate.coordinate]
        kwargs: dict[str, Any] = {}
        if node.label:
            # Always explicit: TikzFigure.add_node() advances its auto-label
            # counter differently depending on how a node was created.
            kwargs["label"] = node.label
        if node.content:
            kwargs["content"] = node.content
        kwargs.update(_common_kwargs(node, node.layer, in_container))
        kwargs.update(_option_kwargs(node))
        kwargs.update(node.kwargs)
        values = list(node.coordinate.coordinate) if node.coordinate else []
        if not in_container and not self._call_reproduces(
            "add_node", values, kwargs, node
        ):
            self._emit_generic(node, target, layer, depth, in_container)
            return
        self.writer.write(call(target, "add_node", *args, **kwargs), depth)

    def _emit_coordinate(
        self, coord: Coordinate, target: str, layer: int, depth: int, in_container: bool
    ) -> None:
        args = [literal(coord.label)]
        kwargs: dict[str, Any] = {}
        if coord._at is not None:
            kwargs["at"] = coord._at
        else:
            assert coord._coordinate is not None
            args += [literal(value) for value in coord._coordinate.coordinate]
        if coord.comment is not None:
            kwargs["comment"] = coord.comment
        if not in_container and layer:
            kwargs["layer"] = layer
        self.writer.write(call(target, "add_coordinate", *args, **kwargs), depth)

    def _emit_path(
        self, path: TikzPath, target: str, layer: int, depth: int, in_container: bool
    ) -> None:
        method = _PATH_METHODS.get(path.tikz_command)
        if method is None or path.label:
            self._emit_generic(path, target, layer, depth, in_container)
            return
        anchors = path.node_anchors or [None] * len(path.nodes)
        nodes = [_waypoint(node, anchor) for node, anchor in zip(path.nodes, anchors)]
        kwargs: dict[str, Any] = {}
        if path.center:
            kwargs["center"] = True
        if path.cycle:
            kwargs["cycle"] = True
        if path.segment_options is not None:
            kwargs["segment_options"] = path.segment_options
        kwargs.update(_common_kwargs(path, layer, in_container))
        kwargs.update(_option_kwargs(path))
        kwargs.update(path.kwargs)
        referenced = [n for n in path.nodes if isinstance(n, (Node, Coordinate))]
        if not in_container and not self._call_reproduces(
            method, [nodes], kwargs, path, referenced
        ):
            self._emit_generic(path, target, layer, depth, in_container)
            return
        self.writer.write(call(target, method, literal(nodes), **kwargs), depth)

    def _emit_shape(
        self, shape: Any, target: str, layer: int, depth: int, in_container: bool
    ) -> None:
        # TikzFigure.circle()/rectangle() take no flag-style options and only
        # exist on the figure itself.
        if shape.options or in_container or shape.tikz_command != "draw":
            self._emit_generic(shape, target, layer, depth, in_container)
            return
        if isinstance(shape, Circle):
            args = [literal(tuple(shape.center.coordinate)), literal(shape._radius)]
            method = "circle"
        else:
            args = [
                literal(tuple(shape.corner1.coordinate)),
                literal(tuple(shape.corner2.coordinate)),
            ]
            method = "rectangle"
        kwargs = _common_kwargs(shape, layer, in_container)
        kwargs.update(shape.kwargs)
        values = (
            [tuple(shape.center.coordinate), shape._radius]
            if isinstance(shape, Circle)
            else [tuple(shape.corner1.coordinate), tuple(shape.corner2.coordinate)]
        )
        if not self._call_reproduces(method, values, kwargs, shape):
            self._emit_generic(shape, target, layer, depth, in_container)
            return
        self.writer.write(call(target, method, *args, **kwargs), depth)

    def _emit_raw(
        self, raw: RawTikz, target: str, layer: int, depth: int, in_container: bool
    ) -> None:
        self.writer.write(call(target, "add_raw", literal(raw.tikz_code)), depth)

    def _emit_scope(
        self, scope: Scope, target: str, layer: int, depth: int, in_container: bool
    ) -> None:
        kwargs = _common_kwargs(scope, layer, in_container)
        kwargs.update(_option_kwargs(scope))
        kwargs.update(scope.kwargs)
        variable = self.writer.name("scope")
        self.writer.write(
            f"with {call(target, 'add_scope', **kwargs)} as {variable}:", depth
        )
        self._emit_body(scope.items, variable, layer, depth + 1)

    def _emit_loop(
        self, loop: Loop, target: str, layer: int, depth: int, in_container: bool
    ) -> None:
        if loop._range_spec is not None:
            spec = loop._range_spec
            values = f"range({spec['start']}, {spec['stop']}, {spec['step']})"
        else:
            values = literal(loop.values)
        kwargs: dict[str, Any] = {}
        if loop.comment is not None:
            kwargs["comment"] = loop.comment
        if not in_container and layer:
            kwargs["layer"] = layer
        variable = self.writer.name("loop")
        header = call(target, "add_loop", literal(loop.variable), values, **kwargs)
        self.writer.write(f"with {header} as {variable}:", depth)
        self._emit_body(loop.items, variable, layer, depth + 1)

    def _emit_generic(
        self, item: Any, target: str, layer: int, depth: int, in_container: bool
    ) -> None:
        """Rebuild any other TikzObject through its own constructor."""
        init_kwargs = getattr(item, "_copy_init_kwargs", None)
        if init_kwargs is None:
            raise CodegenError(
                f"cannot generate Python for {type(item).__name__} objects"
            )
        cls = type(item)
        defaults = {
            "label": "",
            "layer": 0,
            "comment": None,
            "options": [],
            "cycle": False,
            "center": False,
            "tikz_command": "draw",
        }
        kwargs = {
            key: value
            for key, value in init_kwargs().items()
            if value is not None
            and value != []
            and defaults.get(key, object()) != value
        }
        sources = {}
        if isinstance(item, TikzPath):
            # Paths hold references to Node/Coordinate objects; look them up
            # by label in the generated code.
            sources["nodes"] = self._waypoints_source(item, target)
            kwargs.pop("nodes", None)
        self.writer.imports.add(f"from {cls.__module__} import {cls.__name__}")
        arguments = [f"{key}={source}" for key, source in sources.items()]
        arguments += [f"{key}={literal(value)}" for key, value in kwargs.items()]
        construction = f"{cls.__name__}({', '.join(arguments)})"
        if in_container:
            self.writer.write(call(target, "add", construction), depth)
        else:
            self.writer.write(call(target, "add", construction, layer=layer), depth)

    def _waypoints_source(self, path: TikzPath, target: str) -> str:
        """Render a path's waypoints, resolving node references by label."""
        lookup = (
            f"{target}.get_node"
            if target != self.name
            else f"{self.name}.layers.get_node"
        )
        parts = []
        for node in path.nodes:
            if isinstance(node, (Node, Coordinate)):
                if not node.label:
                    raise CodegenError("path refers to a node without a label")
                parts.append(f"{lookup}({literal(node.label)})")
            else:
                parts.append(literal(node))
        return f"[{', '.join(parts)}]"

    def _emit_body(self, items: list, target: str, layer: int, depth: int) -> None:
        if not items:
            self.writer.write("pass", depth)
        for item in items:
            self.emit_item(item, target, layer, depth)

    # ------------------------------------------------------------------ #
    # Figure

    def _figure_kwargs(self) -> dict[str, Any]:
        figure = self.figure
        kwargs: dict[str, Any] = {}
        defaults: list[tuple[str, Any, Any]] = [
            ("ndim", figure.ndim, 2),
            ("label", figure._label, None),
            ("grid", figure._grid, False),
            ("show_axes", figure._show_axes, False),
            ("figsize", figure._figsize, (10, 6)),
            ("description", figure._description, None),
            ("extra_packages", figure.extra_packages, None),
            ("document_setup", figure.document_setup, None),
            ("figure_setup", figure._figure_setup, None),
            ("rows", figure._subfigure_rows, None),
            ("cols", figure._subfigure_cols, None),
        ]
        for key, value, default in defaults:
            if value != default:
                kwargs[key] = value
        return kwargs

    def build(self) -> str:
        figure = self.figure
        if figure.axes or figure._subfigure_axes or figure._subfigure_grid:
            raise CodegenError(
                "figures with pgfplots axes or subfigures are not supported yet"
            )
        writer = self.writer
        writer.write(
            f"{self.name} = TikzFigure({_kwargs_source(self._figure_kwargs())})"
        )

        if figure.tikz_libraries:
            libraries = ", ".join(literal(lib) for lib in figure.tikz_libraries)
            writer.write(f"{self.name}.usetikzlibrary({libraries})")
        for style in figure.named_styles:
            kwargs = dict(style["kwargs"])
            if style["options"]:
                kwargs = {"options": list(style["options"]), **kwargs}
            writer.write(call(self.name, "add_style", literal(style["name"]), **kwargs))
        for variable in figure.variables:
            writer.write(
                call(
                    self.name,
                    "add_variable",
                    literal(variable.label),
                    literal(variable.value),
                )
            )
        for function in figure.declared_functions:
            writer.write(
                call(
                    self.name,
                    "declare_function",
                    literal(function.name),
                    literal(function.args),
                    literal(function.body),
                )
            )
        for color_name, color in figure.colors:
            writer.write(
                call(
                    self.name,
                    "colorlet",
                    literal(color_name),
                    literal(color.color_spec),
                )
            )

        layer_keys: list[int] = []
        for layer_key in figure.layers.layers:
            if not isinstance(layer_key, int):
                raise CodegenError(f"unsupported layer name {layer_key!r}")
            layer_keys.append(layer_key)
        if len(layer_keys) > 1:
            # Fix the layer order up front: it decides the output order, and
            # layers are emitted below in dependency order instead.
            for layer_key in layer_keys:
                writer.write(
                    call(f"{self.name}.layers", "add_layer", literal(layer_key))
                )

        for layer_key in self._layer_order(layer_keys):
            for item in figure.layers.layers[layer_key].items:
                self.emit_item(item, self.name, layer_key, depth=0)
        return "\n".join(writer.lines)

    def _layer_order(self, layer_keys: list[int]) -> list[int]:
        """Order layers so referenced nodes are defined before they are used.

        A path may live on one layer while the nodes it connects live on
        another, and the generated code refers to nodes by label.
        """
        defined: set[str] = set()
        pending = list(layer_keys)
        order: list[int] = []
        while pending:
            for layer_key in pending:
                items = self.figure.layers.layers[layer_key].items
                if _referenced_labels(items) <= defined | _defined_labels(items):
                    order.append(layer_key)
                    defined |= _defined_labels(items)
                    pending.remove(layer_key)
                    break
            else:
                # Cyclic references across layers: keep the original order.
                order.extend(pending)
                break
        return order


def _defined_labels(items: list) -> set[str]:
    """Labels of nodes and coordinates defined by *items*, including nested."""
    labels: set[str] = set()
    for item in items:
        if isinstance(item, (Node, Coordinate)) and item.label:
            labels.add(item.label)
        nested = getattr(item, "items", None)
        if nested is not None:
            labels |= _defined_labels(nested)
    return labels


def _referenced_labels(items: list) -> set[str]:
    """Labels that paths in *items* refer to, including nested containers."""
    labels: set[str] = set()
    for item in items:
        if isinstance(item, TikzPath):
            labels |= {
                node.label
                for node in item.nodes
                if isinstance(node, (Node, Coordinate)) and node.label
            }
        nested = getattr(item, "items", None)
        if nested is not None:
            labels |= _referenced_labels(nested)
    return labels


def _imports_source(imports: set[str]) -> str:
    """Render import lines, merging names imported from the same module."""
    by_module: dict[str, set[str]] = {}
    for line in imports:
        module, _, names = line.partition(" import ")
        by_module.setdefault(module, set()).update(n.strip() for n in names.split(","))
    return "\n".join(
        f"{module} import {', '.join(sorted(names))}"
        for module, names in sorted(by_module.items())
    )


def _kwargs_source(kwargs: dict[str, Any]) -> str:
    return ", ".join(f"{key}={literal(value)}" for key, value in kwargs.items())


def figure_to_python(
    figure: TikzFigure,
    name: str = "fig",
    header: bool = True,
    verify: bool = True,
) -> str:
    """Return Python source code that rebuilds *figure*.

    Args:
        figure: The figure to describe.
        name: Variable name used for the figure in the generated code.
        header: Include the ``import`` lines.
        verify: Execute the generated code and check that it produces the
            same TikZ output as *figure*.

    Returns:
        Python source code.

    Raises:
        CodegenError: If the figure uses features that cannot be expressed
            (pgfplots axes, subfigures, non-integer layers), or if *verify*
            is set and the generated code does not reproduce the figure.
    """
    generator = _FigureCodegen(figure, name)
    body = generator.build()
    imports = {"from tikzfigure import TikzFigure"} | generator.writer.imports
    if any("TikzCoordinate(" in line for line in generator.writer.lines):
        imports.add("from tikzfigure import TikzCoordinate")
    if any("TikzDimension(" in line for line in generator.writer.lines):
        imports.add("from tikzfigure.units import TikzDimension")
    complete = _imports_source(imports) + "\n\n" + body + "\n"
    code = complete if header else body + "\n"

    if verify:
        # Always verify the code including its imports, so that
        # ``header=False`` output is checked too.
        rebuilt = run_generated_code(complete, name=name)
        expected = figure.generate_tikz()
        if rebuilt.generate_tikz() != expected:
            raise CodegenError(
                "generated code does not reproduce the figure; please report "
                "this with the figure that triggered it"
            )
    return code


def run_generated_code(code: str, name: str = "fig") -> TikzFigure:
    """Execute generated code and return the figure it builds."""
    namespace: dict[str, Any] = {}
    exec(compile(code, "<tikzfigure-codegen>", "exec"), namespace)  # noqa: S102
    from tikzfigure.core.figure import TikzFigure

    figure = namespace.get(name)
    if not isinstance(figure, TikzFigure):
        raise CodegenError(f"generated code did not define a figure named {name!r}")
    return figure


def tikz_to_python(
    source: str, name: str = "fig", header: bool = True, verify: bool = True
) -> str:
    """Convert TikZ source directly into tikzfigure Python code."""
    from tikzfigure.parser import parse_tikz

    figure = parse_tikz(source).figure
    return figure_to_python(figure, name=name, header=header, verify=verify)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m tikzfigure.codegen",
        description="Convert a TikZ file into Python code that builds the figure.",
    )
    parser.add_argument("file", help="file containing a tikzpicture ('-' for stdin)")
    parser.add_argument("-o", "--output", help="write to this file instead of stdout")
    parser.add_argument("--name", default="fig", help="figure variable name")
    parser.add_argument(
        "--no-verify",
        action="store_true",
        help="skip executing the generated code to check it",
    )
    args = parser.parse_args(argv)

    source = sys.stdin.read() if args.file == "-" else Path(args.file).read_text()
    code = tikz_to_python(source, name=args.name, verify=not args.no_verify)
    if args.output:
        Path(args.output).write_text(code)
    else:
        print(code, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())

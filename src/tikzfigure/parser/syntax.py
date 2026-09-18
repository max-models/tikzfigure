"""Syntax layer: TikZ options, coordinates and path operations.

Statements produced by :func:`~tikzfigure.parser.lexer.split_statements`
are broken into a flat list of :class:`PathToken` objects here. The same
tokens are used to build library objects *and* to compare rendered output
against the original source (see :func:`canonical_path` and
:func:`canonical_node`), which is what lets the parser guarantee that a
mapped statement renders to equivalent TikZ.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from tikzfigure.parser.lexer import (
    Scanner,
    TikzParseError,
    normalize_space,
    split_top_level,
    strip_comments,
)

_WORD = re.compile(r"[A-Za-z]+")
_NAME = re.compile(r"[A-Za-z0-9_\-\\]*(\.[A-Za-z0-9_ \-]+)?")
_OPERATORS = ("--", "..", "|-", "-|")
_SIMPLE_COMPONENT_CHARS = re.compile(r"[,()\[\]:{}]")


@dataclass(frozen=True)
class Option:
    """A single TikZ option such as ``thick`` or ``line width=2pt``."""

    raw: str
    key: str | None = None
    value: str | None = None

    @property
    def canonical(self) -> str:
        if self.key is None:
            return normalize_space(self.raw)
        return f"{normalize_space(self.key)}={normalize_space(self.value or '')}"


def parse_options(inner: str) -> list[Option]:
    """Parse the inside of a ``[...]`` option block."""
    options: list[Option] = []
    for part in split_top_level(strip_comments(inner), ","):
        raw = normalize_space(part)
        if not raw:
            continue
        pieces = split_top_level(raw, "=")
        if len(pieces) >= 2 and pieces[0].strip():
            key = pieces[0].strip()
            value = "=".join(pieces[1:]).strip()
            options.append(Option(raw=f"{key}={value}", key=key, value=value))
        else:
            options.append(Option(raw=raw))
    return options


@dataclass(frozen=True)
class Coord:
    """A parenthesised TikZ coordinate.

    Attributes:
        inner: Text between the parentheses, whitespace-normalised.
        prefix: ``""``, ``"+"`` or ``"++"`` for relative coordinates.
        kind: ``"named"`` (``(a)``/``(a.north)``), ``"cartesian"``
            (``(1, 2)``/``(1, 2, 3)``), ``"polar"`` (``(30:1cm)``),
            ``"calc"`` (``($(a)+(1,0)$)``) or ``"other"``.
    """

    inner: str
    prefix: str = ""

    @property
    def components(self) -> list[str]:
        return [part.strip() for part in split_top_level(self.inner, ",")]

    @property
    def kind(self) -> str:
        text = self.inner
        if text.startswith("$") and text.endswith("$"):
            return "calc"
        parts = self.components
        if len(parts) in (2, 3) and all(parts):
            if any(re.match(r"^[a-z ]+cs\s*:", p) for p in parts[:1]):
                return "other"
            return "cartesian"
        if len(parts) == 1 and len(split_top_level(text, ":")) >= 2:
            return "polar"
        if _NAME.fullmatch(text):
            return "named"
        return "other"

    @property
    def name(self) -> str:
        return self.inner.split(".", 1)[0]

    @property
    def anchor(self) -> str | None:
        return self.inner.split(".", 1)[1] if "." in self.inner else None

    @property
    def canonical(self) -> str:
        if self.kind == "cartesian":
            return self.prefix + ",".join(
                canonical_component(p) for p in self.components
            )
        return self.prefix + self.inner


def unbrace_component(text: str) -> str:
    """Strip one pair of wrapping braces from a coordinate component."""
    text = text.strip()
    if text.startswith("{") and text.endswith("}"):
        scanner = Scanner(text)
        try:
            scanner.read_group("{")
        except TikzParseError:
            return text
        if scanner.eof():
            return text[1:-1].strip()
    return text


def canonical_component(text: str) -> str:
    """Canonical form of a coordinate component for equivalence checks.

    Braces are only insignificant when the content has no characters that
    would otherwise confuse TikZ's coordinate parser.
    """
    inner = unbrace_component(text)
    if inner != text.strip() and _SIMPLE_COMPONENT_CHARS.search(inner):
        return "{" + normalize_space(inner) + "}"
    return normalize_space(inner)


@dataclass(frozen=True)
class PathToken:
    """One element of a path: options, coordinate, operator, word or group.

    Attributes:
        kind: ``"options"``, ``"coord"``, ``"op"``, ``"word"``, ``"group"``
            or ``"text"``.
        text: Operator, keyword, group body or raw text.
        options: Parsed options for ``"options"`` tokens.
        coord: Parsed coordinate for ``"coord"`` tokens.
    """

    kind: str
    text: str = ""
    options: tuple[Option, ...] = ()
    coord: Coord | None = None

    def is_word(self, *words: str) -> bool:
        return self.kind == "word" and self.text in words

    @property
    def canonical(self) -> tuple[str, ...]:
        if self.kind == "options":
            return ("options", *(o.canonical for o in self.options))
        if self.kind == "coord":
            assert self.coord is not None
            return ("coord", self.coord.canonical)
        if self.kind == "group":
            return ("group", normalize_space(self.text))
        return (self.kind, self.text)


@dataclass
class CommandSyntax:
    """A ``;``-terminated command split into name and path tokens."""

    name: str
    tokens: list[PathToken]


def tokenize_path(text: str) -> list[PathToken]:
    """Split the body of a path command into :class:`PathToken` objects."""
    scanner = Scanner(strip_comments(text))
    tokens: list[PathToken] = []
    while True:
        scanner.skip_whitespace()
        if scanner.eof():
            return tokens
        char = scanner.peek()
        if char == "[":
            inner = scanner.read_group("[")
            tokens.append(
                PathToken("options", text=inner, options=tuple(parse_options(inner)))
            )
        elif char == "(":
            inner = scanner.read_group("(")
            tokens.append(PathToken("coord", coord=Coord(normalize_space(inner))))
        elif char == "+":
            prefix = "++" if scanner.startswith("++") else "+"
            scanner.pos += len(prefix)
            scanner.skip_whitespace()
            if scanner.peek() != "(":
                tokens.append(PathToken("text", text=prefix))
                continue
            inner = scanner.read_group("(")
            tokens.append(
                PathToken("coord", coord=Coord(normalize_space(inner), prefix=prefix))
            )
        elif char == "{":
            tokens.append(PathToken("group", text=scanner.read_group("{").strip()))
        elif any(scanner.startswith(op) for op in _OPERATORS):
            op = next(op for op in _OPERATORS if scanner.startswith(op))
            scanner.pos += len(op)
            tokens.append(PathToken("op", text=op))
        elif char == "\\":
            start = scanner.pos
            scanner.read_control_word()
            tokens.append(PathToken("text", text=scanner.text[start : scanner.pos]))
        else:
            match = _WORD.match(scanner.text, scanner.pos)
            if match:
                scanner.pos = match.end()
                tokens.append(PathToken("word", text=match.group(0)))
            else:
                scanner.pos += 1
                tokens.append(PathToken("text", text=char))


def parse_command(text: str) -> CommandSyntax:
    """Parse ``\\name ... ;`` into a :class:`CommandSyntax`."""
    scanner = Scanner(text.strip())
    name = scanner.read_control_word()
    if name is None:
        raise TikzParseError("expected a command")
    body = scanner.text[scanner.pos :].rstrip()
    body = body.removesuffix(";")
    return CommandSyntax(name=name, tokens=tokenize_path(body))


# ---------------------------------------------------------------------- #
# Canonical forms


def canonical_path(tokens: list[PathToken]) -> tuple[tuple[str, ...], ...]:
    """Whitespace- and brace-insensitive representation of path tokens."""
    return tuple(
        token.canonical
        for token in tokens
        if not (token.kind == "options" and not token.options)
    )


@dataclass
class NodeSyntax:
    """A ``\\node`` statement in normalised form."""

    options: list[Option]
    name: str | None
    at: Coord | None
    content: str
    rest: list[PathToken]


def parse_node_tokens(tokens: list[PathToken]) -> NodeSyntax | None:
    """Interpret tokens after ``\\node`` as ``[opts] (name) at (c) {text}``.

    Options may be interleaved with the name and position, as TikZ allows.
    Returns ``None`` if the tokens do not have that shape.
    """
    options: list[Option] = []
    name: str | None = None
    at: Coord | None = None
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token.kind == "options":
            options.extend(token.options)
        elif token.kind == "coord" and name is None and at is None:
            assert token.coord is not None
            if token.coord.prefix or token.coord.kind != "named":
                if token.coord.inner != "":
                    return None
            name = token.coord.inner
        elif token.is_word("at") and at is None:
            if i + 1 >= len(tokens) or tokens[i + 1].kind != "coord":
                return None
            at = tokens[i + 1].coord
            i += 1
        elif token.kind == "group":
            return NodeSyntax(options, name, at, token.text, tokens[i + 1 :])
        else:
            return None
        i += 1
    return None


def canonical_node(node: NodeSyntax, include_name: bool = True) -> tuple:
    return (
        tuple(o.canonical for o in node.options),
        (node.name or "") if include_name else None,
        node.at.canonical if node.at else None,
        normalize_space(node.content),
        canonical_path(node.rest),
    )

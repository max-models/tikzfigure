"""Brace-aware scanning of TikZ source.

TikZ is not a context-free language, so this module does not try to fully
tokenize it. Instead it provides a :class:`Scanner` that understands the
parts of TeX syntax that decide where a TikZ construct *ends*: balanced
``{}``/``[]``/``()`` groups, escaped characters, ``%`` comments and control
words. :func:`split_statements` builds on it to cut a ``tikzpicture`` body
into top-level statements without being confused by ``;`` inside braces,
multi-line commands or trailing comments.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

_CONTROL_WORD = re.compile(r"\\([A-Za-z@]+|.)")

#: Commands that form a TikZ path and are terminated by a top-level ``;``.
PATH_COMMANDS: frozenset[str] = frozenset(
    {
        "draw",
        "fill",
        "filldraw",
        "path",
        "clip",
        "node",
        "coordinate",
        "shade",
        "shadedraw",
        "pattern",
        "pic",
        "matrix",
        "graph",
        "useasboundingbox",
        "datavisualization",
        "spy",
        "addplot",
        "addplot3",
        "addlegendentry",
        "calendar",
        "chainin",
    }
)


class TikzParseError(ValueError):
    """Raised when TikZ source is malformed or cannot be parsed."""

    def __init__(self, message: str, line: int | None = None) -> None:
        self.line = line
        if line is not None:
            message = f"line {line}: {message}"
        super().__init__(message)


@dataclass
class Statement:
    """One top-level construct of a ``tikzpicture`` body.

    Attributes:
        kind: ``"command"`` for ``;``-terminated path commands and macros,
            ``"environment"`` for ``\\begin{...}``/``\\end{...}`` blocks,
            ``"foreach"`` for ``\\foreach`` loops, ``"comment"`` for a full
            comment line and ``"text"`` for anything else.
        name: Command or environment name without the backslash
            (e.g. ``"draw"``, ``"scope"``).
        text: Source text of the statement, including any comments inside it.
        line: 1-based line number where the statement starts.
        comments: Comment lines (without ``%``) directly preceding the
            statement.
    """

    kind: str
    name: str
    text: str
    line: int
    comments: list[str] = field(default_factory=list)

    @property
    def label(self) -> str:
        """Short human-readable identifier used in diagnostics."""
        if self.kind == "environment":
            return f"\\begin{{{self.name}}}"
        if self.kind in ("command", "foreach"):
            return f"\\{self.name}"
        return self.kind


class Scanner:
    """Cursor over TikZ source with helpers for balanced groups."""

    _CLOSERS = {"{": "}", "[": "]", "(": ")"}

    def __init__(self, text: str, pos: int = 0, line_offset: int = 0) -> None:
        self.text = text
        self.pos = pos
        self.line_offset = line_offset

    # ------------------------------------------------------------------ #
    # Basic cursor helpers

    def eof(self) -> bool:
        return self.pos >= len(self.text)

    def peek(self, n: int = 1) -> str:
        return self.text[self.pos : self.pos + n]

    def line_at(self, pos: int | None = None) -> int:
        pos = self.pos if pos is None else pos
        return self.text.count("\n", 0, pos) + 1 + self.line_offset

    def error(self, message: str, pos: int | None = None) -> TikzParseError:
        return TikzParseError(message, line=self.line_at(pos))

    def skip_whitespace(self) -> None:
        while not self.eof() and self.text[self.pos].isspace():
            self.pos += 1

    def skip_space_and_comments(self) -> None:
        while not self.eof():
            char = self.text[self.pos]
            if char.isspace():
                self.pos += 1
            elif char == "%":
                self.read_comment()
            else:
                break

    def read_comment(self) -> str:
        """Consume a ``%`` comment up to (not including) the newline."""
        assert self.text[self.pos] == "%"
        end = self.text.find("\n", self.pos)
        if end == -1:
            end = len(self.text)
        comment = self.text[self.pos + 1 : end]
        self.pos = end
        return comment

    def startswith(self, token: str) -> bool:
        return self.text.startswith(token, self.pos)

    def read_control_word(self) -> str | None:
        """Consume ``\\name`` and return ``name``, or ``None`` if absent."""
        match = _CONTROL_WORD.match(self.text, self.pos)
        if match is None:
            return None
        self.pos = match.end()
        return match.group(1)

    def peek_control_word(self) -> str | None:
        match = _CONTROL_WORD.match(self.text, self.pos)
        return match.group(1) if match else None

    # ------------------------------------------------------------------ #
    # Groups

    def _skip_escape(self) -> None:
        """Skip a backslash and the character (or control word) after it."""
        match = _CONTROL_WORD.match(self.text, self.pos)
        self.pos = match.end() if match else self.pos + 1

    def read_group(self, opener: str | None = None) -> str:
        """Consume a balanced group and return its inner text.

        ``{}`` groups nest only on braces. ``[]`` and ``()`` groups also
        treat nested braces as opaque, so ``[label={[red]x}]`` and
        ``(${(a)!0.5!(b)}$)`` are read correctly.

        Args:
            opener: Expected opening character. Defaults to the character at
                the cursor.

        Raises:
            TikzParseError: If the group is not closed.
        """
        start = self.pos
        char = self.peek()
        if opener is not None and char != opener:
            raise self.error(f"expected '{opener}', found '{char or 'EOF'}'")
        if char not in self._CLOSERS:
            raise self.error(f"expected a group, found '{char or 'EOF'}'")
        closer = self._CLOSERS[char]
        self.pos += 1
        depth = 1
        while not self.eof():
            current = self.text[self.pos]
            if current == "\\":
                self._skip_escape()
                continue
            if current == "%":
                self.read_comment()
                continue
            if current == "{" and char != "{":
                self.read_group("{")
                continue
            if current == char:
                depth += 1
            elif current == closer:
                depth -= 1
                if depth == 0:
                    self.pos += 1
                    return self.text[start + 1 : self.pos - 1]
            elif current == "}" and char != "{":
                raise self.error(f"unbalanced '}}' inside '{char}' group")
            self.pos += 1
        raise self.error(f"unclosed '{char}'", pos=start)

    def read_until_semicolon(self) -> str:
        """Consume text up to and including the next top-level ``;``."""
        start = self.pos
        while not self.eof():
            current = self.text[self.pos]
            if current == "\\":
                self._skip_escape()
            elif current == "%":
                self.read_comment()
            elif current == "{":
                self.read_group("{")
            elif current == "}":
                raise self.error("unbalanced '}'")
            elif current == ";":
                self.pos += 1
                return self.text[start : self.pos]
            else:
                self.pos += 1
        raise self.error("statement is not terminated by ';'", pos=start)

    def read_rest_of_line(self) -> str:
        end = self.text.find("\n", self.pos)
        if end == -1:
            end = len(self.text)
        chunk = self.text[self.pos : end]
        self.pos = end
        return chunk


# ---------------------------------------------------------------------- #
# Text helpers


def strip_comments(text: str) -> str:
    """Remove ``%`` comments (but not ``\\%``) from *text*."""
    out: list[str] = []
    i = 0
    while i < len(text):
        char = text[i]
        if char == "\\" and i + 1 < len(text):
            out.append(text[i : i + 2])
            i += 2
            continue
        if char == "%":
            end = text.find("\n", i)
            if end == -1:
                break
            i = end
            continue
        out.append(char)
        i += 1
    return "".join(out)


def normalize_space(text: str) -> str:
    """Collapse runs of whitespace into single spaces and strip the ends."""
    return " ".join(text.split())


def split_top_level(text: str, separator: str = ",") -> list[str]:
    """Split *text* on *separator* outside of any ``{}``/``[]``/``()`` group."""
    parts: list[str] = []
    depth = 0
    current: list[str] = []
    i = 0
    while i < len(text):
        char = text[i]
        if char == "\\" and i + 1 < len(text):
            current.append(text[i : i + 2])
            i += 2
            continue
        if char in "{[(":
            depth += 1
        elif char in "}])":
            depth -= 1
        if depth == 0 and text.startswith(separator, i):
            parts.append("".join(current))
            current = []
            i += len(separator)
            continue
        current.append(char)
        i += 1
    parts.append("".join(current))
    return parts


def dedent_lines(text: str) -> str:
    """Strip every line and drop leading/trailing blank lines.

    Leading whitespace carries no meaning in TikZ, and removing it keeps raw
    blocks stable when :meth:`TikzFigure.generate_tikz` re-indents them.
    """
    lines = [line.strip() for line in text.strip().splitlines()]
    return "\n".join(lines)


# ---------------------------------------------------------------------- #
# Statement splitting


def _read_environment(scanner: Scanner, name: str) -> None:
    """Advance past the ``\\end{name}`` matching an already-consumed begin."""
    depth = 1
    pattern = re.compile(r"\\(begin|end)\s*\{" + re.escape(name) + r"\}")
    while not scanner.eof():
        current = scanner.text[scanner.pos]
        if current == "%":
            scanner.read_comment()
            continue
        if current == "\\":
            match = pattern.match(scanner.text, scanner.pos)
            if match:
                scanner.pos = match.end()
                depth += 1 if match.group(1) == "begin" else -1
                if depth == 0:
                    return
                continue
            scanner._skip_escape()
            continue
        scanner.pos += 1
    raise scanner.error(f"missing \\end{{{name}}}")


def _read_macro_arguments(scanner: Scanner) -> None:
    """Consume ``[]``/``{}`` arguments (and ``=[...]``) after a macro name."""
    while True:
        save = scanner.pos
        while scanner.peek() in (" ", "\t"):
            scanner.pos += 1
        char = scanner.peek()
        if char in ("{", "["):
            scanner.read_group()
        elif char == "=":
            # Old-style ``\tikzstyle{name}=[...]``.
            scanner.pos += 1
            scanner.skip_whitespace()
            if scanner.peek() in ("{", "["):
                scanner.read_group()
        else:
            scanner.pos = save
            return


def _read_foreach(scanner: Scanner) -> None:
    """Consume a ``\\foreach`` header and its body (group or statement)."""
    in_match = re.compile(r"\bin\b")
    while True:
        scanner.skip_space_and_comments()
        if scanner.eof():
            raise scanner.error("incomplete \\foreach")
        char = scanner.peek()
        if char in "[{":
            scanner.read_group()
            continue
        match = in_match.match(scanner.text, scanner.pos)
        if match:
            scanner.pos = match.end()
            scanner.skip_space_and_comments()
            if scanner.peek() == "{":
                scanner.read_group("{")
            else:
                word = scanner.read_control_word()
                if word is None:
                    raise scanner.error("expected a value list after 'in'")
            break
        if char == "\\":
            scanner.read_control_word()
            continue
        scanner.pos += 1

    scanner.skip_space_and_comments()
    # Options after the list, e.g. ``\foreach \x in {1,2} [count=\i]`` are
    # not valid TikZ, but ``\foreach ... in {..} {body}`` and a bare
    # statement body are.
    if scanner.peek() == "{":
        scanner.read_group("{")
        return
    name = scanner.read_control_word()
    if name is None:
        raise scanner.error("expected a \\foreach body")
    if name == "foreach":
        _read_foreach(scanner)
    else:
        scanner.read_until_semicolon()


def split_statements(text: str, line_offset: int = 0) -> list[Statement]:
    """Split a ``tikzpicture`` body into top-level :class:`Statement` objects.

    Args:
        text: Body text (without the surrounding environment).
        line_offset: Number of lines preceding *text* in the original
            source, used to report absolute line numbers.

    Raises:
        TikzParseError: For unbalanced groups, unterminated commands or
            unclosed environments.
    """
    scanner = Scanner(text, line_offset=line_offset)
    statements: list[Statement] = []
    pending_comments: list[str] = []
    last_line = 0

    while True:
        last_line = scanner.line_at() if statements else 0
        # Whitespace; a blank line separates comments from the next statement.
        start_ws = scanner.pos
        scanner.skip_whitespace()
        if scanner.text.count("\n", start_ws, scanner.pos) >= 2 and pending_comments:
            for comment in pending_comments:
                statements.append(
                    Statement("comment", "", f"%{comment}", scanner.line_at(start_ws))
                )
            pending_comments = []
        if scanner.eof():
            break

        start = scanner.pos
        line = scanner.line_at()
        char = scanner.peek()

        if char == "%":
            comment = scanner.read_comment()
            if statements and not pending_comments and line == last_line:
                # A trailing comment belongs to the statement before it.
                statements.append(Statement("comment", "", f"%{comment}", line))
            else:
                pending_comments.append(comment)
            continue

        comments, pending_comments = pending_comments, []

        if char == "\\":
            name = scanner.peek_control_word()
            if name == "begin":
                scanner.read_control_word()
                scanner.skip_whitespace()
                env = scanner.read_group("{").strip()
                _read_environment(scanner, env)
                if env == "pgfonlayer":
                    # tikzfigure historically emits ``\end{pgfonlayer}{<n>}``.
                    save = scanner.pos
                    if scanner.peek() == "{":
                        scanner.read_group("{")
                        if "\n" in scanner.text[save : scanner.pos]:
                            scanner.pos = save
                statements.append(
                    Statement(
                        "environment", env, text[start : scanner.pos], line, comments
                    )
                )
                continue
            if name == "end":
                raise scanner.error("unexpected \\end without matching \\begin")
            if name == "foreach":
                scanner.read_control_word()
                _read_foreach(scanner)
                statements.append(
                    Statement(
                        "foreach", name, text[start : scanner.pos], line, comments
                    )
                )
                continue
            if name is not None and name in PATH_COMMANDS:
                scanner.read_until_semicolon()
                statements.append(
                    Statement(
                        "command", name, text[start : scanner.pos], line, comments
                    )
                )
                continue
            if name is not None:
                scanner.read_control_word()
                _read_macro_arguments(scanner)
                save = scanner.pos
                scanner.skip_space_and_comments()
                if scanner.peek() in ("(", "[") or scanner.peek() == ";":
                    # Unknown path-like macro such as a user-defined \mydraw.
                    scanner.pos = save
                    scanner.read_until_semicolon()
                else:
                    scanner.pos = save
                    if scanner.peek() == ";":
                        scanner.pos += 1
                statements.append(
                    Statement(
                        "command", name, text[start : scanner.pos], line, comments
                    )
                )
                continue

        if char == "}":
            raise scanner.error("unbalanced '}'")
        if char == "{":
            scanner.read_group("{")
        else:
            chunk = scanner.read_rest_of_line()
            # Do not swallow a command that starts later on the same line.
            cut = chunk.find("\\")
            if cut > 0:
                scanner.pos = start + cut
        statements.append(
            Statement("text", "", text[start : scanner.pos], line, comments)
        )

    for comment in pending_comments:
        statements.append(Statement("comment", "", f"%{comment}", scanner.line_at()))
    return statements

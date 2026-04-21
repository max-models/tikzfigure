from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from tikzfigure.core.base import TikzObject
from tikzfigure.core.serialization import deserialize_tikz_value, serialize_tikz_value

if TYPE_CHECKING:
    from tikzfigure.math import Expr


class DeclaredFunction(TikzObject):
    """A PGF math function declared with ``\\pgfkeys{/pgf/declare function=...}``.

    Declared functions are emitted near the top of the ``tikzpicture`` so they
    can be reused in variables, coordinates, and expression-based plots. The
    returned object is itself callable, so a declaration like
    ``f = fig.declare_function(...)`` can later be referenced as ``f(x)`` when
    building expressions.
    """

    def __init__(
        self,
        name: str,
        args: str | Sequence[str],
        body: Any,
        comment: str | None = None,
    ) -> None:
        """Initialize a declared PGF function.

        Args:
            name: Function name as used in PGF expressions.
            args: One argument name or a sequence of argument names. Leading
                backslashes are optional.
            body: PGF expression used as the function body.
            comment: Optional comment prepended in the TikZ output.
        """
        super().__init__(label=name, comment=comment, layer=0)
        self._name = name
        self._args = self._normalize_args(args)
        self._body = str(body)

    @staticmethod
    def _normalize_args(args: str | Sequence[str]) -> list[str]:
        raw_args = [args] if isinstance(args, str) else list(args)
        return [arg[1:] if arg.startswith("\\") else arg for arg in raw_args]

    @property
    def name(self) -> str:
        """Declared function name."""
        return self._name

    @property
    def args(self) -> list[str]:
        """Declared argument names without leading backslashes."""
        return list(self._args)

    @property
    def body(self) -> str:
        """PGF expression used as the function body."""
        return self._body

    def __call__(self, *args: Any) -> Expr:
        """Build an expression calling this declared function.

        Raises:
            ValueError: If the number of supplied arguments does not match the
                declared function signature.
        """
        from tikzfigure.math import Expr

        if len(args) != len(self._args):
            raise ValueError(
                f"{self._name} expects {len(self._args)} argument(s), got {len(args)}."
            )
        rendered_args = [arg.pgf if isinstance(arg, Expr) else str(arg) for arg in args]
        return Expr(f"{self._name}({', '.join(rendered_args)})")

    def render_declaration(self) -> str:
        """Render the inner declaration used by PGF's ``declare function`` key."""
        args = ", ".join(f"\\{arg}" for arg in self._args)
        return f"{self._name}({args}) = {self._body};"

    def to_tikz(self, output_unit: str | None = None) -> str:
        """Generate the ``\\pgfkeys{/pgf/declare function=...}`` statement."""
        del output_unit
        declaration = self.render_declaration()
        function_str = f"\\pgfkeys{{/pgf/declare function={{{declaration}}}}}\n"
        return self.add_comment(function_str)

    def to_dict(self) -> dict[str, Any]:
        """Serialize this declared function to a plain dictionary."""
        d = super().to_dict()
        d.update(
            {
                "type": "DeclaredFunction",
                "name": self._name,
                "args": list(self._args),
                "body": self._body,
            }
        )
        serialized = serialize_tikz_value(d)
        if not isinstance(serialized, dict):
            raise TypeError("Serialized function data must remain a dict.")
        return serialized

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "DeclaredFunction":
        """Reconstruct a declared function from a dictionary."""
        restored = deserialize_tikz_value(d)
        if not isinstance(restored, dict):
            raise TypeError("Serialized function data must deserialize to a dict.")
        name = restored.get("name", restored.get("label", ""))
        if not isinstance(name, str):
            raise TypeError("Serialized function name must deserialize to a string.")
        args = restored.get("args", [])
        if isinstance(args, str):
            normalized_args: str | list[str] = args
        else:
            normalized_args = [str(arg) for arg in args]
        return cls(
            name=name,
            args=normalized_args,
            body=restored.get("body", ""),
            comment=restored.get("comment"),
        )

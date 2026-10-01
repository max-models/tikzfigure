from collections.abc import Sequence
from typing import Any

from tikzfigure.core.base import TikzObject
from tikzfigure.core.serialization import deserialize_tikz_value, serialize_tikz_value
from tikzfigure.core.tikz_library import TikzLibrary
from tikzfigure.options import OptionInput


class FitLibrary(TikzLibrary):
    """The ``fit`` library, used to wrap existing nodes/coordinates in a
    bounding node.

    Owns the ``fit=(...)(...)`` node-option formatting, so :class:`Fit`
    doesn't need to duplicate it.
    """

    name = "fit"

    @staticmethod
    def build_fit_value(targets: Sequence[str]) -> str:
        """Build the value for TikZ's ``fit=(a)(b)(c)`` node option."""
        return "".join(f"({target})" for target in targets)


class Fit(TikzObject):
    """A TikZ node that bounds a set of existing nodes/coordinates.

    Renders as a plain ``\\node`` using the ``fit`` library's ``fit=(...)...``
    option, so it picks up any node styling (``draw``, ``fill``,
    ``dashed``, ``inner sep``, ...) like a regular node. Usually created
    through :meth:`TikzFigure.add_fit` rather than instantiated directly,
    since that method resolves node/coordinate labels (with optional
    ``.anchor`` suffixes) for you.
    """

    def __init__(
        self,
        targets: list[str],
        content: str = "",
        label: str = "",
        comment: str | None = None,
        layer: int = 0,
        options: OptionInput | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize a Fit.

        Args:
            targets: TikZ node/coordinate reference strings to fit around
                (e.g. ``["a", "b.north"]``). At least one is required.
            content: Text or LaTeX content displayed inside the fit node.
                Usually left empty.
            label: Internal TikZ name for this fit node. Defaults to ``""``.
            comment: Optional comment prepended in the TikZ output.
            layer: Layer index. Defaults to ``0``.
            options: Flag-style TikZ options (e.g. ``["draw", "dashed"]``).
            **kwargs: Keyword-style TikZ options (e.g. ``inner_sep="5pt"``).
        """
        if not targets:
            raise ValueError("Fit requires at least one target node/coordinate.")

        self._targets = list(targets)
        self._content = content
        super().__init__(
            label=label,
            comment=comment,
            layer=layer,
            options=options,
            **kwargs,
        )

    @property
    def targets(self) -> list[str]:
        """TikZ node/coordinate reference strings this node fits around."""
        return list(self._targets)

    @property
    def content(self) -> str:
        """Text or LaTeX content displayed inside the fit node."""
        return self._content

    def to_tikz(self, output_unit: str | None = None) -> str:
        """Generate the TikZ ``\\node[fit=...]`` command for this fit node.

        Returns:
            A TikZ ``\\node`` command string ending with a newline,
            optionally preceded by a comment line.
        """
        fit_option = f"fit={FitLibrary.build_fit_value(self._targets)}"
        options = self.tikz_options(output_unit)
        all_options = f"{fit_option}, {options}" if options else fit_option

        label_str = f" ({self.label})" if self.label else ""
        node_string = f"\\node[{all_options}]{label_str} {{{self.content}}};\n"
        node_string = self.add_comment(node_string)
        return node_string

    def to_dict(self) -> dict[str, Any]:
        """Serialize this fit node to a plain dictionary.

        Returns:
            A dictionary with ``type``, ``targets``, ``content``, and all
            base-class keys.
        """
        d = super().to_dict()
        d.update(
            {
                "type": "Fit",
                "targets": list(self._targets),
                "content": self._content,
            }
        )
        serialized = serialize_tikz_value(d)
        if not isinstance(serialized, dict):
            raise TypeError("Serialized fit data must remain a dict.")
        return serialized

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Fit":
        """Reconstruct a Fit from a dictionary.

        Args:
            d: Dictionary as produced by :meth:`to_dict`.

        Returns:
            A new :class:`Fit` instance.
        """
        restored = deserialize_tikz_value(d)
        if not isinstance(restored, dict):
            raise TypeError("Serialized fit data must deserialize to a dict.")
        kwargs = restored.get("kwargs", {})
        if not isinstance(kwargs, dict):
            raise TypeError("Serialized fit kwargs must deserialize to a dict.")
        return cls(
            targets=list(restored.get("targets", [])),
            content=restored.get("content", ""),
            label=restored.get("label", ""),
            comment=restored.get("comment"),
            layer=restored.get("layer", 0),
            options=restored.get("options"),
            **kwargs,
        )

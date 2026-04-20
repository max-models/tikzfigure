import inspect
from typing import Any

from tikzfigure.core.serialization import deserialize_tikz_value, serialize_tikz_value
from tikzfigure.options import OptionInput, OptionValue, normalize_options


class TikzObject:
    """Base class for all TikZ elements.

    Provides shared logic for labels, comments, options, and
    conversion of Python keyword arguments to TikZ option strings.

    Attributes:
        label: Unique identifier for this object within the figure.
        comment: Optional comment prepended to the generated TikZ code.
        layer: Layer index this object belongs to.
        options: Flag-style TikZ options (e.g. ``["thick", "->"]``).
        kwargs: Keyword-style TikZ options (e.g. ``{"color": "red"}``).
    """

    def __init__(
        self,
        label: str | None = None,
        comment: str | None = None,
        layer: int | None = 0,
        options: OptionInput | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize a TikzObject.

        Args:
            label: Unique identifier for this object within the figure.
            comment: Comment prepended to the generated TikZ code.
            layer: Layer index this object belongs to. Defaults to ``0``.
            options: Flag-style TikZ options without values
                (e.g. ``["thick", "->"]``).
            **kwargs: Keyword-style TikZ options. Underscores in keys are
                converted to spaces in the output
                (e.g. ``line_width="1pt"`` → ``line width=1pt``).
        """
        self._label = label
        self._comment = comment
        self._layer = layer
        self._options = normalize_options(options)
        self._kwargs = kwargs

    @property
    def label(self) -> str | None:
        """Unique identifier for this object within the figure."""
        return self._label

    @property
    def comment(self) -> str | None:
        """Comment prepended to the generated TikZ code, or ``None``."""
        return self._comment

    @property
    def layer(self) -> int | None:
        """Layer index this object belongs to."""
        return self._layer

    @property
    def options(self) -> list[OptionValue]:
        """Flag-style TikZ options without values."""
        return self._options

    @property
    def kwargs(self) -> dict:
        """Keyword-style TikZ options as a plain dict."""
        return self._kwargs

    def tikz_options(self, output_unit: str | None = None) -> str:
        """Render all options as a single TikZ option string.

        Combines flag-style options and keyword options into the format
        expected inside TikZ square brackets, e.g.
        ``"thick, color=red, line width=1pt"``.

        Args:
            output_unit: If provided, any :class:`~tikzfigure.units.TikzDimension`
                values are converted to this unit before rendering.

        Returns:
            A comma-separated string of TikZ options.
        """
        from tikzfigure.arrows import TikzArrow
        from tikzfigure.colors import TikzColor
        from tikzfigure.styles import TikzStyle
        from tikzfigure.units import TikzDimension

        def _fmt(v: object) -> str:
            if isinstance(v, TikzDimension):
                return str(v.to(output_unit)) if output_unit is not None else str(v)
            if isinstance(v, (TikzArrow, TikzColor, TikzStyle)):
                return str(v)
            return str(v)

        parts: list[str] = []
        if self.options:
            parts.extend(str(option) for option in self.options)
        parts.extend(f"{k.replace('_', ' ')}={_fmt(v)}" for k, v in self.kwargs.items())
        return ", ".join(parts)

    def add_comment(self, string_in: str) -> str:
        """Prepend a TikZ comment line to a string if a comment is set.

        Args:
            string_in: The TikZ code string to annotate.

        Returns:
            The original string prefixed with ``% <comment>\\n`` when a
            comment is set, otherwise the string unchanged.
        """
        if self.comment is not None:
            return f"% {self.comment}\n{string_in}"
        return string_in

    def to_tikz(self, output_unit: str | None = None) -> str:
        """Render this object as TikZ.

        Concrete :class:`TikzObject` subclasses are expected to implement this.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement to_tikz()."
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize this object to a plain dictionary.

        Returns:
            A dictionary containing ``label``, ``comment``, ``layer``,
            ``options``, and ``kwargs`` keys.
        """
        return {
            "label": self._label,
            "comment": self._comment,
            "layer": self._layer,
            "options": serialize_tikz_value(self._options),
            "kwargs": serialize_tikz_value(self._kwargs),
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "TikzObject":
        """Reconstruct a TikzObject from a dictionary.

        Args:
            d: Dictionary as produced by :meth:`to_dict`.

        Returns:
            A new instance of the calling class populated from *d*.
        """
        options = deserialize_tikz_value(d.get("options"))
        kwargs = deserialize_tikz_value(d.get("kwargs", {}))
        if not isinstance(options, list):
            raise TypeError("Serialized options must deserialize to a list.")
        if not isinstance(kwargs, dict):
            raise TypeError("Serialized kwargs must deserialize to a dict.")
        return cls(
            label=d.get("label"),
            comment=d.get("comment"),
            layer=d.get("layer"),
            options=options,
            **kwargs,
        )

    @staticmethod
    def _copy_value(value: Any) -> Any:
        """Clone plain serializable data while preserving external object refs."""
        return deserialize_tikz_value(serialize_tikz_value(value))

    def _copy_init_kwargs(self) -> dict[str, Any]:
        """Build constructor kwargs representing the current object state."""
        signature = inspect.signature(type(self).__init__)
        init_kwargs: dict[str, Any] = {}
        extra_kwargs = self._copy_value(self.kwargs)
        if not isinstance(extra_kwargs, dict):
            raise TypeError("TikZ object kwargs must copy as a dictionary.")

        has_var_keyword = False
        for name, parameter in signature.parameters.items():
            if name == "self":
                continue
            if parameter.kind == inspect.Parameter.VAR_KEYWORD:
                has_var_keyword = True
                continue
            if parameter.kind == inspect.Parameter.VAR_POSITIONAL:
                continue
            if name == "options":
                init_kwargs[name] = self._copy_value(self.options)
                continue
            if name in extra_kwargs:
                init_kwargs[name] = extra_kwargs.pop(name)
                continue

            descriptor = getattr(type(self), name, None)
            if isinstance(descriptor, property):
                init_kwargs[name] = self._copy_value(getattr(self, name))
                continue

            private_name = f"_{name}"
            if hasattr(self, private_name):
                init_kwargs[name] = self._copy_value(getattr(self, private_name))

        if has_var_keyword:
            init_kwargs.update(extra_kwargs)

        return init_kwargs

    def _copy_from_init_kwargs(self, init_kwargs: dict[str, Any]) -> "TikzObject":
        """Reconstruct an object from copied constructor kwargs."""
        return type(self)(**init_kwargs)

    def copy(self, **overrides: Any) -> "TikzObject":
        """Return a copy of this object with optional constructor-style overrides."""
        init_kwargs = self._copy_init_kwargs()
        init_kwargs.update(
            {key: self._copy_value(value) for key, value in overrides.items()}
        )
        return self._copy_from_init_kwargs(init_kwargs)

    def _apply_base_copy_overrides(
        self,
        clone: "TikzObject",
        overrides: dict[str, Any],
        *,
        allow_kwargs: bool = True,
    ) -> "TikzObject":
        """Apply common TikzObject overrides to an already-cloned object."""
        remaining = {key: self._copy_value(value) for key, value in overrides.items()}

        if "label" in remaining:
            clone._label = remaining.pop("label")
        if "comment" in remaining:
            clone._comment = remaining.pop("comment")
        if "layer" in remaining:
            clone._layer = remaining.pop("layer")
        if "options" in remaining:
            clone._options = normalize_options(remaining.pop("options"))

        if remaining:
            if not allow_kwargs:
                invalid = ", ".join(sorted(remaining))
                raise TypeError(
                    f"{self.__class__.__name__}.copy() got unexpected override(s): {invalid}"
                )
            clone._kwargs.update(remaining)

        return clone

    def _restore_from_check_dict(self, d: dict[str, Any]) -> "TikzObject":
        """Reconstruct this object from serialized data for `_check()`."""
        return type(self).from_dict(d)

    def _check(self, output_unit: str | None = None) -> "TikzObject":
        """Round-trip through dict/TikZ serialization and verify equivalence."""
        data = self.to_dict()
        restored = self._restore_from_check_dict(data)
        if restored != self:
            raise AssertionError(
                f"{self.__class__.__name__} changed after to_dict()/from_dict() round-trip."
            )

        original_tikz = self.to_tikz(output_unit)
        restored_tikz = restored.to_tikz(output_unit)
        if original_tikz != restored_tikz:
            raise AssertionError(
                f"{self.__class__.__name__} changed after to_tikz() round-trip."
            )

        return restored

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TikzObject):
            return NotImplemented
        return self.to_dict() == other.to_dict()

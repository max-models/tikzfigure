import base64
import hashlib
from pathlib import Path
from typing import Any

from tikzfigure.core.base import TikzObject
from tikzfigure.core.serialization import deserialize_tikz_value, serialize_tikz_value
from tikzfigure.options import OptionInput


class AxisGraphics(TikzObject):
    """An image placed in data coordinates inside a pgfplots axis.

    Renders as ``\\addplot graphics[xmin=..., xmax=..., ymin=..., ymax=...]
    {file};``. The image is either an existing file (``path``) or bytes the
    figure writes next to the TikZ code when it compiles or saves it
    (``data``), e.g. a raster of a colormap mesh that would be too large as
    pgfplots coordinates.
    """

    def __init__(
        self,
        xmin: float,
        xmax: float,
        ymin: float,
        ymax: float,
        path: str | Path | None = None,
        data: bytes | None = None,
        filename: str | None = None,
        comment: str | None = None,
        options: OptionInput | None = None,
        plot_options: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize an image in an axis.

        Args:
            xmin, xmax, ymin, ymax: Data coordinates of the image edges.
            path: An existing image file, referenced as given. Mutually
                exclusive with ``data``.
            data: The image file's bytes (e.g. PNG). The figure writes them
                as ``filename`` next to the TikZ code it compiles or saves.
            filename: The file name for ``data``. Defaults to one derived
                from the bytes, so equal images share a file.
            comment: Optional comment prepended in the TikZ output.
            options: Flag-style ``\\addplot graphics`` options.
            plot_options: Options of the ``\\addplot`` itself, e.g.
                ``["forget plot"]`` to leave the image out of the legend.
            **kwargs: Keyword-style ``\\addplot graphics`` options.
        """
        if (path is None) == (data is None):
            raise ValueError("give either path or data for an axis image")
        super().__init__(comment=comment, layer=0, options=options or [], **kwargs)
        self._xmin, self._xmax = float(xmin), float(xmax)
        self._ymin, self._ymax = float(ymin), float(ymax)
        self._path = None if path is None else str(path)
        self._data = data
        if data is not None and filename is None:
            filename = f"tikzfigure-{hashlib.sha1(data).hexdigest()[:12]}.png"
        self._filename = filename
        self._plot_options = [str(option) for option in plot_options or []]

    @property
    def xmin(self) -> float:
        return self._xmin

    @property
    def xmax(self) -> float:
        return self._xmax

    @property
    def ymin(self) -> float:
        return self._ymin

    @property
    def ymax(self) -> float:
        return self._ymax

    @property
    def path(self) -> str | None:
        """The referenced image file, or None for an image given as data."""
        return self._path

    @property
    def data(self) -> bytes | None:
        """The image bytes, or None for an image given as a path."""
        return self._data

    @property
    def filename(self) -> str | None:
        """The file name the image data is written as."""
        return self._filename

    @property
    def plot_options(self) -> list[str]:
        """Options of the ``\\addplot`` command itself."""
        return self._plot_options

    @property
    def source(self) -> str:
        """The file name the TikZ code refers to."""
        return self._path if self._path is not None else str(self._filename)

    def files(self) -> dict[str, bytes]:
        """The files this image needs written next to the TikZ code."""
        if self._data is None:
            return {}
        return {str(self._filename): self._data}

    def to_tikz(self, output_unit: str | None = None) -> str:
        options = [
            f"xmin={self._xmin!r}",
            f"xmax={self._xmax!r}",
            f"ymin={self._ymin!r}",
            f"ymax={self._ymax!r}",
        ]
        extra = self.tikz_options(output_unit)
        if extra:
            options.append(extra)
        plot = f"[{', '.join(self._plot_options)}]" if self._plot_options else ""
        code = f"\\addplot{plot} graphics[{', '.join(options)}] {{{self.source}}};\n"
        return self.add_comment(code)

    def to_dict(self) -> dict[str, Any]:
        serialized = serialize_tikz_value(
            {
                "type": "AxisGraphics",
                "xmin": self._xmin,
                "xmax": self._xmax,
                "ymin": self._ymin,
                "ymax": self._ymax,
                "path": self._path,
                "data": (
                    None
                    if self._data is None
                    else base64.b64encode(self._data).decode("ascii")
                ),
                "filename": self._filename,
                "plot_options": self._plot_options,
                "comment": self.comment,
                "options": self.options,
                "kwargs": self.kwargs,
            }
        )
        if not isinstance(serialized, dict):
            raise TypeError("Serialized AxisGraphics data must remain a dict.")
        return serialized

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "AxisGraphics":
        restored = deserialize_tikz_value(d)
        if not isinstance(restored, dict):
            raise TypeError("Serialized AxisGraphics data must deserialize to a dict.")
        data = restored.get("data")
        return cls(
            xmin=restored["xmin"],
            xmax=restored["xmax"],
            ymin=restored["ymin"],
            ymax=restored["ymax"],
            path=restored.get("path"),
            data=None if data is None else base64.b64decode(data),
            filename=restored.get("filename"),
            comment=restored.get("comment"),
            options=restored.get("options"),
            plot_options=restored.get("plot_options"),
            **restored.get("kwargs", {}),
        )

    def copy(self, **overrides: Any) -> "AxisGraphics":
        init: dict[str, Any] = dict(
            xmin=self._xmin,
            xmax=self._xmax,
            ymin=self._ymin,
            ymax=self._ymax,
            path=self._path,
            data=self._data,
            filename=self._filename,
            comment=self.comment,
            options=list(self.options),
            plot_options=list(self._plot_options),
            **self.kwargs,
        )
        init.update(overrides)
        return type(self)(**init)

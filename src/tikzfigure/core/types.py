from typing import Literal

from tikzfigure.options import OptionValue
from tikzfigure.styles import TikzStyle

# ---------- Literal type aliases for IDE autocomplete ---------- #

_Shape = (
    Literal[
        "circle",
        "rectangle",
        "diamond",
        "ellipse",
        "star",
        "regular polygon",
        "trapezium",
        "semicircle",
        "cylinder",
        "dart",
        "kite",
        "isosceles triangle",
        "signal",
        "cloud",
        "forbidden sign",
        "cross out",
        "strike out",
    ]
    | str
    | None
)

_Anchor = (
    Literal[
        "center",
        "north",
        "south",
        "east",
        "west",
        "north east",
        "north west",
        "south east",
        "south west",
        "base",
        "mid",
        "base east",
        "base west",
        "mid east",
        "mid west",
    ]
    | str
    | None
)

_Option = OptionValue
_LineCap = Literal["butt", "rect", "round"] | TikzStyle | str | None
_LineJoin = Literal["miter", "bevel", "round"] | TikzStyle | str | None
_Align = Literal["left", "center", "right", "justify"] | str | None
_Shading = Literal["axis", "radial", "ball"] | str | None

_Pattern = (
    Literal[
        "horizontal lines",
        "vertical lines",
        "north east lines",
        "north west lines",
        "grid",
        "crosshatch",
        "dots",
        "crosshatch dots",
        "fivepointed stars",
        "sixpointed stars",
        "bricks",
        "checkerboard",
    ]
    | str
    | None
)

_Mark = (
    Literal[
        "*",
        "x",
        "o",
        "+",
        "|",
        "-",
        "square",
        "square*",
        "triangle",
        "triangle*",
        "diamond",
        "diamond*",
        "pentagon",
        "pentagon*",
        "oplus",
        "oplus*",
        "otimes",
        "otimes*",
        "asterisk",
        "star",
        "10-pointed star",
        "ball",
    ]
    | str
    | None
)

_Decoration = (
    Literal[
        "zigzag",
        "snake",
        "coil",
        "bumps",
        "bent",
        "random steps",
        "saw",
        "brace",
        "ticks",
        "border",
        "markings",
        "expanding waves",
        "footprints",
    ]
    | str
    | None
)

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = REPO_ROOT / "src" / "tikzfigure" / "colors.py"

_BASIC_COLOR_NAMES = """
black blue brown cyan darkgray gray green lightgray lime magenta olive orange pink
purple red teal violet white yellow
""".split()

_DVIPS_COLOR_NAMES = """
Apricot Aquamarine Bittersweet Black Blue BlueGreen BlueViolet BrickRed Brown
BurntOrange CadetBlue CarnationPink Cerulean CornflowerBlue Cyan Dandelion
DarkOrchid Emerald ForestGreen Fuchsia Goldenrod Gray Green GreenYellow JungleGreen
Lavender LimeGreen Magenta Mahogany Maroon Melon MidnightBlue Mulberry NavyBlue
OliveGreen Orange OrangeRed Orchid Peach Periwinkle PineGreen Plum ProcessBlue
Purple RawSienna Red RedOrange RedViolet Rhodamine RoyalBlue RoyalPurple
RubineRed Salmon SeaGreen Sepia SkyBlue SpringGreen Tan TealBlue Thistle
Turquoise Violet VioletRed White WildStrawberry Yellow YellowGreen YellowOrange
""".split()

_SVG_COLOR_NAMES = """
AliceBlue AntiqueWhite Aqua Aquamarine Azure Beige Bisque Black BlanchedAlmond Blue
BlueViolet Brown BurlyWood CadetBlue Chartreuse Chocolate Coral CornflowerBlue
Cornsilk Crimson Cyan DarkBlue DarkCyan DarkGoldenrod DarkGray DarkGreen DarkGrey
DarkKhaki DarkMagenta DarkOliveGreen DarkOrange DarkOrchid DarkRed DarkSalmon
DarkSeaGreen DarkSlateBlue DarkSlateGray DarkSlateGrey DarkTurquoise DarkViolet
DeepPink DeepSkyBlue DimGray DimGrey DodgerBlue FireBrick FloralWhite ForestGreen
Fuchsia Gainsboro GhostWhite Gold Goldenrod Gray Green GreenYellow Grey Honeydew
HotPink IndianRed Indigo Ivory Khaki Lavender LavenderBlush LawnGreen LemonChiffon
LightBlue LightCoral LightCyan LightGoldenrod LightGoldenrodYellow LightGray
LightGreen LightGrey LightPink LightSalmon LightSeaGreen LightSkyBlue
LightSlateBlue LightSlateGray LightSlateGrey LightSteelBlue LightYellow Lime
LimeGreen Linen Magenta Maroon MediumAquamarine MediumBlue MediumOrchid
MediumPurple MediumSeaGreen MediumSlateBlue MediumSpringGreen MediumTurquoise
MediumVioletRed MidnightBlue MintCream MistyRose Moccasin NavajoWhite Navy
NavyBlue OldLace Olive OliveDrab Orange OrangeRed Orchid PaleGoldenrod PaleGreen
PaleTurquoise PaleVioletRed PapayaWhip PeachPuff Peru Pink Plum PowderBlue Purple
Red RosyBrown RoyalBlue SaddleBrown Salmon SandyBrown SeaGreen Seashell Sienna
Silver SkyBlue SlateBlue SlateGray SlateGrey Snow SpringGreen SteelBlue Tan Teal
Thistle Tomato Turquoise Violet VioletRed Wheat White WhiteSmoke Yellow YellowGreen
""".split()

_X11_COLOR_NAMES = """
AntiqueWhite1 AntiqueWhite2 AntiqueWhite3 AntiqueWhite4 Aquamarine1 Aquamarine2
Aquamarine3 Aquamarine4 Azure1 Azure2 Azure3 Azure4 Bisque1 Bisque2 Bisque3
Bisque4 Blue1 Blue2 Blue3 Blue4 Brown1 Brown2 Brown3 Brown4 Burlywood1 Burlywood2
Burlywood3 Burlywood4 CadetBlue1 CadetBlue2 CadetBlue3 CadetBlue4 Chartreuse1
Chartreuse2 Chartreuse3 Chartreuse4 Chocolate1 Chocolate2 Chocolate3 Chocolate4
Coral1 Coral2 Coral3 Coral4 Cornsilk1 Cornsilk2 Cornsilk3 Cornsilk4 Cyan1 Cyan2
Cyan3 Cyan4 DarkGoldenrod1 DarkGoldenrod2 DarkGoldenrod3 DarkGoldenrod4
DarkOliveGreen1 DarkOliveGreen2 DarkOliveGreen3 DarkOliveGreen4 DarkOrange1
DarkOrange2 DarkOrange3 DarkOrange4 DarkOrchid1 DarkOrchid2 DarkOrchid3
DarkOrchid4 DarkSeaGreen1 DarkSeaGreen2 DarkSeaGreen3 DarkSeaGreen4
DarkSlateGray1 DarkSlateGray2 DarkSlateGray3 DarkSlateGray4 DeepPink1 DeepPink2
DeepPink3 DeepPink4 DeepSkyBlue1 DeepSkyBlue2 DeepSkyBlue3 DeepSkyBlue4
DodgerBlue1 DodgerBlue2 DodgerBlue3 DodgerBlue4 Firebrick1 Firebrick2 Firebrick3
Firebrick4 Gold1 Gold2 Gold3 Gold4 Goldenrod1 Goldenrod2 Goldenrod3 Goldenrod4
Green1 Green2 Green3 Green4 Honeydew1 Honeydew2 Honeydew3 Honeydew4 HotPink1
HotPink2 HotPink3 HotPink4 IndianRed1 IndianRed2 IndianRed3 IndianRed4 Ivory1
Ivory2 Ivory3 Ivory4 Khaki1 Khaki2 Khaki3 Khaki4 LavenderBlush1 LavenderBlush2
LavenderBlush3 LavenderBlush4 LemonChiffon1 LemonChiffon2 LemonChiffon3
LemonChiffon4 LightBlue1 LightBlue2 LightBlue3 LightBlue4 LightCyan1 LightCyan2
LightCyan3 LightCyan4 LightGoldenrod1 LightGoldenrod2 LightGoldenrod3
LightGoldenrod4 LightPink1 LightPink2 LightPink3 LightPink4 LightSalmon1
LightSalmon2 LightSalmon3 LightSalmon4 LightSkyBlue1 LightSkyBlue2 LightSkyBlue3
LightSkyBlue4 LightSteelBlue1 LightSteelBlue2 LightSteelBlue3 LightSteelBlue4
LightYellow1 LightYellow2 LightYellow3 LightYellow4 Magenta1 Magenta2 Magenta3
Magenta4 Maroon1 Maroon2 Maroon3 Maroon4 MediumOrchid1 MediumOrchid2
MediumOrchid3 MediumOrchid4 MediumPurple1 MediumPurple2 MediumPurple3
MediumPurple4 MistyRose1 MistyRose2 MistyRose3 MistyRose4 NavajoWhite1
NavajoWhite2 NavajoWhite3 NavajoWhite4 OliveDrab1 OliveDrab2 OliveDrab3
OliveDrab4 Orange1 Orange2 Orange3 Orange4 OrangeRed1 OrangeRed2 OrangeRed3
OrangeRed4 Orchid1 Orchid2 Orchid3 Orchid4 PaleGreen1 PaleGreen2 PaleGreen3
PaleGreen4 PaleTurquoise1 PaleTurquoise2 PaleTurquoise3 PaleTurquoise4
PaleVioletRed1 PaleVioletRed2 PaleVioletRed3 PaleVioletRed4 PeachPuff1
PeachPuff2 PeachPuff3 PeachPuff4 Pink1 Pink2 Pink3 Pink4 Plum1 Plum2 Plum3
Plum4 Purple1 Purple2 Purple3 Purple4 Red1 Red2 Red3 Red4 RosyBrown1 RosyBrown2
RosyBrown3 RosyBrown4 RoyalBlue1 RoyalBlue2 RoyalBlue3 RoyalBlue4 Salmon1
Salmon2 Salmon3 Salmon4 SeaGreen1 SeaGreen2 SeaGreen3 SeaGreen4 Seashell1
Seashell2 Seashell3 Seashell4 Sienna1 Sienna2 Sienna3 Sienna4 SkyBlue1 SkyBlue2
SkyBlue3 SkyBlue4 SlateBlue1 SlateBlue2 SlateBlue3 SlateBlue4 SlateGray1
SlateGray2 SlateGray3 SlateGray4 Snow1 Snow2 Snow3 Snow4 SpringGreen1
SpringGreen2 SpringGreen3 SpringGreen4 SteelBlue1 SteelBlue2 SteelBlue3
SteelBlue4 Tan1 Tan2 Tan3 Tan4 Thistle1 Thistle2 Thistle3 Thistle4 Tomato1
Tomato2 Tomato3 Tomato4 Turquoise1 Turquoise2 Turquoise3 Turquoise4 VioletRed1
VioletRed2 VioletRed3 VioletRed4 Wheat1 Wheat2 Wheat3 Wheat4 Yellow1 Yellow2
Yellow3 Yellow4 Gray0 Green0 Grey0 Maroon0 Purple0
""".split()


def _to_snake_case(name: str) -> str:
    snake = re.sub(r"(?<!^)(?=[A-Z])", "_", name)
    return snake.lower()


def _iter_entries() -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    seen: set[str] = set()

    for name in _BASIC_COLOR_NAMES:
        if name not in seen:
            entries.append((name, name))
            seen.add(name)

    for spec in _DVIPS_COLOR_NAMES + _SVG_COLOR_NAMES + _X11_COLOR_NAMES:
        for name in (spec, _to_snake_case(spec)):
            if name not in seen:
                entries.append((name, spec))
                seen.add(name)

    return entries


def _render() -> str:
    entries = _iter_entries()
    exported_names = ["TikzColor", "ColorInput", *(name for name, _ in entries)]

    lines = [
        '"""Generated by scripts/generate_colors.py. Do not edit by hand."""',
        "",
        "from __future__ import annotations",
        "",
        "from typing import TypeAlias",
        "",
        "",
        "class TikzColor:",
        '    """An xcolor-compatible TikZ color expression."""',
        "",
        "    def __init__(self, color_spec: str) -> None:",
        '        if color_spec == "":',
        '            raise ValueError("color_spec must not be empty")',
        "        self.color_spec = color_spec",
        "",
        "    @staticmethod",
        "    def _normalize_percent(percent: float | int) -> str:",
        "        if not isinstance(percent, (int, float)):",
        '            raise TypeError("percent must be an int or float")',
        "        numeric = float(percent)",
        "        if numeric < 0:",
        '            raise ValueError("percent must be non-negative")',
        "        if isinstance(percent, int):",
        "            value = numeric",
        "        elif numeric <= 1:",
        "            value = numeric * 100",
        "        else:",
        "            value = numeric",
        "        if value > 100:",
        '            raise ValueError("percent must be between 0 and 1, or between 0 and 100")',
        "        if value.is_integer():",
        "            return str(int(value))",
        "        return str(value)",
        "",
        "    @staticmethod",
        '    def _coerce(other: str | "TikzColor") -> str:',
        "        if isinstance(other, TikzColor):",
        "            return other.color_spec",
        "        return other",
        "",
        "    def mix(",
        '        self, other: str | "TikzColor" | None = None, percent: float | int = 0.5',
        '    ) -> "TikzColor":',
        '        """Build an xcolor mix like ``red!50`` or ``red!50!blue``."""',
        "        pct = self._normalize_percent(percent)",
        "        if other is None:",
        '            return TikzColor(f"{self.color_spec}!{pct}")',
        '        return TikzColor(f"{self.color_spec}!{pct}!{self._coerce(other)}")',
        "",
        '    def complement(self) -> "TikzColor":',
        '        """Return the xcolor complementary-expression form."""',
        '        return TikzColor(f"-{self.color_spec}")',
        "",
        "    def to_tikz(self) -> str:",
        '        """Return the raw xcolor expression."""',
        "        return self.color_spec",
        "",
        '    def __neg__(self) -> "TikzColor":',
        "        return self.complement()",
        "",
        "    def __str__(self) -> str:",
        "        return self.color_spec",
        "",
        "    def __repr__(self) -> str:",
        '        return f"TikzColor({self.color_spec!r})"',
        "",
        "    def __hash__(self) -> int:",
        "        return hash(self.color_spec)",
        "",
        "",
        "ColorInput: TypeAlias = str | TikzColor",
        "",
    ]

    for name, spec in entries:
        lines.append(f'{name}: TikzColor = TikzColor("{spec}")')

    lines.extend(
        [
            "",
            "__all__ = [",
            *[f'    "{name}",' for name in exported_names],
            "]",
            "",
        ]
    )

    return "\n".join(lines)


def main() -> None:
    OUTPUT_PATH.write_text(_render(), encoding="utf-8")


if __name__ == "__main__":
    main()

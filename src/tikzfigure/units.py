from __future__ import annotations

# Conversion factors: 1 <unit> = N pt
_TO_PT: dict[str, float] = {
    "pt": 1.0,
    "bp": 1.00375,
    "mm": 2.84527,
    "cm": 28.4527,
    "in": 72.27,
    "pc": 12.0,
    "dd": 1.07001,
    "cc": 12.84012,
    "sp": 1 / 65536,
    "ex": 6.565,  # font-dependent; typical value
    "em": 10.0,  # font-dependent; typical value
}


class TikzDimension:
    """A TikZ dimension value with a unit, e.g. 2.5cm or 10pt."""

    def __init__(self, value: float | int, unit: str) -> None:
        self.value = value
        self.unit = unit

    def to(self, target_unit: str) -> "TikzDimension":
        """Convert to another TikZ unit."""
        if self.unit == target_unit:
            return TikzDimension(self.value, self.unit)
        if self.unit not in _TO_PT:
            raise ValueError(f"Unknown source unit: {self.unit!r}")
        if target_unit not in _TO_PT:
            raise ValueError(f"Unknown target unit: {target_unit!r}")
        pt_value = float(self.value) * _TO_PT[self.unit]
        converted = pt_value / _TO_PT[target_unit]
        return TikzDimension(converted, target_unit)

    def __str__(self) -> str:
        v = self.value
        if isinstance(v, float) and v == int(v):
            return f"{int(v)}{self.unit}"
        return f"{v}{self.unit}"

    def __float__(self) -> float:
        return float(self.value)

    def __repr__(self) -> str:
        return f"TikzDimension({self.value!r}, {self.unit!r})"


class _Unit:
    """Sentinel for a TikZ unit. Supports multiplication: 2.5 * units.cm."""

    def __init__(self, unit: str) -> None:
        self._unit = unit

    def __rmul__(self, value: float | int) -> TikzDimension:
        return TikzDimension(value, self._unit)

    def __mul__(self, value: float | int) -> TikzDimension:
        return TikzDimension(value, self._unit)


cm = _Unit("cm")
mm = _Unit("mm")
pt = _Unit("pt")
bp = _Unit("bp")
in_ = _Unit("in")
ex = _Unit("ex")
em = _Unit("em")
pc = _Unit("pc")
dd = _Unit("dd")
cc = _Unit("cc")
sp = _Unit("sp")

"""PGF math expression building for TikZ figures.

This module provides a Python API for constructing PGF mathematical expressions
that can be used as node coordinates, variable values, and anywhere a numeric
or expression string is accepted.

Example:
    >>> from tikzfigure.math import sin, cos, sqrt, Var, pi
    >>> sin(60)              # Expr: "sin(60)"
    >>> cos(60) + sin(60)    # Expr: "(cos(60) + sin(60))"
    >>> sqrt(2)              # Expr: "sqrt(2)"
    >>> Var("radius") * 2    # Expr: "(\\radius * 2)"

Warning:
    Importing ``abs``, ``min``, ``max``, ``round`` from this module shadows
    Python's built-in functions. Use targeted imports to avoid confusion:
    ``from tikzfigure.math import sin, cos`` (not ``from tikzfigure.math import *``).
"""

from typing import Any


class Expr:
    """A PGF math expression that can be embedded in TikZ code.

    Instances are immutable and can be combined using Python operators
    (+, -, *, /, **) to form complex expressions. They emit valid PGF
    syntax when converted to string via f-string interpolation.

    Attributes:
        pgf: The PGF math expression string (e.g., "sin(60)", "\\radius").
    """

    def __init__(self, pgf: str) -> None:
        """Initialize an expression.

        Args:
            pgf: The PGF math expression string. Should be a valid PGF
                expression; no validation is performed.
        """
        self.pgf = pgf

    # Binary operators: left operand is Expr

    def __add__(self, other: Any) -> "Expr":
        """Add: expr + other → (expr + other)."""
        if isinstance(other, Expr):
            return Expr(f"({self.pgf} + {other.pgf})")
        return Expr(f"({self.pgf} + {other})")

    # Reflected operators: other operand is left, Expr is right

    def __radd__(self, other: Any) -> "Expr":
        """Reflected add: other + expr → (other + expr)."""
        return Expr(f"({other} + {self.pgf})")

    def __sub__(self, other: Any) -> "Expr":
        """Subtract: expr - other → (expr - other)."""
        if isinstance(other, Expr):
            return Expr(f"({self.pgf} - {other.pgf})")
        return Expr(f"({self.pgf} - {other})")

    def __rsub__(self, other: Any) -> "Expr":
        """Reflected subtract: other - expr → (other - expr)."""
        return Expr(f"({other} - {self.pgf})")

    def __mul__(self, other: Any) -> "Expr":
        """Multiply: expr * other → (expr * other)."""
        if isinstance(other, Expr):
            return Expr(f"({self.pgf} * {other.pgf})")
        return Expr(f"({self.pgf} * {other})")

    def __rmul__(self, other: Any) -> "Expr":
        """Reflected multiply: other * expr → (other * expr)."""
        return Expr(f"({other} * {self.pgf})")

    def __truediv__(self, other: Any) -> "Expr":
        """Divide: expr / other → (expr / other)."""
        if isinstance(other, Expr):
            return Expr(f"({self.pgf} / {other.pgf})")
        return Expr(f"({self.pgf} / {other})")

    def __rtruediv__(self, other: Any) -> "Expr":
        """Reflected divide: other / expr → (other / expr)."""
        return Expr(f"({other} / {self.pgf})")

    def __pow__(self, other: Any) -> "Expr":
        """Power: expr ** other → (expr ^ other) [PGF uses ^]."""
        if isinstance(other, Expr):
            return Expr(f"({self.pgf}^{other.pgf})")
        return Expr(f"({self.pgf}^{other})")

    def __rpow__(self, other: Any) -> "Expr":
        """Reflected power: other ** expr → (other ^ expr)."""
        return Expr(f"({other}^{self.pgf})")

    # Unary operators

    def __neg__(self) -> "Expr":
        """Negate the expression: -expr → (-expr)."""
        return Expr(f"(-{self.pgf})")

    def __pos__(self) -> "Expr":
        """Unary plus: +expr → (+expr)."""
        return Expr(f"(+{self.pgf})")

    def __eq__(self, other: object) -> bool:
        """Check equality based on the PGF expression string."""
        if not isinstance(other, Expr):
            return NotImplemented
        return self.pgf == other.pgf

    def __hash__(self) -> int:
        """Hash based on the PGF expression string."""
        return hash(self.pgf)

    def __repr__(self) -> str:
        """Return a developer-friendly representation."""
        return f"Expr({self.pgf!r})"

    def __str__(self) -> str:
        """Return the PGF expression string for f-string interpolation."""
        return self.pgf


def Var(name: str) -> Expr:
    """Reference a PGF variable by name.

    Args:
        name: The variable name (without the leading backslash).

    Returns:
        An expression referencing ``\\name``.

    Example:
        >>> Var("radius")           # Expr: "\\radius"
        >>> Var("x") ** 2 + Var("y") ** 2  # Expr: "(\\x^2 + \\y^2)"
    """
    return Expr(f"\\{name}")


# --- Trigonometric functions ---


def sin(x: Any) -> Expr:
    """Sine: sin(x)."""
    x_str = x.pgf if isinstance(x, Expr) else x
    return Expr(f"sin({x_str})")


def cos(x: Any) -> Expr:
    """Cosine: cos(x)."""
    x_str = x.pgf if isinstance(x, Expr) else x
    return Expr(f"cos({x_str})")


def tan(x: Any) -> Expr:
    """Tangent: tan(x)."""
    x_str = x.pgf if isinstance(x, Expr) else x
    return Expr(f"tan({x_str})")


def asin(x: Any) -> Expr:
    """Arcsine: asin(x)."""
    x_str = x.pgf if isinstance(x, Expr) else x
    return Expr(f"asin({x_str})")


def acos(x: Any) -> Expr:
    """Arccosine: acos(x)."""
    x_str = x.pgf if isinstance(x, Expr) else x
    return Expr(f"acos({x_str})")


def atan(x: Any) -> Expr:
    """Arctangent: atan(x)."""
    x_str = x.pgf if isinstance(x, Expr) else x
    return Expr(f"atan({x_str})")


def atan2(y: Any, x: Any) -> Expr:
    """Two-argument arctangent: atan2(y, x)."""
    y_str = y.pgf if isinstance(y, Expr) else y
    x_str = x.pgf if isinstance(x, Expr) else x
    return Expr(f"atan2({y_str}, {x_str})")


def sec(x: Any) -> Expr:
    """Secant: sec(x)."""
    x_str = x.pgf if isinstance(x, Expr) else x
    return Expr(f"sec({x_str})")


def cosec(x: Any) -> Expr:
    """Cosecant: cosec(x)."""
    x_str = x.pgf if isinstance(x, Expr) else x
    return Expr(f"cosec({x_str})")


def cot(x: Any) -> Expr:
    """Cotangent: cot(x)."""
    x_str = x.pgf if isinstance(x, Expr) else x
    return Expr(f"cot({x_str})")


def sinh(x: Any) -> Expr:
    """Hyperbolic sine: sinh(x)."""
    x_str = x.pgf if isinstance(x, Expr) else x
    return Expr(f"sinh({x_str})")


def cosh(x: Any) -> Expr:
    """Hyperbolic cosine: cosh(x)."""
    x_str = x.pgf if isinstance(x, Expr) else x
    return Expr(f"cosh({x_str})")


def tanh(x: Any) -> Expr:
    """Hyperbolic tangent: tanh(x)."""
    x_str = x.pgf if isinstance(x, Expr) else x
    return Expr(f"tanh({x_str})")


def exp(x: Any) -> Expr:
    """Exponential: exp(x)."""
    x_str = x.pgf if isinstance(x, Expr) else x
    return Expr(f"exp({x_str})")


# --- Angle conversion ---


def deg(x: Any) -> Expr:
    """Convert radians to degrees: deg(x)."""
    x_str = x.pgf if isinstance(x, Expr) else x
    return Expr(f"deg({x_str})")


def rad(x: Any) -> Expr:
    """Convert degrees to radians: rad(x)."""
    x_str = x.pgf if isinstance(x, Expr) else x
    return Expr(f"rad({x_str})")


# --- Rounding and absolute value ---


def abs(x: Any) -> Expr:
    """Absolute value: abs(x).

    Warning:
        Shadows Python's built-in ``abs``.
    """
    x_str = x.pgf if isinstance(x, Expr) else x
    return Expr(f"abs({x_str})")


def ceil(x: Any) -> Expr:
    """Ceiling (round up): ceil(x)."""
    x_str = x.pgf if isinstance(x, Expr) else x
    return Expr(f"ceil({x_str})")


def floor(x: Any) -> Expr:
    """Floor (round down): floor(x)."""
    x_str = x.pgf if isinstance(x, Expr) else x
    return Expr(f"floor({x_str})")


def round(x: Any) -> Expr:
    """Round to nearest integer: round(x).

    Warning:
        Shadows Python's built-in ``round``.
    """
    x_str = x.pgf if isinstance(x, Expr) else x
    return Expr(f"round({x_str})")


# --- Power and square root ---


def sqrt(x: Any) -> Expr:
    """Square root: sqrt(x)."""
    x_str = x.pgf if isinstance(x, Expr) else x
    return Expr(f"sqrt({x_str})")


def pow(base: Any, exponent: Any) -> Expr:
    """Power: pow(base, exponent) → (base ^ exponent)."""
    base_str = base.pgf if isinstance(base, Expr) else base
    exp_str = exponent.pgf if isinstance(exponent, Expr) else exponent
    return Expr(f"pow({base_str}, {exp_str})")


# --- Logarithms ---


def ln(x: Any) -> Expr:
    """Natural logarithm: ln(x)."""
    x_str = x.pgf if isinstance(x, Expr) else x
    return Expr(f"ln({x_str})")


def func(name: str, *args: Any) -> Expr:
    """Call an arbitrary PGF math function by name."""
    rendered_args = [arg.pgf if isinstance(arg, Expr) else str(arg) for arg in args]
    return Expr(f"{name}({', '.join(rendered_args)})")


def log2(x: Any) -> Expr:
    """Base-2 logarithm: log2(x)."""
    x_str = x.pgf if isinstance(x, Expr) else x
    return Expr(f"log2({x_str})")


def log10(x: Any) -> Expr:
    """Base-10 logarithm: log10(x)."""
    x_str = x.pgf if isinstance(x, Expr) else x
    return Expr(f"log10({x_str})")


# --- Min/max ---


def min(x: Any, y: Any) -> Expr:
    """Minimum of two values: min(x, y).

    Warning:
        Shadows Python's built-in ``min``.
    """
    x_str = x.pgf if isinstance(x, Expr) else x
    y_str = y.pgf if isinstance(y, Expr) else y
    return Expr(f"min({x_str}, {y_str})")


def max(x: Any, y: Any) -> Expr:
    """Maximum of two values: max(x, y).

    Warning:
        Shadows Python's built-in ``max``.
    """
    x_str = x.pgf if isinstance(x, Expr) else x
    y_str = y.pgf if isinstance(y, Expr) else y
    return Expr(f"max({x_str}, {y_str})")


# --- Arithmetic functions ---


def neg(x: Any) -> Expr:
    """Negate: neg(x) → -x."""
    x_str = x.pgf if isinstance(x, Expr) else x
    return Expr(f"neg({x_str})")


def mod(x: Any, y: Any) -> Expr:
    """Modulo: mod(x, y)."""
    x_str = x.pgf if isinstance(x, Expr) else x
    y_str = y.pgf if isinstance(y, Expr) else y
    return Expr(f"mod({x_str}, {y_str})")


def Mod(x: Any, y: Any) -> Expr:
    """Capital-M modulo: Mod(x, y)."""
    x_str = x.pgf if isinstance(x, Expr) else x
    y_str = y.pgf if isinstance(y, Expr) else y
    return Expr(f"Mod({x_str}, {y_str})")


def div(x: Any, y: Any) -> Expr:
    """Integer division: div(x, y)."""
    x_str = x.pgf if isinstance(x, Expr) else x
    y_str = y.pgf if isinstance(y, Expr) else y
    return Expr(f"div({x_str}, {y_str})")


def frac(x: Any, y: Any) -> Expr:
    """Fractional part: frac(x, y)."""
    x_str = x.pgf if isinstance(x, Expr) else x
    y_str = y.pgf if isinstance(y, Expr) else y
    return Expr(f"frac({x_str}, {y_str})")


def gcd(x: Any, y: Any) -> Expr:
    """Greatest common divisor: gcd(x, y)."""
    x_str = x.pgf if isinstance(x, Expr) else x
    y_str = y.pgf if isinstance(y, Expr) else y
    return Expr(f"gcd({x_str}, {y_str})")


def factorial(n: Any) -> Expr:
    """Factorial: factorial(n)."""
    n_str = n.pgf if isinstance(n, Expr) else n
    return Expr(f"factorial({n_str})")


# --- Type conversion ---


def int_(x: Any) -> Expr:
    """Convert to integer: int(x).

    Name is ``int_`` to avoid shadowing Python's built-in ``int``.
    """
    x_str = x.pgf if isinstance(x, Expr) else x
    return Expr(f"int({x_str})")


def real(x: Any) -> Expr:
    """Convert to real number: real(x)."""
    x_str = x.pgf if isinstance(x, Expr) else x
    return Expr(f"real({x_str})")


def scalar(x: Any) -> Expr:
    """Extract scalar from vector: scalar(x)."""
    x_str = x.pgf if isinstance(x, Expr) else x
    return Expr(f"scalar({x_str})")


# --- Vector operations ---


def veclen(x: Any, y: Any) -> Expr:
    """Vector length: veclen(x, y) → sqrt(x² + y²)."""
    x_str = x.pgf if isinstance(x, Expr) else x
    y_str = y.pgf if isinstance(y, Expr) else y
    return Expr(f"veclen({x_str}, {y_str})")


# --- Comparison functions ---


def equal(x: Any, y: Any) -> Expr:
    """Equality: equal(x, y)."""
    x_str = x.pgf if isinstance(x, Expr) else x
    y_str = y.pgf if isinstance(y, Expr) else y
    return Expr(f"equal({x_str}, {y_str})")


def greater(x: Any, y: Any) -> Expr:
    """Greater than: greater(x, y)."""
    x_str = x.pgf if isinstance(x, Expr) else x
    y_str = y.pgf if isinstance(y, Expr) else y
    return Expr(f"greater({x_str}, {y_str})")


def less(x: Any, y: Any) -> Expr:
    """Less than: less(x, y)."""
    x_str = x.pgf if isinstance(x, Expr) else x
    y_str = y.pgf if isinstance(y, Expr) else y
    return Expr(f"less({x_str}, {y_str})")


def notequal(x: Any, y: Any) -> Expr:
    """Not equal: notequal(x, y)."""
    x_str = x.pgf if isinstance(x, Expr) else x
    y_str = y.pgf if isinstance(y, Expr) else y
    return Expr(f"notequal({x_str}, {y_str})")


def notgreater(x: Any, y: Any) -> Expr:
    """Not greater than (<=): notgreater(x, y)."""
    x_str = x.pgf if isinstance(x, Expr) else x
    y_str = y.pgf if isinstance(y, Expr) else y
    return Expr(f"notgreater({x_str}, {y_str})")


def notless(x: Any, y: Any) -> Expr:
    """Not less than (>=): notless(x, y)."""
    x_str = x.pgf if isinstance(x, Expr) else x
    y_str = y.pgf if isinstance(y, Expr) else y
    return Expr(f"notless({x_str}, {y_str})")


# --- Logical functions ---


def and_(x: Any, y: Any) -> Expr:
    """Logical AND: and_(x, y).

    Name is ``and_`` to avoid shadowing Python's keyword ``and``.
    """
    x_str = x.pgf if isinstance(x, Expr) else x
    y_str = y.pgf if isinstance(y, Expr) else y
    return Expr(f"and({x_str}, {y_str})")


def or_(x: Any, y: Any) -> Expr:
    """Logical OR: or_(x, y).

    Name is ``or_`` to avoid shadowing Python's keyword ``or``.
    """
    x_str = x.pgf if isinstance(x, Expr) else x
    y_str = y.pgf if isinstance(y, Expr) else y
    return Expr(f"or({x_str}, {y_str})")


def not_(x: Any) -> Expr:
    """Logical NOT: not_(x).

    Name is ``not_`` to avoid shadowing Python's keyword ``not``.
    """
    x_str = x.pgf if isinstance(x, Expr) else x
    return Expr(f"not({x_str})")


def iseven(x: Any) -> Expr:
    """Check if even: iseven(x)."""
    x_str = x.pgf if isinstance(x, Expr) else x
    return Expr(f"iseven({x_str})")


def isodd(x: Any) -> Expr:
    """Check if odd: isodd(x)."""
    x_str = x.pgf if isinstance(x, Expr) else x
    return Expr(f"isodd({x_str})")


def isprime(x: Any) -> Expr:
    """Check if prime: isprime(x)."""
    x_str = x.pgf if isinstance(x, Expr) else x
    return Expr(f"isprime({x_str})")


# --- Control flow ---


def ifthenelse(condition: Any, true_val: Any, false_val: Any) -> Expr:
    """Conditional: ifthenelse(condition, true_val, false_val)."""
    cond_str = condition.pgf if isinstance(condition, Expr) else condition
    true_str = true_val.pgf if isinstance(true_val, Expr) else true_val
    false_str = false_val.pgf if isinstance(false_val, Expr) else false_val
    return Expr(f"ifthenelse({cond_str}, {true_str}, {false_str})")


# --- Base conversion ---


def bin_(x: Any) -> Expr:
    """Convert to binary: bin_(x).

    Name is ``bin_`` to avoid shadowing Python's built-in ``bin``.
    """
    x_str = x.pgf if isinstance(x, Expr) else x
    return Expr(f"bin({x_str})")


def oct_(x: Any) -> Expr:
    """Convert to octal: oct_(x).

    Name is ``oct_`` to avoid shadowing Python's built-in ``oct``.
    """
    x_str = x.pgf if isinstance(x, Expr) else x
    return Expr(f"oct({x_str})")


def hex_(x: Any) -> Expr:
    """Convert to hexadecimal: hex_(x).

    Name is ``hex_`` to avoid shadowing Python's built-in ``hex``.
    """
    x_str = x.pgf if isinstance(x, Expr) else x
    return Expr(f"hex({x_str})")


def Hex_(x: Any) -> Expr:
    """Convert to hexadecimal (capital): Hex_(x)."""
    x_str = x.pgf if isinstance(x, Expr) else x
    return Expr(f"Hex({x_str})")


# --- Geometric measurements ---


def width(dimension: Any) -> Expr:
    """Get width of a dimension: width(dimension)."""
    d_str = dimension.pgf if isinstance(dimension, Expr) else dimension
    return Expr(f"width({d_str})")


def height(dimension: Any) -> Expr:
    """Get height of a dimension: height(dimension)."""
    d_str = dimension.pgf if isinstance(dimension, Expr) else dimension
    return Expr(f"height({d_str})")


def depth(dimension: Any) -> Expr:
    """Get depth of a dimension: depth(dimension)."""
    d_str = dimension.pgf if isinstance(dimension, Expr) else dimension
    return Expr(f"depth({d_str})")


# --- Constants ---

pi = Expr("pi")
"""The constant π (pi)."""

e = Expr("e")
"""The constant e (Euler's number)."""

rnd = Expr("rnd")
"""Random number in [0, 1)."""

rand = Expr("rand")
"""Random number in [0, 1)."""

true = Expr("true")
"""Boolean true (1)."""

false = Expr("false")
"""Boolean false (0)."""

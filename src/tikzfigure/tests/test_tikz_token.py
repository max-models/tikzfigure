import pytest

from tikzfigure.arrows import TikzArrow
from tikzfigure.core.serialization import deserialize_tikz_value, serialize_tikz_value
from tikzfigure.core.tikz_token import TikzToken
from tikzfigure.decorations import TikzDecoration
from tikzfigure.marks import TikzMark
from tikzfigure.patterns import TikzPattern
from tikzfigure.shapes import TikzShape
from tikzfigure.styles import TikzStyle

TOKEN_CLASSES = [TikzArrow, TikzDecoration, TikzMark, TikzPattern, TikzShape, TikzStyle]


@pytest.mark.parametrize("cls", TOKEN_CLASSES)
def test_token_subclasses_inherit_tikz_token(cls):
    assert issubclass(cls, TikzToken)


@pytest.mark.parametrize("cls", TOKEN_CLASSES)
def test_token_empty_spec_raises(cls):
    with pytest.raises(ValueError):
        cls("")


@pytest.mark.parametrize("cls", TOKEN_CLASSES)
def test_token_str_repr_eq_hash_round_trip(cls):
    a = cls("some-spec")
    b = cls("some-spec")
    assert a == b
    assert hash(a) == hash(b)
    assert str(a) == "some-spec"
    assert a.to_tikz() == "some-spec"
    assert repr(a) == f"{cls.__name__}('some-spec')"

    restored = deserialize_tikz_value(serialize_tikz_value(a))
    assert restored == a
    assert type(restored) is cls


def test_tokens_of_different_types_are_not_equal():
    assert TikzArrow("thick") != TikzStyle("thick")
    assert TikzArrow("thick") != "thick"


def test_token_subclass_must_set_attr_name():
    class _Bare(TikzToken):
        pass

    token = _Bare("x")
    assert token.spec == "x"
    assert token.to_tikz() == "x"

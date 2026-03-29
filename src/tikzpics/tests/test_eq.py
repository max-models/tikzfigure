import pytest
from tikzfigure import TikzFigure
from tikzfigure.core.color import Color
from tikzfigure.core.coordinate import TikzCoordinate
from tikzfigure.core.loop import Loop
from tikzfigure.core.node import Node
from tikzfigure.core.path import TikzPath
from tikzfigure.core.plot import Plot3D
from tikzfigure.core.raw import RawTikz
from tikzfigure.core.variable import Variable


class TestNodeEq:
    def test_equal(self):
        a = Node(x=1, y=2, label="A", content="hello", color="red")
        b = Node(x=1, y=2, label="A", content="hello", color="red")
        assert a == b

    def test_not_equal_different_coords(self):
        a = Node(x=1, y=2, label="A")
        b = Node(x=3, y=4, label="A")
        assert a != b

    def test_not_equal_different_label(self):
        a = Node(x=1, y=2, label="A")
        b = Node(x=1, y=2, label="B")
        assert a != b

    def test_not_equal_different_kwargs(self):
        a = Node(x=1, y=2, label="A", color="red")
        b = Node(x=1, y=2, label="A", color="blue")
        assert a != b

    def test_not_equal_wrong_type(self):
        a = Node(x=1, y=2, label="A")
        assert a != "not a node"
        assert a != 42


class TestTikzCoordinateEq:
    def test_equal(self):
        a = TikzCoordinate(1.0, 2.0)
        b = TikzCoordinate(1.0, 2.0)
        assert a == b

    def test_equal_with_z(self):
        a = TikzCoordinate(1.0, 2.0, 3.0)
        b = TikzCoordinate(1.0, 2.0, 3.0)
        assert a == b

    def test_not_equal_different_x(self):
        a = TikzCoordinate(1.0, 2.0)
        b = TikzCoordinate(9.0, 2.0)
        assert a != b

    def test_not_equal_z_vs_no_z(self):
        a = TikzCoordinate(1.0, 2.0)
        b = TikzCoordinate(1.0, 2.0, 3.0)
        assert a != b

    def test_not_equal_wrong_type(self):
        a = TikzCoordinate(1.0, 2.0)
        assert a != (1.0, 2.0)
        assert a != "coord"


class TestVariableEq:
    def test_equal(self):
        a = Variable("x", 5)
        b = Variable("x", 5)
        assert a == b

    def test_not_equal_different_value(self):
        a = Variable("x", 5)
        b = Variable("x", 10)
        assert a != b

    def test_not_equal_different_label(self):
        a = Variable("x", 5)
        b = Variable("y", 5)
        assert a != b

    def test_not_equal_wrong_type(self):
        a = Variable("x", 5)
        assert a != 5
        assert a != "x"


class TestLoopEq:
    def test_equal(self):
        a = Loop("i", [1, 2, 3])
        b = Loop("i", [1, 2, 3])
        assert a == b

    def test_not_equal_different_values(self):
        a = Loop("i", [1, 2, 3])
        b = Loop("i", [4, 5, 6])
        assert a != b

    def test_not_equal_different_variable(self):
        a = Loop("i", [1, 2, 3])
        b = Loop("j", [1, 2, 3])
        assert a != b

    def test_not_equal_wrong_type(self):
        a = Loop("i", [1, 2, 3])
        assert a != [1, 2, 3]
        assert a != "i"


class TestTikzPathEq:
    def _nodes(self):
        return [Node(x=0, y=0, label="A"), Node(x=1, y=1, label="B")]

    def test_equal(self):
        nodes = self._nodes()
        a = TikzPath(nodes, draw="black")
        b = TikzPath(nodes, draw="black")
        assert a == b

    def test_not_equal_different_kwargs(self):
        nodes = self._nodes()
        a = TikzPath(nodes, draw="black")
        b = TikzPath(nodes, draw="red")
        assert a != b

    def test_not_equal_cycle(self):
        nodes = self._nodes()
        a = TikzPath(nodes)
        b = TikzPath(nodes, cycle=True)
        assert a != b

    def test_not_equal_wrong_type(self):
        a = TikzPath(self._nodes())
        assert a != "not a path"
        assert a != 0


class TestPlot3DEq:
    def test_equal(self):
        a = Plot3D(x=[0, 1], y=[0, 1], z=[0, 1])
        b = Plot3D(x=[0, 1], y=[0, 1], z=[0, 1])
        assert a == b

    def test_not_equal_different_data(self):
        a = Plot3D(x=[0, 1], y=[0, 1], z=[0, 1])
        b = Plot3D(x=[0, 2], y=[0, 1], z=[0, 1])
        assert a != b

    def test_not_equal_wrong_type(self):
        a = Plot3D(x=[0, 1], y=[0, 1], z=[0, 1])
        assert a != [[0, 1], [0, 1], [0, 1]]
        assert a != "plot"


class TestRawTikzEq:
    def test_equal(self):
        a = RawTikz(r"\draw (0,0) -- (1,1);")
        b = RawTikz(r"\draw (0,0) -- (1,1);")
        assert a == b

    def test_not_equal(self):
        a = RawTikz(r"\draw (0,0) -- (1,1);")
        b = RawTikz(r"\draw (0,0) -- (2,2);")
        assert a != b

    def test_not_equal_wrong_type(self):
        a = RawTikz(r"\draw (0,0) -- (1,1);")
        assert a != r"\draw (0,0) -- (1,1);"
        assert a != 0


class TestColorEq:
    def test_equal(self):
        a = Color("red!50!blue")
        b = Color("red!50!blue")
        assert a == b

    def test_not_equal(self):
        a = Color("red!50!blue")
        b = Color("green")
        assert a != b

    def test_not_equal_wrong_type(self):
        a = Color("red")
        assert a != "red"
        assert a != 0


class TestTikzFigureEq:
    def test_equal_empty(self):
        a = TikzFigure()
        b = TikzFigure()
        assert a == b

    def test_equal_with_node(self):
        a = TikzFigure()
        a.add_node(x=0, y=0, label="A", color="blue")
        b = TikzFigure()
        b.add_node(x=0, y=0, label="A", color="blue")
        assert a == b

    def test_not_equal_different_nodes(self):
        a = TikzFigure()
        a.add_node(x=0, y=0, label="A")
        b = TikzFigure()
        b.add_node(x=1, y=1, label="B")
        assert a != b

    def test_not_equal_extra_node(self):
        a = TikzFigure()
        a.add_node(x=0, y=0, label="A")
        b = TikzFigure()
        b.add_node(x=0, y=0, label="A")
        b.add_node(x=1, y=1, label="B")
        assert a != b

    def test_not_equal_wrong_type(self):
        a = TikzFigure()
        assert a != "not a figure"
        assert a != 0

from tikzfigure import TikzFigure, colors, marks, shapes
from tikzfigure.core.axis import Axis2D
from tikzfigure.core.loop import Loop
from tikzfigure.core.scope import Scope


def test_node_copy_allows_style_and_position_overrides():
    fig = TikzFigure()
    a = fig.add_node(
        0, 0, label="A", content="A", shape=shapes.circle, fill=colors.blue
    )

    b = a.copy(label="B", x=2, y=1, fill=colors.red)

    assert b is not a
    assert a.label == "A"
    assert a.x == 0
    assert a.y == 0
    assert a.kwargs["fill"] == colors.blue
    assert b.label == "B"
    assert b.x == 2
    assert b.y == 1
    assert b.kwargs["fill"] == colors.red
    assert "fill=red" in b.to_tikz()


def test_node_copy_accepts_pos_override_for_tuple_coordinates():
    fig = TikzFigure()
    a = fig.node((0, 2), label="A", content="A", shape=shapes.circle, fill=colors.blue)
    copied = a.copy(pos=(3, 2), label="B", content="B")

    b = fig.add_node(copied)

    assert b is copied
    assert b is not a
    assert b.label == "B"
    assert b.x == 3
    assert b.y == 2
    assert "pos" not in b.kwargs
    assert "(B) at ({3}, {2})" in b.to_tikz()


def test_node_copy_preserves_auto_generated_label_outside_figure_insertion():
    fig = TikzFigure()
    a = fig.node((0, 2), content="A", shape=shapes.circle, fill=colors.blue)

    b = a.copy(x=3, y=2, content="B")
    assert a.label == "node0"
    assert b.label == "node0"
    assert "(node0)" in a.to_tikz()
    assert "(node0)" in b.to_tikz()


def test_add_copy_assigns_fresh_label_for_auto_labeled_source():
    fig = TikzFigure()
    a = fig.node((0, 2), content="A", shape=shapes.circle, fill=colors.blue)

    b = fig.add_copy(a, x=3, y=2, content="B")
    c = fig.add_copy(a, x=0, y=0, content="C")
    d = fig.add_copy(a, x=3, y=0, content="D")

    assert a.label == "node0"
    assert b.label == "node1"
    assert c.label == "node2"
    assert d.label == "node3"
    assert [item.label for item in fig.layers.layers[0].items[:4]] == [
        "node0",
        "node1",
        "node2",
        "node3",
    ]


def test_add_copy_preserves_explicit_label_and_warns(caplog):
    source = TikzFigure()
    a = source.node((0, 0), label="A", content="A", shape=shapes.circle)
    target = TikzFigure()

    with caplog.at_level("WARNING"):
        b = target.add_copy(a, x=1, y=0, content="B")

    assert b.label == "A"
    assert "preserved explicit label 'A' on copied node" in caplog.text


def test_path_copy_reuses_referenced_nodes_and_overrides_kwargs():
    fig = TikzFigure()
    a = fig.add_node(0, 0, label="A")
    b = fig.add_node(1, 0, label="B")
    path = fig.draw([a, b], color=colors.blue)

    copied = path.copy(color=colors.red)

    assert copied is not path
    assert copied.nodes[0] is a
    assert copied.nodes[1] is b
    assert path.kwargs["color"] == colors.blue
    assert copied.kwargs["color"] == colors.red


def test_axis_copy_preserves_plots_and_accepts_overrides():
    axis = Axis2D(xlabel="x", ylabel="y", label="axis1", comment="original")
    axis.add_plot(
        [0, 1, 2], [0, 1, 4], label="series", color=colors.blue, mark=marks.square
    )
    axis.set_ticks("x", [0, 1], ["0", "1"])
    axis.set_legend(position="north west")

    copied = axis.copy(xlabel="time")

    assert copied is not axis
    assert copied.xlabel == "time"
    assert axis.xlabel == "x"
    assert copied.to_dict()["plots"] == axis.to_dict()["plots"]
    assert copied.to_dict()["ticks"] == axis.to_dict()["ticks"]
    assert copied.to_dict()["legend_pos"] == "north west"


def test_scope_copy_deep_clones_items_and_preserves_internal_refs():
    scope = Scope(label="s1", fill=colors.blue)
    a = scope.add_node(0, 0, label="A", content="A")
    b = scope.add_node(1, 0, label="B", content="B")
    scope.draw([a, b], color=colors.black)

    copied = scope.copy(label="s2", fill=colors.red)

    original_a, original_b, original_path = scope.items
    copied_a, copied_b, copied_path = copied.items

    assert copied is not scope
    assert copied.label == "s2"
    assert scope.kwargs["fill"] == colors.blue
    assert copied.kwargs["fill"] == colors.red
    assert copied_a is not original_a
    assert copied_b is not original_b
    assert copied_path is not original_path
    assert copied_path.nodes[0] is copied_a
    assert copied_path.nodes[1] is copied_b


def test_loop_copy_deep_clones_items_and_accepts_overrides():
    loop = Loop(variable="i", values=[1, 2], comment="numbers")
    a = loop.add_node(0, 0, label="A", content=r"$\i$")
    b = loop.add_node(1, 0, label="B", content="B")
    loop.add_path([a, b], color=colors.blue)

    copied = loop.copy(variable="j", values=[3, 4])

    assert copied is not loop
    assert copied.variable == "j"
    assert copied.values == [3, 4]
    assert loop.variable == "i"
    assert loop.values == [1, 2]
    assert copied.items[0] is not loop.items[0]
    assert copied.items[2].nodes[0] is copied.items[0]


def test_figure_copy_deep_clones_items_and_preserves_internal_refs():
    fig = TikzFigure(label="original")
    a = fig.add_node(0, 0, label="A", content="A", fill=colors.blue)
    b = fig.add_node(1, 0, label="B", content="B")
    fig.draw([a, b], color=colors.black)

    copied = fig.copy(label="copied")

    original_items = fig.layers.layers[0].items
    copied_items = copied.layers.layers[0].items
    copied_a, copied_b, copied_path = copied_items

    assert copied is not fig
    assert copied.to_dict()["label"] == "copied"
    assert fig.to_dict()["label"] == "original"
    assert copied_items[0] is not original_items[0]
    assert copied_items[1] is not original_items[1]
    assert copied_items[2] is not original_items[2]
    assert copied_a.label == "A"
    assert copied_b.label == "B"
    assert copied_path.nodes[0] is copied_a
    assert copied_path.nodes[1] is copied_b

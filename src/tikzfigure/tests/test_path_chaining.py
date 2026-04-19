import pytest

from tikzfigure import TikzFigure, colors, styles
from tikzfigure.core.coordinate import Coordinate
from tikzfigure.core.node import Node
from tikzfigure.core.path import TikzPath
from tikzfigure.core.path_builder import NodePathBuilder


def test_node_to_returns_builder_and_tracks_segment_options():
    a = Node(0, 0, label="A")
    b = Node(1, 0, label="B")
    c = Node(2, 0, label="C")

    builder = a.to(b).to(c, options=["bend left"], looseness=1.2)

    assert isinstance(builder, NodePathBuilder)
    assert builder.nodes == [a, b, c]
    assert builder.segment_options == [
        None,
        {"options": ["bend left"], "looseness": 1.2},
    ]


def test_node_to_normalizes_string_options_to_list():
    a = Node(0, 0, label="A")
    b = Node(1, 0, label="B")

    builder = a.to(b, options="bend left")

    assert isinstance(builder, NodePathBuilder)
    assert builder.nodes == [a, b]
    assert builder.segment_options == [{"options": ["bend left"]}]


def test_segment_options_returns_defensive_copy():
    a = Node(0, 0, label="A")
    b = Node(1, 0, label="B")
    c = Node(2, 0, label="C")

    builder = a.to(b).to(c, options=["bend left"], looseness=1.2)

    exposed_options = builder.segment_options
    assert exposed_options is not None

    exposed_options.append({"draw": "red"})
    exposed_options[1]["options"].append("dashed")
    exposed_options[1]["looseness"] = 3

    assert builder.segment_options == [
        None,
        {"options": ["bend left"], "looseness": 1.2},
    ]


def test_node_to_rejects_non_node_targets():
    a = Node(0, 0, label="A")

    with pytest.raises(TypeError, match="only supports Node or Coordinate targets"):
        a.to("B")  # type: ignore[arg-type]


def test_coordinate_to_returns_builder_and_tracks_segment_options():
    a = Coordinate("A", (0, 0))
    b = Coordinate("B", (1, 0))
    c = Coordinate("C", (2, 0))

    builder = a.to(b).to(c, node={"content": "label", "above": True})

    assert isinstance(builder, NodePathBuilder)
    assert builder.nodes == [a, b, c]
    assert builder.segment_options == [
        None,
        {"node": {"content": "label", "above": True}},
    ]


def test_normalize_segment_options_returns_none_for_empty_list():
    assert NodePathBuilder._normalize_segment_options(options=[]) is None


def test_builder_tracks_arc_segment_without_extra_waypoint():
    a = Node(0, 0, label="A")
    b = Node(1, 0, label="B")

    builder = a.to(b).arc(start_angle=0, end_angle=90, radius="3mm")

    assert builder.nodes == [a, b]
    assert builder.segment_options == [
        None,
        {"connector": "arc", "start_angle": 0, "end_angle": 90, "radius": "3mm"},
    ]


def test_draw_accepts_node_path_builder_and_reuses_segment_options():
    fig = TikzFigure()
    a = fig.add_node(x=0, y=0, label="A")
    b = fig.add_node(x=1, y=0, label="B")
    c = fig.add_node(x=2, y=0, label="C")

    path = fig.draw(
        a.to(b).to(c, options=["bend left"], looseness=1.2),
        color="blue",
    )

    assert [node.label for node in path.nodes] == ["A", "B", "C"]
    assert path.segment_options == [
        None,
        {"options": ["bend left"], "looseness": 1.2},
    ]
    assert (
        "\\draw[color=blue] (A) to (B) to[bend left, looseness=1.2] (C);"
        in path.to_tikz()
    )


def test_draw_accepts_coordinate_path_builder_and_reuses_segment_options():
    fig = TikzFigure()
    a = fig.add_coordinate("A", (0, 0))
    b = fig.add_coordinate("B", (1, 0))

    path = fig.draw(
        a.to(b, node={"content": "label", "above": True}),
        color="blue",
    )

    assert path.nodes == [a, b]
    assert path.segment_options == [{"node": {"content": "label", "above": True}}]
    assert "\\draw[color=blue] (A) to node[above] {label} (B);" in path.to_tikz()


def test_filldraw_accepts_node_path_builder():
    fig = TikzFigure()
    a = fig.add_node(x=0, y=0, label="A")
    b = fig.add_node(x=1, y=0, label="B")
    c = fig.add_node(x=2, y=0, label="C")

    path = fig.filldraw(
        a.to(b).to(c, options=["bend right"]),
        fill="red!20",
    )

    assert path.tikz_command == "filldraw"
    assert path.segment_options == [None, {"options": ["bend right"]}]


def test_draw_renders_arc_path_segment_from_builder():
    fig = TikzFigure()
    a = fig.add_node(x=0, y=0, label="A")
    b = fig.add_node(x=1, y=0, label="B")

    path = fig.draw(a.to(b).arc(start_angle=0, end_angle=90, radius="3mm"))

    assert path.segment_options == [
        None,
        {"connector": "arc", "start_angle": 0, "end_angle": 90, "radius": "3mm"},
    ]
    assert "\\draw (A) to (B) arc[start angle=0, end angle=90, radius=3mm];" in (
        path.to_tikz()
    )


def test_draw_allows_segments_after_arc():
    fig = TikzFigure()
    a = fig.add_node(x=0, y=0, label="A")
    b = fig.add_node(x=1, y=0, label="B")
    c = fig.add_node(x=2, y=1, label="C")

    path = fig.draw(
        a.to(b).arc(start_angle=0, end_angle=90, radius="3mm").to(c),
        color="blue",
    )

    assert (
        "\\draw[color=blue] (A) to (B) arc[start angle=0, end angle=90, radius=3mm] to (C);"
        in path.to_tikz().replace("\n\t", " ")
    )


def test_path_to_dict_from_dict_preserves_rich_segment_options():
    fig = TikzFigure()
    a = fig.add_node(x=0, y=0, label="A")
    b = fig.add_node(x=1, y=0, label="B")

    path = fig.draw(
        a.to(
            b,
            options=[styles.bend_left()],
            node={
                "content": "label",
                "fill": colors.white,
            },
        ),
        color=colors.red,
    )

    data = path.to_dict()

    assert data["kwargs"]["color"]["__tikzfigure_serialized_type__"] == "TikzColor"
    assert (
        data["segment_options"][0]["options"][0]["__tikzfigure_serialized_type__"]
        == "TikzStyle"
    )
    assert (
        data["segment_options"][0]["node"]["fill"]["__tikzfigure_serialized_type__"]
        == "TikzColor"
    )

    restored = TikzPath.from_dict(data, node_lookup={"A": a, "B": b})
    assert restored.kwargs["color"] == colors.red
    assert restored.segment_options == [
        {
            "options": [styles.bend_left()],
            "node": {"content": "label", "fill": colors.white},
        }
    ]


def test_draw_rejects_extra_segment_options_when_builder_is_used():
    fig = TikzFigure()
    a = fig.add_node(x=0, y=0, label="A")
    b = fig.add_node(x=1, y=0, label="B")

    with pytest.raises(ValueError, match="segment_options cannot be passed"):
        fig.draw(a.to(b), segment_options=[{"options": ["bend left"]}])


def test_draw_list_input_still_renders_plain_to_segments():
    fig = TikzFigure()
    a = fig.add_node(x=0, y=0, label="A")
    b = fig.add_node(x=1, y=0, label="B")
    c = fig.add_node(x=2, y=0, label="C")

    path = fig.draw([a, b, c], color="blue")

    assert path.segment_options is None
    assert "\\draw[color=blue] (A) to (B) to (C);" in path.to_tikz()

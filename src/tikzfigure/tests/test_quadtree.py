from tikzfigure import QuadtreeNode, QuadtreePlot, TikzFigure


def test_quadtree_plot_renders_nested_quadrants_with_level_colors():
    tree = [None, QuadtreeNode(), [None, None, None, None], None]
    plot = QuadtreePlot(tree, bounds=(0, 0, 4, 4), level_colors=["red", "blue"])

    tikz = plot.to_tikz()

    assert tikz.count("\\draw") == 3
    assert "draw=red" in tikz
    assert tikz.count("draw=blue") == 2
    assert "(2.0,0) rectangle (4,2.0)" in tikz


def test_quadtree_figure_integration_and_serialization():
    fig = TikzFigure()
    fig.add_quadtree(
        {"sw": None, "se": None, "nw": None, "ne": None},
        level_colors=["green"],
    )

    output = fig.generate_tikz(skip_header=True)
    assert "draw=green" in output

    original = fig.layers.layers[0].items[0]
    restored = QuadtreePlot.from_dict(original.to_dict())
    assert restored.level_colors == ["green"]
    assert restored.to_tikz() == original.to_tikz()


def test_quadtree_rejects_invalid_children_and_colors():
    try:
        QuadtreeNode([None, None])
    except ValueError:
        pass
    else:
        raise AssertionError("expected invalid child count to fail")

    try:
        QuadtreePlot(None, level_colors=[])
    except ValueError:
        pass
    else:
        raise AssertionError("expected empty colors to fail")

from tikzpics import TikzFigure


def test_tikz_equivalence():

    tikz = TikzFigure()

    options = ["draw", "rounded corners", "line width=3"]

    # M
    nodes = [[0, 0], [0, 3], [1, 2], [2, 3], [2, 0]]
    for i, node_data in enumerate(nodes):
        tikz.add_node(
            x=node_data[0],
            y=node_data[1],
            label=f"M{i}",
            layer=0,
            color="red",
            content=f"Node {i}",
        )
    tikz.draw(
        [f"M{i}" for i in range(len(nodes))],
        options=options,
        layer=1,
    )
    t1 = tikz.generate_tikz()

    # Create a new TikzFigure instance based on the generated tikz code
    tikz_2 = TikzFigure(tikz_code=tikz.generate_tikz())

    t2 = tikz_2.generate_tikz()

    # Check that generated code is equivalant
    assert t1 == t2, "Generated tikz code not the same as original"


def test_logo_equivalence():

    tikz = TikzFigure()

    options = ["draw", "rounded corners", "line width=3"]

    # M
    nodes = [[0, 0], [0, 10], [1, 2], [2, 3], [2, 0]]
    for i, node_data in enumerate(nodes):
        tikz.add_node(
            x=node_data[0],
            y=node_data[1],
            label=f"M{i}",
            layer=0,
            color="red",
            content=f"Node {i}",
        )
    tikz.draw(
        [f"M{i}" for i in range(len(nodes))],
        options=options,
        layer=1,
    )
    t1 = tikz.generate_tikz()

    # Create a new TikzFigure instance based on the generated tikz code
    tikz_2 = TikzFigure(tikz_code=tikz.generate_tikz())
    t2 = tikz_2.generate_tikz()
    print(f"{t1}")
    print(f"{t2}")
    # Check that generated code is equivalant
    assert t1 == t2, "Generated tikz code not the same as original"


if __name__ == "__main__":
    test_logo_equivalence()
    test_tikz_equivalence()

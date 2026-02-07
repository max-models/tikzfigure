from tikzpics.core.raw import RawTikz


def test_raw_tikz_to_tikz():
    """Test that to_tikz() returns the tikz code with newline."""
    tikz_code = "\\draw (0,0) -- (1,1);"
    raw = RawTikz(tikz_code)
    assert raw.to_tikz() == tikz_code + "\n"


def test_raw_tikz_multiline():
    """Test that RawTikz handles multiline tikz code."""
    tikz_code = """\\draw (0,0) -- (1,1);
\\draw (2,2) -- (3,3);
\\node at (0,0) {Label};"""
    raw = RawTikz(tikz_code)
    assert raw.tikz_code == tikz_code
    assert raw.to_tikz() == tikz_code + "\n"


def test_raw_tikz_with_special_characters():
    """Test that RawTikz handles special characters in tikz code."""
    tikz_code = "\\draw[->] (0,0) -- node[above] {$\\alpha$} (1,1);"
    raw = RawTikz(tikz_code)
    assert raw.tikz_code == tikz_code
    assert raw.to_tikz() == tikz_code + "\n"


def test_raw_tikz_with_options():
    """Test that RawTikz handles tikz code with various options."""
    tikz_code = "\\draw[thick,blue,dashed] (0,0) circle (1cm);"
    raw = RawTikz(tikz_code)
    assert raw.tikz_code == tikz_code
    assert raw.to_tikz() == tikz_code + "\n"


def test_raw_tikz_preserves_whitespace():
    """Test that RawTikz preserves leading and trailing whitespace."""
    tikz_code = "  \\draw (0,0) -- (1,1);  "
    raw = RawTikz(tikz_code)
    assert raw.tikz_code == tikz_code
    assert raw.to_tikz() == tikz_code + "\n"


# Integration tests with TikzFigure


def test_raw_tikz_integration_with_figure():
    """Test that RawTikz integrates properly with TikzFigure using add_raw()."""
    from tikzpics import TikzFigure

    fig = TikzFigure()
    fig.add_raw("\\draw (0,0) -- (1,1);")

    tikz_output = fig.generate_tikz()
    assert "\\draw (0,0) -- (1,1);" in tikz_output
    assert "\\begin{tikzpicture}" in tikz_output
    assert "\\end{tikzpicture}" in tikz_output


def test_raw_tikz_with_comments():
    """Test adding comments through raw TikZ code."""
    from tikzpics import TikzFigure

    fig = TikzFigure()
    fig.add_raw("% This is a comment in the TikZ code")
    fig.add_raw("\\draw (0,0) -- (1,1);")

    tikz_output = fig.generate_tikz()
    assert "% This is a comment in the TikZ code" in tikz_output
    assert "\\draw (0,0) -- (1,1);" in tikz_output


def test_raw_tikz_with_nodes_and_references():
    """Test using raw TikZ code to reference previously created nodes."""
    from tikzpics import TikzFigure

    fig = TikzFigure()

    n1 = fig.add_node(
        0, 0, shape="circle", color="white", fill="blue", content="Hello!"
    )
    n2 = fig.add_node(5, 0, shape="circle", color="white", fill="red", content="Hi!")

    # Add raw TikZ code that references the nodes
    fig.add_raw(f"\\draw[->, thick, dashed] ({n2.label}) -- ({n1.label});")

    tikz_output = fig.generate_tikz()

    # Verify nodes are in output
    assert n1.label in tikz_output
    assert n2.label in tikz_output

    # Verify raw draw command is in output
    assert f"\\draw[->, thick, dashed] ({n2.label}) -- ({n1.label});" in tikz_output


def test_raw_tikz_complex_integration():
    """Test complex integration with nodes and multiple raw TikZ additions."""
    from tikzpics import TikzFigure

    fig = TikzFigure()

    n1 = fig.add_node(
        0, 0, shape="circle", color="white", fill="blue", content="Hello!"
    )
    n2 = fig.add_node(5, 0, shape="circle", color="white", fill="red", content="Hi!")

    fig.add_raw("% This is a comment in the TikZ code")
    fig.add_raw("\\node at (2.5, 1) {This is a raw TikZ node};")
    fig.add_raw(f"\\draw[->, thick, dashed] ({n2.label}) -- ({n1.label});")

    tikz_output = fig.generate_tikz()

    # Check all elements are present
    assert "% This is a comment in the TikZ code" in tikz_output
    assert "\\node at (2.5, 1) {This is a raw TikZ node};" in tikz_output
    assert f"\\draw[->, thick, dashed] ({n2.label}) -- ({n1.label});" in tikz_output
    assert "Hello!" in tikz_output
    assert "Hi!" in tikz_output


def test_raw_tikz_with_layers():
    """Test adding raw TikZ code to different layers."""
    from tikzpics import TikzFigure

    fig = TikzFigure()

    fig.add_raw("\\draw[red] (0,0) -- (1,1);", layer=0)
    fig.add_raw("\\draw[blue] (0,1) -- (1,0);", layer=1)

    tikz_output = fig.generate_tikz()

    assert "\\draw[red] (0,0) -- (1,1);" in tikz_output
    assert "\\draw[blue] (0,1) -- (1,0);" in tikz_output


def test_raw_tikz_with_mathematical_notation():
    """Test raw TikZ with mathematical notation and LaTeX commands."""
    from tikzpics import TikzFigure

    fig = TikzFigure()

    fig.add_raw(
        "\\node at (0,0) {$\\int_0^\\infty e^{-x^2} dx = \\frac{\\sqrt{\\pi}}{2}$};"
    )
    fig.add_raw("\\draw[->] (0,0) -- node[above] {$\\vec{F} = m\\vec{a}$} (2,0);")

    tikz_output = fig.generate_tikz()

    assert "$\\int_0^\\infty e^{-x^2} dx = \\frac{\\sqrt{\\pi}}{2}$" in tikz_output
    assert "$\\vec{F} = m\\vec{a}$" in tikz_output


def test_raw_tikz_multiple_additions_order():
    """Test that multiple raw TikZ additions maintain order."""
    from tikzpics import TikzFigure

    fig = TikzFigure()

    fig.add_raw("% First")
    fig.add_raw("% Second")
    fig.add_raw("% Third")

    tikz_output = fig.generate_tikz()

    # Check all comments are present
    assert "% First" in tikz_output
    assert "% Second" in tikz_output
    assert "% Third" in tikz_output

    # Check order is maintained
    first_pos = tikz_output.find("% First")
    second_pos = tikz_output.find("% Second")
    third_pos = tikz_output.find("% Third")

    assert first_pos < second_pos < third_pos

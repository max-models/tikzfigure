import pytest

from tikzfigure import TikzFigure
from tikzfigure.core.circle import Circle
from tikzfigure.core.coordinate import Coordinate
from tikzfigure.core.loop import Loop
from tikzfigure.core.node import Node
from tikzfigure.core.path import TikzPath
from tikzfigure.core.raw import RawTikz
from tikzfigure.core.rectangle import Rectangle
from tikzfigure.core.scope import Scope
from tikzfigure.parser import TikzParseError, parse_tikz, split_statements


def picture(body: str) -> str:
    return "\\begin{tikzpicture}\n" + body.strip("\n") + "\n\\end{tikzpicture}"


def items(fig: TikzFigure, layer: int = 0) -> list:
    return fig.layers.layers[layer].items


def body_lines(fig: TikzFigure) -> list[str]:
    lines = fig.generate_tikz(skip_header=True).strip().splitlines()
    return [line.strip() for line in lines[1:-1]]


def assert_stable(fig: TikzFigure) -> None:
    generated = fig.generate_tikz()
    assert TikzFigure.from_tikz_code(generated).generate_tikz() == generated


# ---------------------------------------------------------------------- #
# Statement splitting


def test_split_statements_respects_braces_comments_and_multiline():
    statements = split_statements(
        r"""
\node[label={a; b}] (a)
    at (0, 0) {x; y}; \draw (a) -- (1, 1); % trailing
% about c
\node (c) at (1, 0) {50\% done};
"""
    )
    assert [(s.kind, s.name) for s in statements] == [
        ("command", "node"),
        ("command", "draw"),
        ("comment", ""),
        ("command", "node"),
    ]
    assert statements[0].text.endswith("{x; y};")
    assert statements[0].line == 2
    assert statements[3].comments == [" about c"]


def test_split_statements_environments_and_foreach():
    statements = split_statements(
        r"""
\begin{scope}[red]
    \begin{scope}
        \draw (0, 0) -- (1, 0);
    \end{scope}
\end{scope}
\foreach \x in {1,2} \draw (\x, 0) -- (\x, 1);
\foreach \x in {1,2} {
    \node at (\x, 0) {};
}
"""
    )
    assert [(s.kind, s.name) for s in statements] == [
        ("environment", "scope"),
        ("foreach", "foreach"),
        ("foreach", "foreach"),
    ]


@pytest.mark.parametrize(
    ("source", "message"),
    [
        (r"\draw (0, 0) -- (1, 1);", "no \\begin{tikzpicture}"),
        (picture(r"\node at (0, 0) {unclosed;"), "unclosed '{'"),
        (picture(r"\draw (0, 0) -- (1, 1)"), "not terminated by ';'"),
        (picture(r"\begin{scope} \draw (0, 0) -- (1, 1);"), "missing \\end{scope}"),
        (
            "\\begin{tikzpicture}\n\\draw (0,0) -- (1,1);\n",
            "missing \\end{tikzpicture}",
        ),
        (picture(r"\draw (0, 0) -- (1, 1);}"), "unbalanced '}'"),
    ],
)
def test_malformed_source_raises(source, message):
    with pytest.raises(TikzParseError, match=message.replace("\\", "\\\\")):
        TikzFigure.from_tikz_code(source)


def test_parse_error_reports_line_number():
    with pytest.raises(TikzParseError) as info:
        TikzFigure.from_tikz_code(
            picture("\\draw (0, 0) -- (1, 1);\n\\node at (0, 0) {x")
        )
    assert info.value.line == 3


# ---------------------------------------------------------------------- #
# Nodes


def test_node_with_structured_options():
    result = parse_tikz(
        picture(r"\node[draw, fill=red, line width=2pt] (a) at (1, 2.5) {$x$};")
    )
    node = items(result.figure)[0]
    assert isinstance(node, Node)
    assert (node.label, node.x, node.y, node.content) == ("a", 1, 2.5, "$x$")
    assert node.options == ["draw"]
    assert node.kwargs == {"fill": "red", "line_width": "2pt"}
    assert result.coverage == 1.0


def test_node_option_order_is_preserved():
    # Node() would reorder ``shape`` before ``fill``; the parser must not.
    fig = TikzFigure.from_tikz_code(
        picture(r"\node[fill=red, shape=circle] (a) at (0, 0) {};")
    )
    assert body_lines(fig) == [r"\node[fill=red, shape=circle] (a) at ({0}, {0}) {};"]


def test_node_label_option_is_not_the_node_name():
    fig = TikzFigure.from_tikz_code(picture(r"\node[label=above:hi] (a) at (0, 0) {};"))
    node = items(fig)[0]
    assert node.label == "a"
    assert "label=above:hi" in node.options


def test_node_options_after_name_multiline_and_relative_position():
    fig = TikzFigure.from_tikz_code(
        picture(
            r"""
\node (a) [draw]
    at (0, 0)
    {A};
\node[right=of a] (b) {B};
"""
        )
    )
    a, b = items(fig)
    assert a.options == ["draw"] and a.label == "a"
    assert b.x is None and b.kwargs == {"right": "of a"}


def test_content_with_semicolons_braces_and_escaped_percent():
    fig = TikzFigure.from_tikz_code(
        picture(r"\node (a) at (0, 0) {$f(x)=[0,1]; {x}$ 100\% sure}; % comment")
    )
    assert items(fig)[0].content == r"$f(x)=[0,1]; {x}$ 100\% sure"


def test_anonymous_nodes_do_not_collide_with_existing_auto_labels():
    fig = TikzFigure.from_tikz_code(
        picture(
            r"""
\node at (0, 0) {first};
\node (node0) at (1, 0) {explicit};
"""
        )
    )
    labels = [node.label for node in items(fig)]
    assert len(set(labels)) == 2
    assert "node0" in labels


# ---------------------------------------------------------------------- #
# Paths and shapes


def test_path_connectors_anchors_inline_nodes_and_cycle():
    fig = TikzFigure.from_tikz_code(
        picture(
            r"""
\node (a) at (0, 0) {A};
\node (b) at (2, 0) {B};
\draw[->, color=blue] (a.east) -- node[above, sloped] {go} (b) to[bend left] (1, -1) |- (0, -2) -- cycle;
"""
        )
    )
    path = items(fig)[2]
    assert isinstance(path, TikzPath)
    assert path.tikz_command == "draw"
    assert path.options == ["->"] and path.kwargs == {"color": "blue"}
    assert path.node_anchors == ["east", None, None, None]
    assert path.cycle
    assert path.segment_options == [
        {"connector": "--", "node": {"content": "go", "options": ["above", "sloped"]}},
        {"options": ["bend left"]},
        {"connector": "|-"},
    ]
    assert_stable(fig)


def test_plain_to_path_matches_draw_api():
    parsed = TikzFigure.from_tikz_code(
        picture(
            r"""
\node (a) at (0, 0) {};
\node (b) at (1, 0) {};
\draw[thick] (a) to (b);
"""
        )
    )
    built = TikzFigure()
    built.add_node(0, 0, label="a")
    built.add_node(1, 0, label="b")
    built.draw(["a", "b"], options=["thick"])
    assert parsed == built


def test_arc_and_fill_commands():
    fig = TikzFigure.from_tikz_code(
        picture(
            r"\fill[red] (0, 0) -- (1, 0) arc[start angle=0, end angle=90, radius=1] -- cycle;"
        )
    )
    path = items(fig)[0]
    assert path.tikz_command == "fill"
    assert {
        "connector": "arc",
        "options": ["start angle=0", "end angle=90", "radius=1"],
    } in (path.segment_options)


def test_circle_and_rectangle_become_shapes():
    fig = TikzFigure.from_tikz_code(
        picture(
            r"""
\draw[thick] (0, 0) circle (1cm);
\filldraw[fill=blue] (0, 0) rectangle ({\w}, {max(1,2)});
"""
        )
    )
    circle, rectangle = items(fig)
    assert isinstance(circle, Circle) and isinstance(rectangle, Rectangle)
    assert rectangle.tikz_command == "filldraw"
    assert_stable(fig)


@pytest.mark.parametrize(
    ("statement", "reason"),
    [
        (r"\draw (0, 0) -- ++(1, 0);", "relative coordinate"),
        (r"\draw (0, 0) -- (1, 0) node[right] {x};", "path operation 'node'"),
        (r"\draw (0, 0) edge (1, 0);", "path operation 'edge'"),
        (r"\draw (0, 0) grid (1, 1);", "path operation 'grid'"),
        (r"\draw (missing) -- (1, 0);", "reference to undefined node"),
        (r"\draw (0, 0) [red] -- (1, 0);", "options in the middle of a path"),
        (r"\draw (30:1) -- (0, 0);", "polar coordinate"),
        (r"\matrix [matrix of nodes] { a \\ };", "command '\\matrix'"),
    ],
)
def test_unsupported_statements_are_kept_verbatim(statement, reason):
    result = parse_tikz(picture(statement))
    assert [d.reason for d in result.raw] == [reason]
    raw = items(result.figure)[0]
    assert isinstance(raw, RawTikz)
    assert body_lines(result.figure) == [statement]


def test_strict_mode_raises_for_raw_statements():
    source = picture(r"\draw (0, 0) edge (1, 0);")
    with pytest.raises(TikzParseError, match="path operation 'edge'"):
        TikzFigure.from_tikz_code(source, strict=True)
    TikzFigure.from_tikz_code(picture(r"\draw (0, 0) -- (1, 0);"), strict=True)


# ---------------------------------------------------------------------- #
# Coordinates, containers and definitions


def test_coordinates():
    fig = TikzFigure.from_tikz_code(
        picture(
            r"""
\coordinate (p) at (1, 2);
\coordinate (q) at ($(p)!0.5!(0,0)$);
\draw (p) -- (q);
"""
        )
    )
    p, q, path = items(fig)
    assert isinstance(p, Coordinate) and isinstance(q, Coordinate)
    assert isinstance(path, TikzPath)
    assert_stable(fig)


def test_scopes_and_loops_nest_and_resolve_nodes():
    result = parse_tikz(
        picture(
            r"""
\node (a) at (0, 0) {};
\begin{scope}[xshift=1cm, red]
    \foreach \i in {1,...,3} {
        \node (n\i) at (\i, 0) {\i};
        \draw (a) -- (n\i);
    }
\end{scope}
"""
        )
    )
    scope = items(result.figure)[1]
    assert isinstance(scope, Scope)
    assert scope.options == ["xshift=1cm", "red"]
    loop = scope.items[0]
    assert isinstance(loop, Loop)
    assert loop.variable == "i" and loop.values == [1, "...", 3]
    assert [type(item) for item in loop.items] == [Node, TikzPath]
    assert result.coverage == 1.0
    assert_stable(result.figure)


def test_unsupported_foreach_is_raw():
    result = parse_tikz(
        picture(r"\foreach \x/\y in {1/2} { \draw (\x, \y) -- (0, 0); }")
    )
    assert result.raw[0].reason == "foreach with options or multiple variables"


def test_definitions_are_hoisted_only_when_order_is_kept():
    result = parse_tikz(
        picture(
            r"""
\tikzset{hot/.style={draw=red, very thick}}
\pgfmathsetmacro{\r}{1.5}
\pgfkeys{/pgf/declare function={sq(\x) = \x*\x;}}
\colorlet{soft}{blue!20}
\draw[hot] (0, 0) -- (1, 0);
\pgfmathsetmacro{\late}{2}
"""
        )
    )
    fig = result.figure
    assert [v.label for v in fig.variables] == ["r"]
    assert [f.name for f in fig.declared_functions] == ["sq"]
    assert [name for name, _ in fig.colors] == ["soft"]
    assert fig.named_styles[0]["name"] == "hot"
    assert [d.reason for d in result.raw] == ["variable definition would be reordered"]
    assert_stable(fig)


def test_variable_after_color_is_not_reordered():
    result = parse_tikz(picture("\\colorlet{c}{red}\n\\pgfmathsetmacro{\\a}{1}"))
    assert [d.reason for d in result.raw] == ["variable definition would be reordered"]


def test_numbered_layers():
    fig = TikzFigure.from_tikz_code(
        picture(
            r"""
\pgfdeclarelayer{0}
\pgfdeclarelayer{1}
\pgfsetlayers{0,1}
\begin{pgfonlayer}{1}
    \node (a) at (0, 0) {};
\end{pgfonlayer}{1}
\begin{pgfonlayer}{0}
    \draw (a) -- (1, 1);
\end{pgfonlayer}
"""
        )
    )
    assert isinstance(items(fig, 1)[0], Node)
    assert isinstance(items(fig, 0)[0], TikzPath)
    assert_stable(fig)


def test_named_layers_are_raw():
    result = parse_tikz(
        picture(
            r"""
\pgfdeclarelayer{background}
\pgfsetlayers{background,main}
\begin{pgfonlayer}{background}
    \fill (0, 0) circle (1);
\end{pgfonlayer}
"""
        )
    )
    assert {d.reason for d in result.raw} == {"named pgf layer"}


def test_picture_options_and_styles():
    fig = TikzFigure.from_tikz_code(
        "\\begin{tikzpicture}[scale=2, box/.style={draw, fill=red}]\n"
        "\\node[box] (a) at (0, 0) {};\n\\end{tikzpicture}"
    )
    assert fig._figure_setup == "scale=2"
    assert fig.named_styles == [
        {"name": "box", "options": ["draw"], "kwargs": {"fill": "red"}}
    ]
    assert_stable(fig)


def test_picture_options_with_style_first_stay_verbatim():
    fig = TikzFigure.from_tikz_code(
        "\\begin{tikzpicture}[box/.style={draw}, scale=2]\n\\end{tikzpicture}"
    )
    assert fig._figure_setup == "box/.style={draw}, scale=2"
    assert fig.named_styles == []


# ---------------------------------------------------------------------- #
# Comments and document structure


def test_comments_attach_to_following_statement():
    fig = TikzFigure.from_tikz_code(
        picture(
            r"""
% first
% about a
\node (a) at (0, 0) {};
% standalone

% about the path
\draw (a) -- (1, 1); % trailing
"""
        )
    )
    first, node, standalone, path, trailing = items(fig)
    assert first.tikz_code == "% first"
    assert node.comment == "about a"
    assert standalone.tikz_code == "% standalone"
    assert path.comment == "about the path"
    assert trailing.tikz_code == "% trailing"


def test_generated_comments_are_not_duplicated():
    fig = TikzFigure()
    fig.add_node(0, 0, label="a", layer=0)
    fig.add_node(1, 0, label="b", layer=1)
    fig.draw(["a", "b"], layer=1, comment="edge")
    assert_stable(fig)


def test_full_document_and_figure_environment():
    fig = TikzFigure.from_tikz_code(
        r"""
\documentclass{standalone}
\usepackage{tikz}
\usepackage{amsmath,bm}
\usetikzlibrary{calc, positioning}
\newcommand{\myvec}[1]{\bm{#1}}
\begin{document}
\begin{figure}
\begin{tikzpicture}
    \node (a) at (0, 0) {$\myvec{x}$};
\end{tikzpicture}
\label{fig:vec}
\end{figure}
\end{document}
"""
    )
    assert fig.extra_packages == ["amsmath", "bm"]
    assert fig.tikz_libraries == ["calc", "positioning"]
    assert fig.document_setup == r"\newcommand{\myvec}[1]{\bm{#1}}"
    assert fig._label == "fig:vec"


def test_additional_tikzpictures_are_reported():
    result = parse_tikz(picture("") + "\n" + picture(r"\draw (0,0) -- (1,1);"))
    assert result.raw[0].reason == "additional tikzpicture ignored"


def test_constructor_keyword_still_parses():
    fig = TikzFigure(tikz_code=picture(r"\node (a) at (0, 0) {A};"))
    assert fig.layers.get_node("a").content == "A"


def test_summary_lists_raw_statements():
    result = parse_tikz(picture("\\node (a) at (0, 0) {};\n\\draw (a) edge (1, 1);"))
    assert result.summary().splitlines() == [
        "1/2 statements mapped (50%)",
        "  line 3: \\draw kept as raw TikZ: path operation 'edge'",
    ]
    assert result.unsupported_reasons() == {"path operation 'edge'": 1}

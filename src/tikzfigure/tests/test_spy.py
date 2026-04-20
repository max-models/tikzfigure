from tikzfigure import TikzFigure, colors, shapes


def test_add_spy_auto_enables_figure_spy_scope():
    fig = TikzFigure()
    fig.draw([(0, 0), (2, 0)], color=colors.black)

    spy = fig.spy(
        on=(1, 0),
        at=(3, 1),
        options=[colors.red],
        magnification=3,
        size="1cm",
        connect_spies=True,
        node_label="zoom",
        node_options=[shapes.circle],
        node_style={"left": True, "draw": colors.red},
    )

    tikz = fig.generate_tikz()

    assert "spy" in fig.tikz_libraries
    assert "\\begin{tikzpicture}[spy scope]" in tikz
    assert spy.to_tikz() == (
        "\\spy[red, connect spies, magnification=3, size=1cm] "
        "on ({1}, {0}) in node (zoom) [circle, left, draw=red] at ({3}, {1});\n"
    )


def test_spy_scope_presets_and_styles_render():
    fig = TikzFigure()

    with fig.spy_scope(
        mode="outlines",
        options=[shapes.circle],
        magnification=4,
        size="2cm",
        connect_spies=True,
        every_spy_in_node_options=[shapes.circle],
        every_spy_in_node_style={"draw": colors.blue, "line_width": "0.8pt"},
        every_spy_on_node_style={"draw": colors.red, "line_width": "0.2pt"},
    ) as local:
        local.draw([(0, 0), (2, 0)], color=colors.black)
        local.spy(
            on=(1, 0),
            at=(3, 1),
            options=[colors.green],
            node_label="detail",
            node_style={"right": True},
        )

    tikz = fig.generate_tikz()

    assert (
        "spy using outlines={circle, connect spies, magnification=4, size=2cm}" in tikz
    )
    assert "every spy in node/.style={circle, draw=blue, line width=0.8pt}" in tikz
    assert "every spy on node/.style={draw=red, line width=0.2pt}" in tikz
    assert "\\spy[green] on ({1}, {0}) in node (detail) [right] at ({3}, {1});" in tikz


def test_configure_spy_scope_supports_lens_and_connection_path():
    fig = TikzFigure()
    fig.configure_spy_scope(
        mode="overlays",
        size="12mm",
        lens_kwargs={"scale": 3, "rotate": 10},
        every_spy_in_node_style={"shape": shapes.shape("magnifying glass")},
        spy_connection_path=r"\draw[blue, dashed] (tikzspyonnode) -- (tikzspyinnode);",
    )
    fig.draw([(0, 0), (2, 1)], color=colors.black)
    fig.spy(on=(1, 0.5), at=(3, -1))

    tikz = fig.generate_tikz()

    assert "spy using overlays={size=12mm, lens={scale=3, rotate=10}}" in tikz
    assert "every spy in node/.style={shape=magnifying glass}" in tikz
    assert (
        "spy connection path={\\draw[blue, dashed] (tikzspyonnode) -- (tikzspyinnode);}"
        in tikz
    )


def test_spy_round_trips_through_figure_dict():
    fig = TikzFigure()
    a = fig.node((0, 0), label="A", content="A")
    with fig.spy_scope(
        mode="scope",
        magnification=2,
        size="1cm",
        every_spy_on_node_options=[shapes.circle],
    ) as local:
        local.draw([a, (2, 0)], color=colors.black)
        local.spy(
            on=a,
            at=(3, 1),
            node_label="zoom",
            node_options=[shapes.circle],
            node_style={"draw": colors.blue},
        )

    data = fig.to_dict()
    fig2 = TikzFigure.from_dict(data)

    assert data["layers"][0][1]["type"] == "Scope"
    assert data["layers"][0][1]["items"][1]["type"] == "Spy"
    assert fig2.generate_tikz() == fig.generate_tikz()


def test_axis_can_render_coordinates_and_spy_inside_axis():
    fig = TikzFigure()
    fig.configure_spy_scope(
        mode="outlines",
        options=[shapes.rectangle],
        magnification=3,
        connect_spies=True,
    )

    ax = fig.axis2d(
        grid="major",
        options=["no markers"],
        domain="-5:5",
        enlargelimits="false",
    )
    ax.add_plot(func="x^2")
    ax.add_plot(func="x^3")

    spypoint = ax.coordinate("spypoint", at="axis cs:0,0")
    spyviewer = ax.coordinate("spyviewer", at="axis cs:0.5,-90")
    ax.spy(
        on=spypoint,
        at=spyviewer,
        width="6cm",
        height="1cm",
        node_style={"fill": colors.white},
    )

    tikz = fig.generate_tikz()

    assert "spy using outlines={rectangle, connect spies, magnification=3}" in tikz
    assert (
        "\\begin{axis}[no markers, grid=major, domain=-5:5, enlargelimits=false]"
        in tikz
    )
    assert "\\coordinate (spypoint) at (axis cs:0,0);" in tikz
    assert "\\coordinate (spyviewer) at (axis cs:0.5,-90);" in tikz
    assert (
        "\\spy[width=6cm, height=1cm] on (spypoint) in node [fill=white] at (spyviewer);"
        in tikz
    )

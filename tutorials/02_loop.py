from maxtikzlib.figure import TikzFigure

fig = TikzFigure()

origin = fig.add_node(
    -1,
    -1,
    label="origin",
    content="\color{white}O",
    shape="circle",
    fill="red",
    layer=1,
)

with fig.loop("i", range(5), layer=1) as loop:
    node = loop.add_node(
        "2.5*\i",
        -5.0,
        label="xnodes\i",
        content="\color{white}\i",
        shape="circle",
        fill="blue",
    )

with fig.loop("i", range(5), layer=0) as loop:
    loop.add_path(
        [origin, node],
        color="black",
        path_actions=["line width=2"],
    )

with fig.loop("i", range(5), layer=1) as loop_i:
    with loop_i.add_loop("j", range(3)) as loop_j:
        node = loop_j.add_node(
            "5*\i",
            "3*\j",
            label="xynodes\i\j",
            content=r"\color{white}\i,\j",
            shape="circle",
            fill="blue",
        )


with fig.loop("i", range(5), layer=3) as loop_i:
    with loop_i.add_loop("j", range(3)) as loop_j:
        loop_j.add_path(
            [origin, node],
            color="black",
            path_actions=["line width=3"],
        )

# print(fig.generate_standalone())
fig.compile_pdf(filename="loop.pdf")

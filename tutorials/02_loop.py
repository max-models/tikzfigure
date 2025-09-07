from maxtikzlib.figure import TikzFigure

fig = TikzFigure()

origin = fig.add_node(
    0,
    0,
    label="origin",
    content="\color{white}O",
    shape="circle",
    fill="red",
    layer=1,
)

with fig.loop("i", range(5), layer=1) as loop:
    node = loop.add_node(
        "5*\i",
        5.0,
        label="p\i",
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

# print(fig.generate_standalone())
fig.compile_pdf(filename="loop.pdf")

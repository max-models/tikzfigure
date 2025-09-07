from maxtikzlib.figure import TikzFigure

fig = TikzFigure()

num_xpoints = 5
num_ypoints = 3
dx = 2.5

origin = fig.add_node(
    ((num_xpoints - 1) / 2) * dx,
    -2.5,
    label="origin",
    content="\color{white}O",
    shape="circle",
    fill="red",
    comment="Origin node",
)

# Green nodes at the bottom
with fig.loop("i", range(num_xpoints), comment="Green nodes at the bottom") as loop:
    node = loop.add_node(
        f"{dx}*\i",
        -5.0,
        label="xnodes\i",
        content="\color{white}\i",
        shape="circle",
        fill="green!50!black",
    )

# Draw lines from origin to the bottom nodes
with fig.loop(
    "i", range(num_xpoints), comment="Lines from origin to green nodes"
) as loop:
    loop.add_path(
        [origin, node],
        color="black",
        path_actions=["line width=2"],
    )

# Draw the top node grid
with fig.loop("i", range(num_xpoints), comment="Blue nodegrid") as loop_i:
    with loop_i.add_loop("j", range(num_ypoints), comment="inner j-loop") as loop_j:
        node = loop_j.add_node(
            f"{dx}*\i",
            f"3*\j",
            label="xynodes\i\j",
            content=r"\color{white}\i,\j",
            shape="circle",
            fill="blue",
        )

# Lines from origin to blue node grid
with fig.loop(
    "i", range(num_xpoints), comment="Lines from origin to blue node grid"
) as loop_i:
    with loop_i.add_loop("j", range(num_ypoints), comment="inner j-loop") as loop_j:
        loop_j.add_path(
            [origin, node],
            color="black",
            path_actions=["line width=3"],
        )

print(fig.generate_standalone())
fig.compile_pdf(filename="loop.pdf")

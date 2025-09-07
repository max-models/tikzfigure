import numpy as np

from maxtikzlib.figure import TikzFigure

fig = TikzFigure()

path_actions = ["draw", "rounded corners=8pt", "line width=6"]
colors = ["purple", "blue", "purple"]

# M with thick tracing
nodes_M = [
    [0, 0],
    [0, 3.5],
    [1, 3.5],
    [1.25, 2.75],
    [1.5, 3.5],
    [2.5, 3.5],
    [2.5, 0],
    [2, 0],
    [2, 2.75],
    [1.25, 2.0],
    [0.5, 2.75],
    [0.5, 0],
]

fig.add_path(
    nodes_M,
    path_actions=path_actions,
    layer=0,
    cycle=True,
    color=colors[0],
    fill=f"{colors[0]}!50!white",
    comment="Path for M",
    center=True,
)

# T with thick tracing
nodes_T = [
    [3.125, 0],
    [3.125, 4],
    [0, 4],
    [0, 4.75],
    [7, 4.75],
    [7, 4],
    [3.875, 4],
    [3.875, 0],
]

fig.add_path(
    nodes_T,
    path_actions=path_actions,
    layer=0,
    cycle=True,
    color=colors[1],
    fill=f"{colors[1]}!50!white",
    comment="Path for T",
    center=True,
)

# L with thick tracing
nodes_L = [
    [4.5, 0],
    [4.5, 3.5],
    [5.25, 3.5],
    [5.25, 0.75],
    [7, 0.75],
    [7, 0],
]

fig.add_path(
    nodes_L,
    path_actions=path_actions,
    layer=2,
    cycle=True,
    color=colors[2],
    fill=f"{colors[2]}!50!white",
    comment="Path for L",
    center=True,
)

xvec = np.arange(0, 7, 0.1)
yvec = np.sin(xvec) * 0.25 + 1.25

nodes_line = [(x, y) for x, y in zip(xvec, yvec)]

fig.add_path(
    nodes_line,
    path_actions=path_actions,
    layer=1,
    color="black",
    comment="Sine wave path",
    center=True,
)

print(fig.generate_tikz())

fig.compile_pdf(filename="mtl_logo.pdf")

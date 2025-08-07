# running
# pip install git+https://github.com/max-models/maxtikzlib

from itertools import cycle

from scipy.fftpack import hilbert

from maxtikzlib.figure import Path, TikzFigure


def node_positions_to_path(tikz, node_positions, nodelabel, path_actions, layer=1):
    nodes = []
    for i, node_data in enumerate(node_positions):
        node = tikz.add_node(
            node_data[0],
            node_data[1],
            f"{nodelabel}{i}",
            layer=0,
            color="red",
            # content=f"Node {i}",
        )
        nodes.append(node)
    tikz.add_path(nodes, path_actions=path_actions, layer=layer)


def add_square(tikz, x0, y0, L, nodelabel, path_actions, layer=1):
    node_positions = [
        [x0, y0],
        [x0 + L, y0],
        [x0 + L, y0 + L],
        [x0, y0 + L],
        [x0, y0],
    ]
    node_positions_to_path(tikz, node_positions, nodelabel, path_actions, layer)


def draw_grid(tikz):

    # Level A
    add_square(
        tikz=tikz,
        x0=0,
        y0=0,
        L=8,
        nodelabel="LevelA",
        path_actions=["draw", "line width=2"],
        layer=4,
    )

    add_square(
        tikz=tikz,
        x0=0,
        y0=0,
        L=8,
        nodelabel="LevelBG",
        path_actions=["draw", "line width=0", "fill=yellow!10!white"],
        layer=0,
    )

    # # Level B
    # for x0 in [0, 4]:
    #     for y0 in [0, 4]:
    #         add_square(
    #             x0=x0,
    #             y0=y0,
    #             L=4,
    #             nodelabel=f"LevelB{x0}{y0}",
    #             path_actions=["draw", "line width=2", "color=red"],
    #             layer=3,
    #         )

    # Level C
    for x0 in [0, 2, 4, 6]:
        for y0 in [0, 2, 4, 6]:
            add_square(
                tikz=tikz,
                x0=x0,
                y0=y0,
                L=2,
                nodelabel=f"LevelC{x0}{y0}",
                path_actions=["draw", "line width=2", "color=blue"],
                layer=2,
            )

    # Level D
    for x0 in [4, 5, 6, 7]:
        for y0 in [2, 3, 4, 5]:
            add_square(
                tikz=tikz,
                x0=x0,
                y0=y0,
                L=1,
                nodelabel=f"LevelD{x0}{y0}",
                path_actions=[
                    "draw",
                    "line width=2",
                    "color=green!50!black",
                    "fill=green!10!white",
                ],
                layer=1,
            )

    # Level E
    for x0 in [5, 5.5]:
        for y0 in [3, 3.5]:
            add_square(
                tikz=tikz,
                x0=x0,
                y0=y0,
                L=0.5,
                nodelabel=f"LevelE{round(x0)}{round(y0)}",
                path_actions=[
                    "draw",
                    "line width=2",
                    "color=red!50!black",
                    "fill=red!10!white",
                ],
                layer=1,
            )


def draw_hilbert_curve():

    tikz = TikzFigure(figure_setup=">={{Triangle[scale=1]}}")

    draw_grid(tikz=tikz)
    hilbert_path = [
        [1, 1],
        [3, 1],
        [3, 3],
        [1, 3],
        [1, 7],
        [3, 7],
        [3, 5],
        [4.5, 4.5],
        [5.5, 4.5],
        [5.5, 5.5],
        [4.5, 5.5],
        [5, 7],
        [7, 7],
        [7.5, 5.5],
        [6.5, 5.5],
        [6.5, 4.5],
        [7.5, 4.5],
        [7.5, 2.5],
        [6.5, 2.5],
        [6.5, 3.5],
        [5.75, 3.75],
        [5.75, 3.25],
        [5.25, 3.25],
        [5.25, 3.75],
        [4.5, 3.5],
        [4.5, 2.5],
        [5.5, 2.5],
        [5, 1],
        [7, 1],
    ]
    for i in range(len(hilbert_path) - 1):
        path = [hilbert_path[i], hilbert_path[i + 1]]
        node_positions_to_path(
            tikz,
            path,
            nodelabel=f"ZPath{i}",
            path_actions=["->", "draw", "line width=1", "color=black"],
            layer=5,
        )
    with open("figure_hilbert.tikz", "w") as f:
        f.write(tikz.generate_tikz())
    with open("standalone_hilbert.tex", "w") as f:
        f.write(tikz.generate_standalone())
    # tikz.compile_pdf(filename='hilbert_curve.pdf')


def draw_z_curve():

    tikz = TikzFigure(figure_setup=">={{Triangle[scale=1]}}")

    draw_grid(tikz=tikz)
    z_path = [
        [1, 7],
        [3, 7],
        [1, 5],
        [3, 5],
        [5, 7],
        [7, 7],
        [4.5, 5.5],
        [5.5, 5.5],
        [4.5, 4.5],
        [5.5, 4.5],
        [6.5, 5.5],
        [7.5, 5.5],
        [6.5, 4.5],
        [7.5, 4.5],
        [1, 3],
        [3, 3],
        [1, 1],
        [3, 1],
        [4.5, 3.5],
        [5.25, 3.75],
        [5.75, 3.75],
        [5.25, 3.25],
        [5.75, 3.25],
        [4.5, 2.5],
        [5.5, 2.5],
        [6.5, 3.5],
        [7.5, 3.5],
        [6.5, 2.5],
        [7.5, 2.5],
        [5, 1],
        [7, 1],
    ]
    for i in range(len(z_path) - 1):
        path = [z_path[i], z_path[i + 1]]
        node_positions_to_path(
            tikz,
            path,
            nodelabel=f"ZPath{i}",
            path_actions=["->", "draw", "line width=1", "color=black"],
            layer=5,
        )
    with open("figure_z.tikz", "w") as f:
        f.write(tikz.generate_tikz())
    with open("standalone_z.tex", "w") as f:
        f.write(tikz.generate_standalone())

    # print(tikz.generate_standalone())

    # tikz.compile_pdf(filename='z_curve.pdf')


if __name__ == "__main__":
    draw_hilbert_curve()
    draw_z_curve()

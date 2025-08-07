from itertools import cycle

from scipy.fftpack import hilbert

from maxtikzlib.figure import Path, TikzFigure


def node_positions_to_path(tikz, node_positions, path_actions, layer=1):
    nodes = []
    for i, node_data in enumerate(node_positions):
        node = tikz.add_node(
            node_data[0],
            node_data[1],
            layer=0,
            color="red",
        )
        nodes.append(node)
    tikz.add_path(nodes, path_actions=path_actions, layer=layer)


def add_grid(tikz, x0, y0, L, N, path_actions, layer=1):
    x1 = x0 + L
    y1 = y0 + L
    delta = L / N
    node_positions = []

    for i in range(N + 1):

        # Horizontal line
        y = y0 + i * delta
        node_positions = [[x0, y], [x1, y]]
        node_positions_to_path(tikz, node_positions, path_actions, layer)

        # Vertical line
        x = x0 + i * delta
        node_positions = [[x, y0], [x, y1]]
        node_positions_to_path(tikz, node_positions, path_actions, layer)


def add_square(tikz, x0, y0, L, path_actions, layer=1):
    node_positions = [
        [x0, y0],
        [x0 + L, y0],
        [x0 + L, y0 + L],
        [x0, y0 + L],
        [x0, y0],
    ]
    node_positions_to_path(tikz, node_positions, path_actions, layer)


def draw_grid(tikz):

    # Add backgrounds
    add_square(
        tikz=tikz,
        x0=0,
        y0=0,
        L=8,
        path_actions=["draw", "line width=0", "fill=yellow!10!white"],
        layer=0,
    )

    add_square(
        tikz=tikz,
        x0=4,
        y0=2,
        L=4,
        path_actions=["draw", "line width=0", "fill=blue!10!white"],
        layer=1,
    )

    add_square(
        tikz=tikz,
        x0=5,
        y0=3,
        L=1,
        path_actions=["draw", "line width=0", "fill=red!10!white"],
        layer=2,
    )

    # Level A
    add_grid(
        tikz,
        x0=0,
        y0=0,
        L=8,
        N=4,
        path_actions=["draw", "line width=2", "color=black"],
        layer=3,
    )

    # Level B
    add_grid(
        tikz,
        x0=4,
        y0=2,
        L=4,
        N=4,
        path_actions=["draw", "line width=2", "color=blue"],
        layer=4,
    )

    # Level C
    add_grid(
        tikz,
        x0=5,
        y0=3,
        L=1.0,
        N=2,
        path_actions=["draw", "line width=2", "color=red"],
        layer=5,
    )


def draw_hilbert_curve(save=False):

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
            path_actions=["->", "draw", "line width=1", "color=black"],
            layer=6,
        )
    print(tikz.generate_tikz())

    if save:
        with open("figure_hilbert.tikz", "w") as f:
            f.write(tikz.generate_tikz())
        with open("standalone_hilbert.tex", "w") as f:
            f.write(tikz.generate_standalone())
        # tikz.compile_pdf(filename='hilbert_curve.pdf')


def draw_z_curve(save=False):

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
            path_actions=["->", "draw", "line width=1", "color=black"],
            layer=5,
        )
    print((tikz.generate_tikz()))
    if save:
        with open("figure_z.tikz", "w") as f:
            f.write(tikz.generate_tikz())
        with open("standalone_z.tex", "w") as f:
            f.write(tikz.generate_standalone())

    # print(tikz.generate_standalone())

    # tikz.compile_pdf(filename='z_curve.pdf')


if __name__ == "__main__":
    draw_hilbert_curve(save=True)
    draw_z_curve(save=True)

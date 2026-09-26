"""Example: Draw an adaptive quadtree with a color for each depth."""

from tikzfigure import TikzFigure


def main() -> None:
    fig = TikzFigure()

    # Children are ordered southwest, southeast, northwest, northeast.
    # None means that the corresponding quadrant is not subdivided.
    tree = {
        "sw": [None, None, None, None],
        "se": {
            "sw": None,
            "se": [None, None, None, None],
            "nw": None,
            "ne": None,
        },
        "nw": None,
        "ne": [None, None, None, None],
    }

    fig.add_quadtree(
        tree,
        bounds=(0, 0, 8, 8),
        level_colors=["black", "blue", "red"],
        line_width="0.8pt",
    )

    fig.show(use_web_compilation=True)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Generate the quickstart output figure shown on the home page.

Run from anywhere:
    python astro_docs/scripts/generate_quickstart.py
"""

from pathlib import Path

from tikzfigure import TikzFigure

OUT = Path(__file__).resolve().parent.parent / "public" / "quickstart" / "output.png"
OUT.parent.mkdir(parents=True, exist_ok=True)


def main() -> None:
    fig = TikzFigure()
    a = fig.add_node(
        0,
        0,
        content="A",
        shape="circle",
        fill="cyan!40",
    )
    b = fig.add_node(
        3,
        0,
        content="B",
        shape="circle",
        fill="cyan!40",
    )
    c = fig.add_node(
        0,
        -2,
        content="C",
        shape="circle",
        fill="cyan!40",
    )

    fig.draw([a, b], arrows="->")
    fig.draw([b, c], arrows="->")

    fig.savefig(str(OUT))

    print(fig)
    print(f"Saved → {OUT}")


if __name__ == "__main__":
    main()

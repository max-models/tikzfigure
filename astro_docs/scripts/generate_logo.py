#!/usr/bin/env python3
"""Generate the tikzfigure logo (simple node graph) using the library itself.

Run from root of the repository with:
    python astro_docs/scripts/generate_logo2.py
"""

from pathlib import Path

from tikzfigure import TikzFigure

OUT = Path(__file__).resolve().parent.parent / "src" / "assets" / "logo.png"


def main() -> None:
    fig = TikzFigure(figsize=(2.5, 2.5))

    # Background
    fig.add_raw(
        r"\fill[rounded corners=22pt, fill=blue!10!black]"
        r" (-2.6,-2.8) rectangle (2.6,2.8);",
        layer=0,
    )

    # Nodes
    opts = dict(
        draw="none",
        minimum_size="1.2cm",
        font=r"\bfseries\ttfamily",
        color="white",
        shape="circle",
        layer=1,
    )
    nA = fig.add_node(0.0, 2.0, fill="violet!70!blue", content="A", **opts)
    nB = fig.add_node(-1.7, 0.0, fill="cyan!80!blue", content="B", **opts)
    nC = fig.add_node(1.7, 0.0, fill="magenta!60!red", content="C", **opts)
    nD = fig.add_node(0.0, -2.0, fill="teal!70!green", content="D", **opts)

    # Edges
    for src, dst in [(nA, nB), (nA, nC), (nB, nD), (nC, nD)]:
        fig.draw(
            [src, dst],
            options=["-Stealth"],
            line_width="2pt",
            color="white",
        )
    # fig.show()
    fig.savefig(str(OUT))
    print(f"Saved → {OUT}")


if __name__ == "__main__":
    main()

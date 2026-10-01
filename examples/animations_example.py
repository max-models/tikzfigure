"""Example: PDF animations with the `animations` TikZ library.

Registers the `animations` library and uses `raw()` to attach `.animate`
directives to nodes, since tikzfigure has no dedicated animation object
model yet. The generated PDF animates in a compatible viewer (e.g. Adobe
Reader): the traffic light's fill fades to red, and the ball translates
to the right.
"""

from tikzfigure import TikzFigure


def main():
    fig = TikzFigure()
    fig.usetikzlibrary("animations")

    # Animate a node's fill color.
    traffic_light = fig.node(
        (0, 0),
        shape="circle",
        fill="orange",
        minimum_size="1cm",
    )
    fig.raw(
        f"\\tikzset{{{traffic_light.label}/.animate = {{fill = {{red}}}}}}",
    )

    # Animate a node moving along a path (a translation over 2 seconds).
    ball = fig.node(
        (0, -2.5),
        shape="circle",
        fill="blue!60",
        minimum_size="0.8cm",
    )
    fig.raw(
        f"\\tikzset{{{ball.label}/.animate = {{translate = {{{{(4,0)}}{{2s}}}}}}}}",
    )

    fig.savefig("animations.pdf", use_web_compilation=True)
    fig.show(use_web_compilation=True)


if __name__ == "__main__":
    main()

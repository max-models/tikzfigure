import math

from tikzpics import TikzFigure


def main():
    fig = TikzFigure()

    # Archimedean spiral: r = a + b*theta
    a = 0.0
    b = 0.08
    turns = 6
    steps = 600

    points = []
    for i in range(steps + 1):
        theta = (2 * math.pi * turns) * (i / steps)
        r = a + b * theta
        x = r * math.cos(theta)
        y = r * math.sin(theta)
        points.append((x, y))

    fig.draw(points, options=["thick", "blue"])

    fig.show()


if __name__ == "__main__":
    main()

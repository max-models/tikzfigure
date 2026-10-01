from tikzfigure import GanttChart, TikzFigure


def test_gantt_chart_renders_pgfgantt_rows_and_package():
    fig = TikzFigure()
    chart = fig.add_gantt_chart(
        1,
        6,
        options=["hgrid", "vgrid"],
        rows=[
            {"type": "titlelist", "content": "1,2,3,4,5,6"},
            {"type": "group", "content": "Planning", "start": 1, "end": 2},
            {
                "type": "bar",
                "content": "Design",
                "start": 1,
                "end": 2,
                "name": "design",
            },
            {"type": "milestone", "content": "Review", "at": 3, "name": "review"},
            {"type": "link", "source": "design", "target": "review"},
        ],
    )

    assert isinstance(chart, GanttChart)
    assert "pgfgantt" in fig.extra_packages
    tikz = fig.generate_tikz()
    assert r"\begin{ganttchart}[hgrid, vgrid]{1}{6}" in tikz
    assert r"\ganttbar[name=design]{Design}{1}{2}\\" in tikz
    assert r"\ganttlink{design}{review}" in tikz


def test_gantt_chart_round_trips():
    fig = TikzFigure()
    fig.gantt(1, 3).add_row("bar", content="Build", start=1, end=3)

    restored = TikzFigure.from_dict(fig.to_dict())

    assert restored.generate_tikz() == fig.generate_tikz()
    assert restored.extra_packages == ["pgfgantt"]

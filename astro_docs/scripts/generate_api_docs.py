from __future__ import annotations

import re
import textwrap
from pathlib import Path

try:
    from pydoc_markdown import PydocMarkdown
    from pydoc_markdown.contrib.loaders.python import PythonLoader
    from pydoc_markdown.contrib.processors.crossref import CrossrefProcessor
    from pydoc_markdown.contrib.processors.filter import FilterProcessor
    from pydoc_markdown.contrib.processors.smart import SmartProcessor
    from pydoc_markdown.contrib.renderers.markdown import MarkdownRenderer
except ImportError as exc:  # pragma: no cover - exercised in docs environments
    raise SystemExit(
        "pydoc-markdown is required to generate the Astro API docs. "
        'Install the docs dependencies first, for example with `pip install ".[docs]"`.'
    ) from exc

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
OUTPUT_PATH = ROOT / "astro_docs" / "src" / "content" / "docs" / "api.md"

SECTIONS: list[tuple[str, str, str]] = [
    ("Figure API", "from tikzfigure import TikzFigure", "tikzfigure.core.figure"),
    ("Node API", "from tikzfigure import Node", "tikzfigure.core.node"),
    (
        "Coordinates and vectors",
        "from tikzfigure import TikzCoordinate, TikzVector",
        "tikzfigure.core.coordinate",
    ),
    ("Colors", "from tikzfigure import colors", "tikzfigure.colors"),
    ("Units", "from tikzfigure import units", "tikzfigure.units"),
    ("Shapes", "from tikzfigure import shapes", "tikzfigure.shapes"),
    ("Styles", "from tikzfigure import styles", "tikzfigure.styles"),
    ("Arrows", "from tikzfigure import arrows", "tikzfigure.arrows"),
    ("Patterns", "from tikzfigure import patterns", "tikzfigure.patterns"),
    ("Decorations", "from tikzfigure import decorations", "tikzfigure.decorations"),
    ("Marks", "from tikzfigure import marks", "tikzfigure.marks"),
    ("Options", "from tikzfigure import options", "tikzfigure.options"),
]


def _render_module(module_name: str) -> str:
    renderer = MarkdownRenderer(
        render_page_title=False,
        render_toc=False,
        render_module_header=False,
        descriptive_class_title=False,
        add_module_prefix=False,
        add_method_class_prefix=True,
    )
    session = PydocMarkdown(
        loaders=[
            PythonLoader(
                modules=[module_name],
                search_path=[str(SRC_DIR)],
            )
        ],
        processors=[
            FilterProcessor(documented_only=True, exclude_private=True),
            SmartProcessor(),
            CrossrefProcessor(),
        ],
        renderer=renderer,
    )
    modules = session.load_modules()
    session.process(modules)
    return renderer.render_to_string(modules).strip()


def _normalize_rst_roles(markdown: str) -> str:
    return re.sub(r":[a-z]+:`~?([^`]+)`", r"`\1`", markdown)


def _bump_headings(markdown: str, levels: int = 1) -> str:
    lines = markdown.splitlines()
    in_fence = False
    adjusted: list[str] = []
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            adjusted.append(line)
            continue
        if not in_fence and stripped.startswith("#"):
            prefix_len = len(line) - len(stripped)
            hashes, rest = stripped.split(" ", 1)
            adjusted.append(f"{line[:prefix_len]}{'#' * levels}{hashes} {rest}")
            continue
        adjusted.append(line)
    return "\n".join(adjusted)


def _render_section(title: str, import_example: str, module_name: str) -> str:
    rendered = _render_module(module_name)
    rendered = _normalize_rst_roles(rendered)
    rendered = _bump_headings(rendered, 1)
    rendered = rendered.strip()

    if not rendered:
        raise RuntimeError(f"No API documentation was rendered for {module_name}.")

    return "\n".join(
        [
            f"## {title}",
            "",
            "```python",
            import_example,
            "```",
            "",
            rendered,
        ]
    ).strip()


def build_api_page() -> str:
    intro = textwrap.dedent(
        """\
        ---
        title: API Reference
        description: Generated reference for the current tikzfigure Python API.
        ---

        > This page is generated from the current Python docstrings by
        > `astro_docs/scripts/generate_api_docs.py`. Edit the docstrings in
        > `src/tikzfigure/`, not this file.

        The sections below follow the current public API surface exported from
        `tikzfigure`, plus the underlying modules that define the main public
        classes.
        """
    ).strip()

    sections = [
        _render_section(title=title, import_example=import_example, module_name=module)
        for title, import_example, module in SECTIONS
    ]
    return intro + "\n\n" + "\n\n".join(sections) + "\n"


def main() -> None:
    OUTPUT_PATH.write_text(build_api_page(), encoding="utf-8")
    print(f"API docs generated at {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

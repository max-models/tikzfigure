#!/usr/bin/env python3
"""Convert .qmd tutorials and .ipynb notebooks to Starlight-compatible markdown.

Run from anywhere:
    python astro_docs/scripts/build_tutorials.py
"""

import argparse
import os
import re
import shutil
import subprocess
import tempfile
from multiprocessing import Pool
from pathlib import Path

ASTRO_ROOT = Path(__file__).resolve().parent.parent
TUTORIALS_SRC = ASTRO_ROOT.parent / "tutorials"
CONTENT_DST = ASTRO_ROOT / "src" / "content" / "docs" / "tutorials"
PUBLIC_DST = ASTRO_ROOT / "public" / "tutorials"
BASE_PATH = "/tikzfigure"
# This is the tab for python code, do not use TAB from tikzfigure.core.constants
# since that is used for the tikz code and could change in the future.
TAB = "    "


def iter_tutorial_sources() -> list[Path]:
    """Return all tutorial sources in a stable order for sharding/building."""
    qmds = sorted(TUTORIALS_SRC.glob("*.qmd"))
    nbs = sorted(
        nb
        for nb in TUTORIALS_SRC.glob("*.ipynb")
        if ".ipynb_checkpoints" not in nb.parts
    )
    return sorted([*qmds, *nbs], key=lambda path: path.name)


def select_tutorial_shard(
    tutorials: list[Path], shard_count: int | None, shard_index: int | None
) -> list[Path]:
    """Return the subset of tutorials assigned to a shard."""
    if shard_count is None and shard_index is None:
        return tutorials
    if shard_count is None or shard_index is None:
        raise ValueError("shard_count and shard_index must be provided together.")
    if shard_count < 1:
        raise ValueError("shard_count must be at least 1.")
    if not 0 <= shard_index < shard_count:
        raise ValueError(
            f"shard_index must be between 0 and {shard_count - 1}, got {shard_index}."
        )
    return [
        tutorial
        for position, tutorial in enumerate(tutorials)
        if position % shard_count == shard_index
    ]


def extract_title(content: str, fallback: str) -> str:
    """Extract title from YAML frontmatter or first # heading."""
    fm_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if fm_match:
        title_match = re.search(
            r'^title:\s*["\']?(.*?)["\']?\s*$', fm_match.group(1), re.MULTILINE
        )
        if title_match:
            return title_match.group(1).strip()
    heading_match = re.search(r"^# (.+)$", content, re.MULTILINE)
    if heading_match:
        return heading_match.group(1).strip()
    return fallback


def strip_frontmatter(content: str) -> str:
    """Remove YAML frontmatter block and the leading # heading (Starlight renders the title from frontmatter)."""
    content = re.sub(r"^---\n.*?\n---\n?", "", content, flags=re.DOTALL).lstrip()
    content = re.sub(r"^#[^\n]+\n+", "", content)
    return content


def fix_image_paths(content: str, tutorial_name: str) -> str:
    """Rewrite relative image paths to absolute /tutorials/<name>/... paths.

    Quarto emits paths like ``<name>_files/figure-commonmark/foo.png``, but
    copy_assets() copies the *contents* of ``<name>_files/`` directly into
    ``public/tutorials/<name>/``, so the ``<name>_files/`` prefix must be
    stripped before building the final URL.

    Handles both markdown ``![alt](path)`` syntax and HTML ``<img src="path">``
    tags, since Quarto emits the latter for figures with width attributes.
    """

    files_prefix = f"{tutorial_name}_files/"

    def rewrite(path: str) -> str:
        if path.startswith(("http://", "https://", "/")):
            return path
        if path.startswith(files_prefix):
            path = path[len(files_prefix) :]
        return f"{BASE_PATH}/tutorials/{tutorial_name}/{path}"
        # return f"./{path}"

    def replace_md(m: re.Match[str]) -> str:
        alt, path = m.group(1), m.group(2)
        return f"![{alt}]({rewrite(path)})"

    def replace_img(m: re.Match[str]) -> str:
        return m.group(0).replace(m.group(1), rewrite(m.group(1)))

    content = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", replace_md, content)
    content = re.sub(r'<img\b[^>]*\bsrc="([^"]+)"', replace_img, content)
    return content


def fix_tikzcode_callouts(content: str) -> str:
    """Convert [[CALLOUT-*]] and [[TAB]] markers to JSX Astro components.

    Transforms:
        [[CALLOUT-NOTE START]] ... [[CALLOUT-NOTE END]]
            → <Callout type="note"> ... </Callout>

        ## heading markers within callouts become TabItem components
        Multiple ## sections create a <Tabs> wrapper
    """
    # Wrap tab groups in a collapsible section so code panes are hidden by default.
    content = content.replace(
        "`TABS_START`", "<details>\n<summary>Show Tikz code</summary>\n\n<Tabs>"
    )
    content = content.replace("`TABS_END`", "</Tabs>\n</details>")

    # Replace `TAB_START` and `TAB_END` with <Tab> and </Tab>
    # Get the label from the `TAB_START` marker, e.g. `TAB_START label="Section"`
    tab_start_pattern = r"`TAB_START\s+label=\"([^\"]+)\"`"
    content = re.sub(tab_start_pattern, r'<TabItem label="\1">', content)
    content = content.replace("`TAB_END`", "</TabItem>")

    return content


def fence_indented_output_blocks(content: str) -> str:
    """Convert top-level 4-space-indented blocks into fenced text code blocks."""
    lines = content.splitlines()
    out: list[str] = []
    i = 0
    in_fence = False

    while i < len(lines):
        line = lines[i]

        # Track whether we're inside a fenced code block
        if line.startswith("```"):
            in_fence = not in_fence
            out.append(line)
            i += 1
            continue

        prev_blank = i == 0 or lines[i - 1].strip() == ""

        # Only process indented blocks if we're NOT in a fence
        if line.startswith(TAB) and prev_blank and not in_fence:
            block: list[str] = []
            j = i
            while j < len(lines):
                current = lines[j]
                if current.startswith(TAB):
                    block.append(current[len(TAB) :])
                    j += 1
                    continue
                # Keep blank lines inside the block if followed by another
                # indented line, so one output becomes one fenced block.
                if (
                    current.strip() == ""
                    and j + 1 < len(lines)
                    and lines[j + 1].startswith(TAB)
                ):
                    block.append("")
                    j += 1
                    continue
                break

            out.append("```tex")
            out.extend(block)
            out.append("```")
            i = j
            continue

        out.append(line)
        i += 1

    rewritten = "\n".join(out)
    if content.endswith("\n"):
        rewritten += "\n"
    return rewritten


def write_content(title: str, body: str, out_path: Path) -> None:
    """Write MDX content with component imports if needed."""
    imports = ""
    if "<Callout" in body or "<TabItem" in body:
        imports = "import { Callout } from '@astrojs/starlight/components'\nimport { Tabs, TabItem } from '@astrojs/starlight/components'\n\n"

    content = f'---\ntitle: "{title}"\n---\n\n{imports}{body}'
    out_path.write_text(content, encoding="utf-8")
    print(f"  Written: {out_path.relative_to(ASTRO_ROOT)}")


def copy_assets(src_files_dir: Path, tutorial_name: str) -> None:
    if not src_files_dir.exists():
        return
    dst = PUBLIC_DST / tutorial_name
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src_files_dir, dst)


def process_qmd(qmd_path: Path) -> None:
    name = qmd_path.stem
    print(f"Rendering {qmd_path.name} ...")
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        # Copy the .qmd into its own isolated directory so concurrent Quarto
        # instances don't collide on project-level temp files in the source dir.
        work_dir = tmp_dir / "src"
        work_dir.mkdir()
        work_qmd = work_dir / qmd_path.name
        shutil.copy2(qmd_path, work_qmd)
        # Copy includes directory if it exists
        includes_src = TUTORIALS_SRC / "includes"
        includes_dst = work_dir / "includes"
        if includes_src.exists() and includes_src.is_dir():
            shutil.copytree(includes_src, includes_dst, dirs_exist_ok=True)
        out_dir = tmp_dir / "out"
        out_dir.mkdir()
        env = {**os.environ, "TMPDIR": tmp}
        subprocess.run(
            [
                "quarto",
                "render",
                str(work_qmd),
                "--to",
                "gfm",
                "--output-dir",
                str(out_dir),
            ],
            check=True,
            env=env,
        )
        md_file = out_dir / f"{name}.md"
        if not md_file.exists():
            print(f"  Warning: expected {md_file.name}, skipping")
            return

        content = md_file.read_text(encoding="utf-8")
        title = extract_title(content, name)
        body = fix_image_paths(strip_frontmatter(content), name)
        body = fix_tikzcode_callouts(body)
        body = fence_indented_output_blocks(body)
        copy_assets(out_dir / f"{name}_files", name)

    write_content(title, body, CONTENT_DST / f"{name}.mdx")


def process_notebook(nb_path: Path) -> None:
    name = nb_path.stem
    print(f"Converting {nb_path.name} ...")
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        subprocess.run(
            [
                "jupyter",
                "nbconvert",
                "--to",
                "markdown",
                "--execute",
                str(nb_path),
                "--output-dir",
                str(tmp_dir),
            ],
            check=True,
        )
        md_file = tmp_dir / f"{name}.md"
        if not md_file.exists():
            print(f"  Warning: expected {md_file.name}, skipping")
            return

        content = md_file.read_text(encoding="utf-8")
        title = extract_title(content, name)
        body = fix_image_paths(strip_frontmatter(content), name)
        body = fence_indented_output_blocks(body)
        copy_assets(tmp_dir / f"{name}_files", name)

    write_content(title, body, CONTENT_DST / f"{name}.mdx")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--serial", action="store_true", help="Process tutorials one at a time"
    )
    parser.add_argument(
        "--name",
        type=str,
        help="Process a specific tutorial by name (without extension)",
    )
    parser.add_argument(
        "--shard-count",
        type=int,
        help="Split tutorials into this many deterministic shards.",
    )
    parser.add_argument(
        "--shard-index",
        type=int,
        help="Process only one zero-based shard from --shard-count.",
    )
    args = parser.parse_args()

    CONTENT_DST.mkdir(parents=True, exist_ok=True)
    PUBLIC_DST.mkdir(parents=True, exist_ok=True)

    tutorials = iter_tutorial_sources()

    if args.name:
        tutorials = [tutorial for tutorial in tutorials if args.name in tutorial.stem]

    tutorials = select_tutorial_shard(tutorials, args.shard_count, args.shard_index)

    qmds = [tutorial for tutorial in tutorials if tutorial.suffix == ".qmd"]
    nbs = [tutorial for tutorial in tutorials if tutorial.suffix == ".ipynb"]

    if args.shard_count is not None and args.shard_index is not None:
        print(
            f"Processing shard {args.shard_index + 1}/{args.shard_count} "
            f"({len(tutorials)} tutorial(s))."
        )
    elif args.name:
        print(f"Processing {len(tutorials)} tutorial(s) matching {args.name!r}.")
    else:
        print(f"Processing {len(tutorials)} tutorial(s).")

    if args.serial:
        for qmd in qmds:
            process_qmd(qmd)
        for nb in nbs:
            process_notebook(nb)
    else:
        with Pool() as pool:
            pool.map(process_qmd, qmds)
            pool.map(process_notebook, nbs)

    print("Done.")


if __name__ == "__main__":
    main()

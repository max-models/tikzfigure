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

    def replace_md(m: re.Match) -> str:
        alt, path = m.group(1), m.group(2)
        return f"![{alt}]({rewrite(path)})"

    def replace_img(m: re.Match) -> str:
        return m.group(0).replace(m.group(1), rewrite(m.group(1)))

    content = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", replace_md, content)
    content = re.sub(r'<img\b[^>]*\bsrc="([^"]+)"', replace_img, content)
    return content


def write_content(title: str, body: str, out_path: Path) -> None:
    out_path.write_text(f'---\ntitle: "{title}"\n---\n\n{body}', encoding="utf-8")
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
        copy_assets(out_dir / f"{name}_files", name)

    write_content(title, body, CONTENT_DST / f"{name}.md")


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
        copy_assets(tmp_dir / f"{name}_files", name)

    write_content(title, body, CONTENT_DST / f"{name}.md")


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
    args = parser.parse_args()

    CONTENT_DST.mkdir(parents=True, exist_ok=True)
    PUBLIC_DST.mkdir(parents=True, exist_ok=True)

    qmds = sorted(TUTORIALS_SRC.glob("*.qmd"))
    nbs = sorted(
        nb
        for nb in TUTORIALS_SRC.glob("*.ipynb")
        if ".ipynb_checkpoints" not in nb.parts
    )

    if args.name:
        qmds = [qmd for qmd in qmds if args.name in qmd.stem]
        nbs = [nb for nb in nbs if args.name in nb.stem]

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

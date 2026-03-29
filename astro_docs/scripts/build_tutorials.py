#!/usr/bin/env python3
"""Convert .qmd tutorials and .ipynb notebooks to Starlight-compatible markdown.

Run from anywhere:
    python astro_docs/scripts/build_tutorials.py
"""

import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ASTRO_ROOT = Path(__file__).resolve().parent.parent
TUTORIALS_SRC = ASTRO_ROOT.parent / "tutorials"
CONTENT_DST = ASTRO_ROOT / "src" / "content" / "docs" / "tutorials"
PUBLIC_DST = ASTRO_ROOT / "public" / "tutorials"
BASE_PATH = "/tikzpics"


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
        subprocess.run(
            [
                "quarto",
                "render",
                str(qmd_path),
                "--to",
                "gfm",
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
    CONTENT_DST.mkdir(parents=True, exist_ok=True)
    PUBLIC_DST.mkdir(parents=True, exist_ok=True)

    for qmd in sorted(TUTORIALS_SRC.glob("*.qmd")):
        process_qmd(qmd)

    for nb in sorted(TUTORIALS_SRC.glob("*.ipynb")):
        if ".ipynb_checkpoints" not in nb.parts:
            process_notebook(nb)

    print("Done.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Convert .qmd tutorials and .ipynb notebooks to Starlight-compatible markdown.

Run from the repo root:
    python docs/scripts/build_tutorials.py
"""

import re
import shutil
import subprocess
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
TUTORIALS_SRC = REPO_ROOT / "tutorials"
CONTENT_DST = REPO_ROOT / "docs" / "src" / "content" / "docs" / "tutorials"
PUBLIC_DST = REPO_ROOT / "docs" / "public" / "tutorials"


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
    """Remove YAML frontmatter block."""
    return re.sub(r"^---\n.*?\n---\n?", "", content, flags=re.DOTALL).lstrip()


def fix_image_paths(content: str, tutorial_name: str) -> str:
    """Rewrite relative image paths to absolute /tutorials/<name>/... paths."""

    def replace(m: re.Match) -> str:
        alt, path = m.group(1), m.group(2)
        if path.startswith(("http://", "https://", "/")):
            return m.group(0)
        return f"![{alt}](/tutorials/{tutorial_name}/{path})"

    return re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", replace, content)


def write_content(title: str, body: str, out_path: Path) -> None:
    out_path.write_text(f'---\ntitle: "{title}"\n---\n\n{body}', encoding="utf-8")
    print(f"  Written: {out_path.relative_to(REPO_ROOT)}")


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

import subprocess
from pathlib import Path


def on_pre_build(config):
    import shutil

    tutorials_src = Path("tutorials")
    tutorials_dst = Path("docs/tutorials")
    if tutorials_src.exists():
        tutorials_dst.mkdir(exist_ok=True)
        for qmd in tutorials_src.glob("*.qmd"):
            subprocess.run(
                [
                    "quarto",
                    "render",
                    str(qmd),
                    "--to",
                    "gfm",
                    "--output-dir",
                    str(tutorials_dst.resolve()),
                ],
                check=True,
            )
        for nb in tutorials_src.glob("*.ipynb"):
            shutil.copy(nb, tutorials_dst / nb.name)

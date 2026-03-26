import shutil
from pathlib import Path


def on_pre_build(config):
    tutorials_src = Path("tutorials")
    tutorials_dst = Path("docs/tutorials")
    if tutorials_src.exists():
        tutorials_dst.mkdir(exist_ok=True)
        for nb in tutorials_src.glob("*.ipynb"):
            shutil.copy2(nb, tutorials_dst / nb.name)

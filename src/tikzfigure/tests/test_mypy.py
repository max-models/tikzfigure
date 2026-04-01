"""Type checking tests using mypy."""

import subprocess
from pathlib import Path


def test_mypy_build_tutorials():
    """Verify build_tutorials.py passes mypy type checking."""
    build_tutorials = (
        Path(__file__).resolve().parent.parent.parent.parent
        / "astro_docs"
        / "scripts"
        / "build_tutorials.py"
    )
    assert build_tutorials.exists(), (
        f"build_tutorials.py not found at {build_tutorials}"
    )

    result = subprocess.run(
        ["mypy", str(build_tutorials)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"mypy failed:\n{result.stdout}\n{result.stderr}"


if __name__ == "__main__":
    test_mypy_build_tutorials()
    print("mypy check passed!")

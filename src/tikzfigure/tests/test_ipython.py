"""Tests for IPython magic commands."""

import pytest

pytest.importorskip("IPython")

from IPython.testing.globalipapp import start_ipython


@pytest.fixture(scope="session")
def session_ip():
    """Start IPython session for testing.

    Skips if IPython singleton is already initialized with an incompatible shell.
    """
    try:
        return start_ipython()
    except Exception as e:
        # If IPython shell singleton is already initialized with a different type,
        # skip these tests since we already have good coverage from test_coverage_edge_cases.py
        if "MultipleInstanceError" in str(
            type(e).__name__
        ) or "incompatible sibling" in str(e):
            pytest.skip(f"IPython shell singleton already initialized: {e}")
        raise


@pytest.fixture(scope="function")
def ip(session_ip):
    """Get IPython instance and clean up after each test."""
    if session_ip is None:
        pytest.skip("IPython shell not available")
    yield session_ip
    # Clean up any loaded extensions
    try:
        session_ip.run_line_magic("unload_ext", "tikzfigure")
    except Exception:
        pass


def test_load_extension(ip):
    """Test that the extension loads without errors."""
    ip.run_line_magic("load_ext", "tikzfigure")

    # Check that the magic commands are registered
    assert "tikz" in ip.magics_manager.magics["cell"]
    assert "tikz_load" in ip.magics_manager.magics["line"]


def test_tikz_magic_simple(ip):
    """Test basic tikz magic with simple figure."""
    ip.run_line_magic("load_ext", "tikzfigure")

    tikz_code = r"""
\begin{tikzpicture}
\draw (0,0) -- (1,1);
\end{tikzpicture}
"""

    # This should not raise an error
    try:
        ip.run_cell_magic("tikz", "", tikz_code)
    except Exception as e:
        pytest.fail(f"tikz magic failed with error: {e}")


def test_tikz_magic_with_save(ip, tmp_path):
    """Test tikz magic with save option."""
    ip.run_line_magic("load_ext", "tikzfigure")

    tikz_code = r"""
\begin{tikzpicture}
\draw[fill=red] (0,0) circle (1cm);
\end{tikzpicture}
"""

    output_file = tmp_path / "test_output.png"

    # Run with save option
    ip.run_cell_magic("tikz", f"--save {output_file}", tikz_code)

    # Check that file was created
    assert output_file.exists()
    assert output_file.stat().st_size > 0


def test_tikz_magic_with_pdf_save(ip, tmp_path):
    """Test tikz magic saving to PDF."""
    ip.run_line_magic("load_ext", "tikzfigure")

    tikz_code = r"""
\begin{tikzpicture}
\node[draw] {Test};
\end{tikzpicture}
"""

    output_file = tmp_path / "test_output.pdf"

    # Run with save option
    ip.run_cell_magic("tikz", f"--save {output_file}", tikz_code)

    # Check that PDF file was created
    assert output_file.exists()
    assert output_file.stat().st_size > 0


def test_tikz_load_magic(ip, tmp_path):
    """Test tikz_load magic command."""
    ip.run_line_magic("load_ext", "tikzfigure")

    # Create a test tikz file
    tikz_file = tmp_path / "test.tikz"
    tikz_code = r"""
\begin{tikzpicture}
\draw (0,0) rectangle (2,2);
\end{tikzpicture}
"""
    tikz_file.write_text(tikz_code)

    # Load and render
    try:
        ip.run_line_magic("tikz_load", str(tikz_file))
    except Exception as e:
        pytest.fail(f"tikz_load magic failed with error: {e}")


def test_tikz_magic_error_handling(ip):
    """Test that invalid tikz code produces appropriate errors."""
    ip.run_line_magic("load_ext", "tikzfigure")

    # Invalid tikz code
    invalid_tikz = r"""
\begin{tikzpicture}
\invalid_command
\end{tikzpicture}
"""

    # Should handle error gracefully (not crash)
    # The magic catches exceptions and prints them
    ip.run_cell_magic("tikz", "", invalid_tikz)


def test_unload_extension(ip):
    """Test that the extension unloads without errors."""
    ip.run_line_magic("load_ext", "tikzfigure")

    # Check that magics are loaded
    assert "tikz" in ip.magics_manager.magics["cell"]
    assert "tikz_load" in ip.magics_manager.magics["line"]

    ip.run_line_magic("unload_ext", "tikzfigure")

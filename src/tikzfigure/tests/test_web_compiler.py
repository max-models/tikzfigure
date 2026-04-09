"""Tests for web-based LaTeX compilation via latex-on-http API."""

import subprocess
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

requests = pytest.importorskip("requests")

from tikzfigure.core.web_compiler import compile_with_latex_on_http


class TestWebCompiler:
    """Test suite for compile_with_latex_on_http function."""

    def test_compile_with_latex_on_http_success(self):
        """Test successful compilation with 200 response and PDF content."""
        latex_content = r"\documentclass{article}\begin{document}Hello\end{document}"

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "output.pdf"

            # Mock successful response with valid PDF magic bytes
            # API returns 201 Created on success
            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.content = b"%PDF-1.4\nPDF_CONTENT_HERE"

            with patch("requests.post") as mock_post:
                mock_post.return_value = mock_response

                # Should not raise any exception
                compile_with_latex_on_http(latex_content, output_path)

                # Verify the file was written
                assert output_path.exists()
                assert output_path.read_bytes() == b"%PDF-1.4\nPDF_CONTENT_HERE"

                # Verify the correct endpoint was called
                mock_post.assert_called_once()
                call_args = mock_post.call_args
                assert call_args[0][0] == "https://latex.ytotech.com/builds/sync"

                # Verify the JSON body format
                json_body = call_args[1]["json"]
                assert json_body["compiler"] == "pdflatex"
                assert "resources" in json_body
                assert len(json_body["resources"]) == 1
                assert json_body["resources"][0]["main"] is True
                assert json_body["resources"][0]["content"] == latex_content

    def test_compile_with_latex_on_http_failure(self):
        """Test handling of 400 error response."""
        latex_content = r"\documentclass{article}\begin{document}Hello\end{document}"

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "output.pdf"

            # Mock error response
            mock_response = MagicMock()
            mock_response.status_code = 400
            mock_response.text = "Bad Request: Invalid LaTeX"

            with patch("requests.post") as mock_post:
                mock_post.return_value = mock_response

                # Should raise RuntimeError
                with pytest.raises(RuntimeError) as exc_info:
                    compile_with_latex_on_http(latex_content, output_path)

                assert "HTTP error" in str(exc_info.value).lower() or "400" in str(
                    exc_info.value
                )

    def test_compile_with_latex_on_http_network_error(self):
        """Test handling of network errors (RequestException)."""
        latex_content = r"\documentclass{article}\begin{document}Hello\end{document}"

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "output.pdf"

            # Mock network error
            with patch("requests.post") as mock_post:
                mock_post.side_effect = requests.ConnectionError("Connection timeout")

                # Should raise RuntimeError
                with pytest.raises(RuntimeError) as exc_info:
                    compile_with_latex_on_http(latex_content, output_path)

                assert (
                    "network" in str(exc_info.value).lower()
                    or "timeout" in str(exc_info.value).lower()
                )

    def test_compile_pdf_explicit_web_compilation(self, tmp_path):
        """Test compile_pdf() with explicit use_web_compilation=True."""
        from tikzfigure import TikzFigure

        fig = TikzFigure()
        fig.add_node("test", content="Test Node")

        output_pdf = tmp_path / "test_output.pdf"

        # Mock subprocess.run and requests.post
        with (
            patch("subprocess.run") as mock_subprocess,
            patch("requests.post") as mock_post,
        ):
            # Mock the web compiler response with valid PDF magic bytes
            # API returns 201 Created on success
            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.content = b"%PDF-1.4\nPDF_CONTENT_HERE"
            mock_post.return_value = mock_response

            # Call compile_pdf with use_web_compilation=True
            fig.compile_pdf(filename=output_pdf, use_web_compilation=True)

            # Verify requests.post was called (web API used)
            mock_post.assert_called_once()
            # Verify subprocess.run was NOT called (didn't use pdflatex)
            mock_subprocess.assert_not_called()
            # Verify the output file was created
            assert output_pdf.exists()

    def test_compile_pdf_with_web_fallback(self, tmp_path):
        """Test compile_pdf() falls back to web API when pdflatex fails."""
        from tikzfigure import TikzFigure

        fig = TikzFigure()
        fig.add_node("test", content="Test Node")

        output_pdf = tmp_path / "test_output.pdf"

        # Mock subprocess.run and requests.post
        with (
            patch("subprocess.run") as mock_subprocess,
            patch("requests.post") as mock_post,
        ):
            # Mock subprocess failure (pdflatex not available)
            mock_subprocess.side_effect = subprocess.CalledProcessError(1, "pdflatex")

            # Mock the web compiler response
            # API returns 201 Created on success
            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.content = b"%PDF-1.4\nPDF_CONTENT_HERE"
            mock_post.return_value = mock_response

            # Call compile_pdf without use_web_compilation (should still succeed via fallback)
            fig.compile_pdf(filename=output_pdf, use_web_compilation=False)

            # Verify subprocess.run was called first (attempted pdflatex)
            mock_subprocess.assert_called_once()
            # Verify requests.post was called (fell back to web API)
            mock_post.assert_called_once()
            # Verify the output file was created
            assert output_pdf.exists()

    def test_compile_pdf_fallback_pdflatex_not_found(self, tmp_path):
        """Test compile_pdf() falls back to web API when pdflatex is not installed (FileNotFoundError)."""
        from tikzfigure import TikzFigure

        fig = TikzFigure()
        fig.add_node("test", content="Test Node")

        output_pdf = tmp_path / "test_output.pdf"

        # Mock subprocess.run and requests.post
        with (
            patch("subprocess.run") as mock_subprocess,
            patch("requests.post") as mock_post,
        ):
            # Mock FileNotFoundError (pdflatex not installed)
            mock_subprocess.side_effect = FileNotFoundError("pdflatex not found")

            # Mock the web compiler response
            # API returns 201 Created on success
            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.content = b"%PDF-1.4\nPDF_CONTENT_HERE"
            mock_post.return_value = mock_response

            # Call compile_pdf without use_web_compilation (should still succeed via fallback)
            fig.compile_pdf(filename=output_pdf, use_web_compilation=False)

            # Verify subprocess.run was called first (attempted pdflatex)
            mock_subprocess.assert_called_once()
            # Verify requests.post was called (fell back to web API)
            mock_post.assert_called_once()
            # Verify the output file was created
            assert output_pdf.exists()

    def test_savefig_pdf_with_web_compilation(self, tmp_path):
        """Test savefig() passes use_web_compilation through to compile_pdf()."""
        from tikzfigure import TikzFigure

        fig = TikzFigure()
        fig.add_node("test", content="Test Node")

        output_pdf = tmp_path / "test_output.pdf"

        # Mock compile_pdf to verify it's called with use_web_compilation=True
        with patch.object(fig, "compile_pdf") as mock_compile:
            # Call savefig with use_web_compilation=True
            fig.savefig(filename=output_pdf, use_web_compilation=True)

            # Verify compile_pdf was called with use_web_compilation=True
            mock_compile.assert_called_once()
            call_kwargs = mock_compile.call_args[1]
            assert call_kwargs.get("use_web_compilation") is True

    def test_show_with_web_compilation(self, tmp_path):
        """Test show() accepts and passes use_web_compilation parameter through to savefig()."""
        from tikzfigure import TikzFigure

        fig = TikzFigure()
        fig.add_node("test", content="Test Node")

        # Mock the backend display method and os.environ to prevent actual display
        with (
            patch.object(fig, "_show_matplotlib") as mock_backend,
            patch("os.environ.get", return_value=None),
        ):
            # Call show with use_web_compilation=True
            fig.show(backend="matplotlib", use_web_compilation=True)

            # Verify the backend was called with use_web_compilation=True
            mock_backend.assert_called_once()
            call_kwargs = mock_backend.call_args[1]
            assert call_kwargs.get("use_web_compilation") is True

    def test_end_to_end_web_compilation(self, tmp_path):
        """Test end-to-end web compilation with a simple figure."""
        from tikzfigure import TikzFigure

        # Create a simple figure with two nodes and a path
        fig = TikzFigure()
        fig.add_node(label="node1", x=0, y=0, content="Start")
        fig.add_node(label="node2", x=2, y=0, content="End")
        fig.draw(["node1", "node2"])

        output_pdf = tmp_path / "simple_figure.pdf"

        # Mock the web API response
        # API returns 201 Created on success
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.content = b"%PDF-1.4\nMock PDF content"

        with patch("requests.post") as mock_post:
            mock_post.return_value = mock_response

            # Call savefig with use_web_compilation=True
            fig.savefig(filename=output_pdf, use_web_compilation=True)

            # Verify requests.post was called (web API used)
            mock_post.assert_called_once()
            call_args = mock_post.call_args

            # Verify the correct endpoint was called
            assert call_args[0][0] == "https://latex.ytotech.com/builds/sync"

            # Verify the output file was created and contains PDF content
            assert output_pdf.exists()
            content = output_pdf.read_bytes()
            assert content == b"%PDF-1.4\nMock PDF content"

    def test_web_compilation_with_complex_figure(self, tmp_path):
        """Test web compilation with a more complex figure (grid of nodes)."""
        from tikzfigure import TikzFigure

        # Create a more complex figure with a 3x3 grid of nodes
        fig = TikzFigure()
        for i in range(3):
            for j in range(3):
                node_id = f"node_{i}_{j}"
                fig.add_node(label=node_id, x=i, y=j, content=f"({i},{j})")

        # Connect some nodes to create paths
        fig.draw(["node_0_0", "node_1_0", "node_2_0"])
        fig.draw(["node_0_1", "node_1_1", "node_2_1"])
        fig.draw(["node_0_2", "node_1_2", "node_2_2"])

        output_pdf = tmp_path / "complex_figure.pdf"

        # Mock the web API response
        # API returns 201 Created on success
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.content = b"%PDF-1.4\nMock PDF content for complex figure"

        with patch("requests.post") as mock_post:
            mock_post.return_value = mock_response

            # Call compile_pdf with use_web_compilation=True
            fig.compile_pdf(filename=output_pdf, use_web_compilation=True)

            # Verify requests.post was called
            mock_post.assert_called_once()
            call_args = mock_post.call_args

            # Verify the correct endpoint was called
            assert call_args[0][0] == "https://latex.ytotech.com/builds/sync"

            # Verify LaTeX content was sent in JSON body
            json_body = call_args[1]["json"]
            assert json_body["compiler"] == "pdflatex"
            latex_text = json_body["resources"][0]["content"]

            # Verify required TikZ directives are in the LaTeX
            assert r"\documentclass" in latex_text
            assert r"\begin{document}" in latex_text
            assert r"\begin{tikzpicture}" in latex_text
            assert r"\end{tikzpicture}" in latex_text
            assert r"\end{document}" in latex_text

            # Verify nodes are defined in the LaTeX
            assert "node_0_0" in latex_text
            assert "node_1_1" in latex_text
            assert "node_2_2" in latex_text

            # Verify the output PDF file was created
            assert output_pdf.exists()
            content = output_pdf.read_bytes()
            assert content == b"%PDF-1.4\nMock PDF content for complex figure"

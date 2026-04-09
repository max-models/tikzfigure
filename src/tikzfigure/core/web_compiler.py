"""Web-based LaTeX compilation via latex-on-http API."""

import json
from pathlib import Path
from typing import Union


def compile_with_latex_on_http(
    latex_content: str,
    output_path: Union[Path, str],
    timeout: int = 30,
    verbose: bool = False,
) -> None:
    """
    Compile LaTeX code to PDF using the latex-on-http API (latex.ytotech.com).

    Sends LaTeX content to https://latex.ytotech.com/builds/sync with JSON body
    containing compiler (pdflatex) and resources (LaTeX content).

    Args:
        latex_content: The LaTeX code to compile as a string.
        output_path: Path where the compiled PDF should be saved.
        timeout: Request timeout in seconds (default: 30).
        verbose: Whether to print verbose output (default: False).

    Raises:
        RuntimeError: If compilation fails or network error occurs.
        ImportError: If requests package is not installed.
    """
    try:
        import requests
    except ImportError:
        raise ImportError(
            "The 'requests' package is required for web-based compilation. "
            "Install with: pip install requests"
        ) from None

    output_path = Path(output_path)

    # Create parent directories if needed
    output_path.parent.mkdir(parents=True, exist_ok=True)

    url = "https://latex.ytotech.com/builds/sync"

    try:
        if verbose:
            print(f"Compiling LaTeX via {url}...")

        # Prepare JSON body with correct API format
        request_body = {
            "compiler": "pdflatex",
            "resources": [
                {
                    "main": True,
                    "content": latex_content,
                }
            ],
        }

        # Send LaTeX to the API as JSON
        response = requests.post(
            url,
            json=request_body,
            timeout=timeout,
        )

        # Check for HTTP errors (API returns 200 or 201 on success)
        if response.status_code in (200, 201):
            # Validate we got a PDF, not an error log
            if not response.content.startswith(b"%PDF"):
                # API returned error log as 200/201 response
                error_text = response.content.decode("utf-8", errors="replace")[:500]
                raise RuntimeError(
                    f"LaTeX compilation failed on server. Server response:\n{error_text}"
                )

            # Write the PDF to the output file
            output_path.write_bytes(response.content)

            if verbose:
                print(f"Successfully compiled to {output_path}")
        else:
            raise RuntimeError(f"HTTP error {response.status_code}: {response.text}")

    except requests.RequestException as e:
        raise RuntimeError(f"Network error during LaTeX compilation: {e}") from e

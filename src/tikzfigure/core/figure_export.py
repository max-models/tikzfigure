from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any


class FigureExportMixin:
    def _resolve_use_web_compilation(self, use_web_compilation: bool) -> bool:
        raise NotImplementedError

    def _check(self, output_unit: str | None = None) -> Any:
        raise NotImplementedError

    def generate_standalone(
        self,
        skip_header: bool = False,
        verbose: bool = False,
        output_unit: str | None = None,
    ) -> str:
        raise NotImplementedError

    def generate_tikz(
        self,
        use_layers: bool = True,
        skip_header: bool = False,
        verbose: bool = False,
        output_unit: str | None = None,
    ) -> str:
        raise NotImplementedError

    def _run_optional_check(
        self, check: bool = False, output_unit: str | None = None
    ) -> None:
        if not check:
            return
        try:
            self._check(output_unit=output_unit)
        except Exception as exc:
            print(f"Warning: TikzFigure._check() failed: {exc}")

    def compile_pdf(
        self,
        filename: Path | str = Path("output.pdf"),
        verbose: bool = False,
        use_web_compilation: bool = False,
        output_unit: str | None = None,
        check: bool = False,
    ) -> None:
        if isinstance(filename, str):
            filename = Path(filename)

        use_web_compilation = self._resolve_use_web_compilation(use_web_compilation)
        self._run_optional_check(check=check, output_unit=output_unit)
        latex_document = self.generate_standalone(output_unit=output_unit)
        if verbose:
            print(latex_document)

        if use_web_compilation:
            from tikzfigure.core.web_compiler import compile_with_latex_on_http

            compile_with_latex_on_http(latex_document, filename, verbose=verbose)
            return

        with tempfile.TemporaryDirectory() as tempdir:
            tex_file = Path(tempdir) / "figure.tex"
            with open(tex_file, "w") as f:
                f.write(latex_document)
            try:
                head_tail = (str(filename.parent), filename.name)

                output_directory = head_tail[0]
                jobname = head_tail[1].replace(".pdf", "")
                cmd = [
                    "pdflatex",
                    "-interaction=nonstopmode",
                    "-jobname",
                    f"{jobname}",
                    "-output-directory",
                    f"{output_directory}",
                    str(tex_file),
                ]
                if verbose:
                    print(f"{cmd =}")
                subprocess.run(
                    cmd,
                    cwd=tempdir,
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                os.remove(filename.with_suffix(".aux"))
                os.remove(filename.with_suffix(".log"))
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                if verbose:
                    if isinstance(e, FileNotFoundError):
                        print(
                            "pdflatex not available or compilation failed, attempting fallback to web API"
                        )
                    else:
                        print(
                            "Local pdflatex compilation failed, attempting fallback to web API..."
                        )
                        if e.stderr:
                            print(e.stderr.decode())
                        else:
                            print(str(e))

                from tikzfigure.core.web_compiler import compile_with_latex_on_http

                try:
                    compile_with_latex_on_http(
                        latex_document, filename, verbose=verbose
                    )
                except RuntimeError as web_error:
                    print("An error occurred while compiling the LaTeX document:")
                    if isinstance(e, subprocess.CalledProcessError):
                        if e.stderr:
                            print(e.stderr.decode())
                        else:
                            print(str(e))
                    elif isinstance(e, FileNotFoundError):
                        print(f"pdflatex not found: {str(e)}")
                    print(f"\nWeb compilation also failed: {str(web_error)}")
                    raise RuntimeError(
                        f"Local compilation failed. Web compilation fallback also failed: {str(web_error)}"
                    ) from web_error

    def savefig(
        self,
        filename: Path | str,
        dpi: int = 300,
        verbose: bool = False,
        transparent: bool = True,
        use_web_compilation: bool = False,
        output_unit: str | None = None,
        check: bool = False,
    ) -> None:
        if isinstance(filename, str):
            filename = Path(filename)

        use_web_compilation = self._resolve_use_web_compilation(use_web_compilation)
        self._run_optional_check(check=check, output_unit=output_unit)
        ext = filename.suffix.lower()

        if ext == ".pdf":
            compile_pdf_kwargs: dict[str, Any] = {
                "filename": filename,
                "verbose": verbose,
                "use_web_compilation": use_web_compilation,
            }
            if output_unit is not None:
                compile_pdf_kwargs["output_unit"] = output_unit
            self.compile_pdf(**compile_pdf_kwargs)
        elif ext == ".tikz":
            if verbose:
                print(f"Saving TikZ code to {filename}")
            tikz_code = self.generate_tikz(output_unit=output_unit)
            with open(filename, "w") as f:
                f.write(tikz_code)
        elif ext in [".png", ".jpg", ".jpeg"]:
            import fitz

            with tempfile.TemporaryDirectory() as tempdir:
                temp_pdf = Path(tempdir) / "temp.pdf"

                if verbose:
                    print(f"Compiling TikZ to temporary PDF: {temp_pdf}")

                raster_compile_pdf_kwargs: dict[str, Any] = {
                    "filename": temp_pdf,
                    "verbose": verbose,
                    "use_web_compilation": use_web_compilation,
                }
                if output_unit is not None:
                    raster_compile_pdf_kwargs["output_unit"] = output_unit
                self.compile_pdf(**raster_compile_pdf_kwargs)

                if verbose:
                    print(f"Converting {temp_pdf} → {filename}")

                doc = fitz.open(temp_pdf)
                page = doc[0]
                use_alpha = transparent and ext == ".png"
                pix = page.get_pixmap(dpi=dpi, alpha=use_alpha)
                pix.save(filename)
                doc.close()
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    def _show_matplotlib(
        self,
        dpi: int = 300,
        verbose: bool = False,
        transparent: bool = True,
        use_web_compilation: bool = False,
        output_unit: str | None = None,
    ) -> None:
        try:
            import matplotlib.image as mpimg
            import matplotlib.pyplot as plt
        except ImportError:
            raise ImportError(
                "matplotlib is required for this backend. "
                "Install with: pip install matplotlib\n"
                "Or use backend='system' or backend='pillow'"
            )

        if verbose:
            print("Using matplotlib backend for display.")

        with tempfile.TemporaryDirectory() as tempdir:
            temp_png = Path(tempdir) / "temp.png"
            savefig_kwargs: dict[str, Any] = {
                "filename": temp_png,
                "dpi": dpi,
                "verbose": verbose,
                "use_web_compilation": use_web_compilation,
            }
            if output_unit is not None:
                savefig_kwargs["output_unit"] = output_unit
            self.savefig(**savefig_kwargs)

            img = mpimg.imread(temp_png)
            height_width_ratio = img.shape[0] / img.shape[1]

            fig, ax = plt.subplots(figsize=(10, 10 * height_width_ratio))
            ax.imshow(img)
            ax.axis("off")
            plt.tight_layout(pad=0)
            plt.show()

    def _show_system(
        self,
        dpi: int = 300,
        transparent: bool = True,
        verbose: bool = False,
        use_web_compilation: bool = False,
        output_unit: str | None = None,
    ) -> None:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            temp_path = tmp.name

        try:
            savefig_kwargs: dict[str, Any] = {
                "filename": temp_path,
                "dpi": dpi,
                "transparent": transparent,
                "verbose": verbose,
                "use_web_compilation": use_web_compilation,
            }
            if output_unit is not None:
                savefig_kwargs["output_unit"] = output_unit
            self.savefig(**savefig_kwargs)

            import platform

            system = platform.system()

            if system == "Darwin":
                subprocess.run(["open", temp_path], check=True)
            elif system == "Linux":
                subprocess.run(["xdg-open", temp_path], check=True)
            elif system == "Windows":
                os.startfile(temp_path)  # type: ignore[attr-defined]
            else:
                print(f"Saved figure to: {temp_path}")
                print("Please open manually (unsupported platform for auto-display)")
        except Exception as e:
            print(f"Could not open figure automatically: {e}")
            print(f"Figure saved to: {temp_path}")

    def _show_pillow(
        self,
        dpi: int = 300,
        verbose: bool = False,
        transparent: bool = True,
        use_web_compilation: bool = False,
        output_unit: str | None = None,
    ) -> None:
        try:
            from PIL import Image
        except ImportError:
            raise ImportError(
                "Pillow is required for this backend. "
                "Install with: pip install Pillow\n"
                "Or use backend='system' or backend='matplotlib'"
            )

        with tempfile.TemporaryDirectory() as tempdir:
            temp_png = Path(tempdir) / "temp.png"
            savefig_kwargs: dict[str, Any] = {
                "filename": temp_png,
                "dpi": dpi,
                "transparent": transparent,
                "verbose": verbose,
                "use_web_compilation": use_web_compilation,
            }
            if output_unit is not None:
                savefig_kwargs["output_unit"] = output_unit
            self.savefig(**savefig_kwargs)

            img = Image.open(temp_png)
            img.show()

    def show(
        self,
        width: int | None = None,
        height: int | None = None,
        dpi: int = 300,
        verbose: bool = False,
        backend: str = "matplotlib",
        transparent: bool = True,
        use_web_compilation: bool = False,
        output_unit: str | None = None,
        check: bool = False,
    ) -> None:
        use_web_compilation = self._resolve_use_web_compilation(use_web_compilation)
        self._run_optional_check(check=check, output_unit=output_unit)

        if os.environ.get("tikzfigure_NO_SHOW") == "1" or os.environ.get(
            "PYTEST_CURRENT_TEST"
        ):
            if verbose:
                print("Display suppressed (test/headless mode).")
            return

        try:
            from IPython import get_ipython

            if get_ipython() is not None and "IPKernelApp" in get_ipython().config:
                from IPython.display import Image, display

                with tempfile.TemporaryDirectory() as tempdir:
                    temp_pdf = Path(tempdir) / "temp.png"
                    savefig_kwargs: dict[str, Any] = {
                        "filename": temp_pdf,
                        "transparent": transparent,
                        "verbose": verbose,
                        "use_web_compilation": use_web_compilation,
                    }
                    if output_unit is not None:
                        savefig_kwargs["output_unit"] = output_unit
                    self.savefig(**savefig_kwargs)
                    display(Image(filename=temp_pdf, width=width, height=height))
                return
        except (ImportError, AttributeError):
            pass

        if backend == "matplotlib":
            self._show_matplotlib(
                dpi=dpi,
                verbose=verbose,
                transparent=transparent,
                use_web_compilation=use_web_compilation,
                output_unit=output_unit,
            )
        elif backend == "system":
            self._show_system(
                dpi=dpi,
                verbose=verbose,
                transparent=transparent,
                use_web_compilation=use_web_compilation,
                output_unit=output_unit,
            )
        elif backend == "pillow":
            self._show_pillow(
                dpi=dpi,
                verbose=verbose,
                transparent=transparent,
                use_web_compilation=use_web_compilation,
                output_unit=output_unit,
            )
        else:
            raise ValueError(
                f"Unknown backend '{backend}'. "
                "Options: 'matplotlib', 'system', 'pillow'"
            )

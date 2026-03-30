from typing import Any

from IPython.core.magic import Magics, cell_magic, line_magic, magics_class

from tikzfigure.core.figure import TikzFigure


@magics_class
class TikzMagics(Magics):
    """IPython magic commands for rendering TikZ figures inline.

    Load this extension in a Jupyter notebook with::

        %load_ext tikzfigure.ipython

    Then use ``%%tikz`` to render TikZ code cells or ``%tikz_load`` to
    display a TikZ file from disk.
    """

    @cell_magic
    def tikz(self, line: str, cell: str) -> None:
        """Compile and display a TikZ figure from a cell.

        Usage::

            %%tikz [options]
            \\begin{tikzpicture}
            \\draw (0,0) -- (1,1);
            \\end{tikzpicture}

        Args:
            line: Command-line options for this magic:

                - ``-s`` / ``--save <path>`` – save output to *path*.
                - ``-w`` / ``--width <px>`` – display width in pixels
                  (Jupyter only).
                - ``-H`` / ``--height <px>`` – display height in pixels
                  (Jupyter only).
                - ``-v`` / ``--verbose`` – show compilation details.

            cell: The TikZ source code (the cell body).
        """
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument("-s", "--save", type=str, default=None)
        parser.add_argument("-w", "--width", type=int, default=None)
        parser.add_argument("-H", "--height", type=int, default=None)
        parser.add_argument("-v", "--verbose", action="store_true")

        try:
            args = parser.parse_args(line.split())
        except SystemExit:
            print("Error parsing arguments. Use %%tikz? for help.")
            return

        try:
            fig = TikzFigure.from_tikz_code(cell)

            if args.save:
                fig.savefig(filename=args.save, verbose=args.verbose)
                if args.verbose:
                    print(f"Saved to {args.save}")

            fig.show(width=args.width, height=args.height, verbose=args.verbose)

        except Exception as e:
            print(f"Error: {e}")
            if args.verbose:
                import traceback

                traceback.print_exc()

    @line_magic
    def tikz_load(self, line: str) -> None:
        """Load and display a TikZ figure from a file on disk.

        Usage::

            %tikz_load filename.tikz [options]

        Args:
            line: Space-separated arguments:

                - ``filename`` – path to the ``.tikz`` file (required).
                - ``-w`` / ``--width <px>`` – display width in pixels.
                - ``-H`` / ``--height <px>`` – display height in pixels.
        """
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument("filename", type=str)
        parser.add_argument("-w", "--width", type=int, default=None)
        parser.add_argument("-H", "--height", type=int, default=None)

        try:
            args = parser.parse_args(line.split())
        except SystemExit:
            print("Error parsing arguments. Use %tikz_load? for help.")
            return

        try:
            with open(args.filename, "r") as f:
                tikz_code = f.read()

            fig = TikzFigure.from_tikz_code(tikz_code)
            fig.show(width=args.width, height=args.height)

        except FileNotFoundError:
            print(f"Error: File '{args.filename}' not found.")


def load_ipython_extension(ipython: Any) -> None:
    """Register TikzMagics with the running IPython instance.

    Args:
        ipython: The active :class:`IPython.core.interactiveshell.InteractiveShell`
            instance provided by IPython's extension machinery.
    """
    ipython.register_magics(TikzMagics)


def unload_ipython_extension(ipython: Any) -> None:
    """Unload the tikzfigure IPython extension.

    Args:
        ipython: The active IPython shell instance. Currently unused.
    """
    pass

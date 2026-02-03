from IPython.core.magic import Magics, cell_magic, line_magic, magics_class

from tikzpics.figure import TikzFigure


@magics_class
class TikzMagics(Magics):
    """IPython magic commands for rendering TikZ figures."""

    @cell_magic
    def tikz(self, line, cell):
        """
        Cell magic to compile and display TikZ figures.

        Usage:
        ------
        %%tikz [options]
        \\begin{tikzpicture}
        \\draw (0,0) -- (1,1);
        \\end{tikzpicture}

        Options:
        --------
        -s, --save : Save output to file
        -w, --width : Display width in pixels
        -H, --height : Display height in pixels
        -v, --verbose : Show compilation details

        Examples:
        ---------
        %%tikz
        \\begin{tikzpicture}
        \\draw (0,0) circle (1cm);
        \\end{tikzpicture}

        %%tikz --save output.pdf
        \\begin{tikzpicture}
        \\node {Hello TikZ!};
        \\end{tikzpicture}

        %%tikz --width 800
        \\begin{tikzpicture}
        \\draw[->] (0,0) -- (2,0);
        \\end{tikzpicture}
        """
        # Parse options
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

        # Create TikzFigure and display
        try:
            fig = TikzFigure.from_tikz_code(cell)

            # Save if requested
            if args.save:
                fig.savefig(filename=args.save, verbose=args.verbose)
                if args.verbose:
                    print(f"Saved to {args.save}")

            # Display the figure
            fig.show(width=args.width, height=args.height, verbose=args.verbose)

        except Exception as e:
            print(f"Error: {e}")
            if args.verbose:
                import traceback

                traceback.print_exc()

    @line_magic
    def tikz_load(self, line):
        """
        Line magic to load and display a TikZ figure from file.

        Usage:
        ------
        %tikz_load filename.tikz [options]

        Options:
        --------
        -w, --width : Display width in pixels
        -H, --height : Display height in pixels

        Example:
        --------
        %tikz_load my_figure.tikz --width 800
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

        # Read TikZ file and display
        try:
            with open(args.filename, "r") as f:
                tikz_code = f.read()

            # Create figure and display
            fig = TikzFigure.from_tikz_code(tikz_code)
            fig.show(width=args.width, height=args.height)

        except FileNotFoundError:
            print(f"Error: File '{args.filename}' not found.")
        except Exception as e:
            print(f"Error: {e}")


def load_ipython_extension(ipython):
    """Load the extension in IPython."""
    ipython.register_magics(TikzMagics)


def unload_ipython_extension(ipython):
    """Unload the extension."""
    pass

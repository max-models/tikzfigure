import os
import re
import subprocess
import tempfile

import matplotlib.patches as patches
from numpy import isin

from maxtikzlib.color import Color
from maxtikzlib.coordinate import TikzCoordinate
from maxtikzlib.layer import Tikzlayer
from maxtikzlib.linestyle import Linestyle
from maxtikzlib.loop import Loop
from maxtikzlib.node import Node
from maxtikzlib.path import Path
from maxtikzlib.wrapper import TikzWrapper


class TikzFigure:
    def __init__(self, **kwargs):
        """
        Initialize the TikzFigure class for creating TikZ figures.

        Parameters:
        **kwargs: Arbitrary keyword arguments.
            - figsize (tuple): Figure size (default is (10, 6)).
            - caption (str): Caption for the figure.
            - description (str): Description of the figure.
            - label (str): Label for the figure.
            - grid (bool): Whether to display grid lines (default is False).
            TODO: Add all options
        """
        # Set default values
        self._figsize = kwargs.get("figsize", (10, 6))
        self._caption = kwargs.get("caption", None)
        self._description = kwargs.get("description", None)
        self._label = kwargs.get("label", None)
        self._grid = kwargs.get("grid", False)
        self._tikz_code = kwargs.get("tikz_code", None)
        self._figure_setup = kwargs.get("figure_setup", None)

        # Initialize lists to hold Node and Path objects
        self.nodes = []
        self.paths = []
        self.layers = {}

        # Counter for unnamed nodes
        self._node_counter = 0

        if self._tikz_code:
            self.tikz_to_figure(self._tikz_code)

    def tikz_to_figure(self, tikz_code):
        # print(tikz_code)
        lines = tikz_code.split("\n")
        lines = [line.lstrip().rstrip() for line in lines]
        lines = [line for line in lines if line not in ["", "\n"]]
        lines = [line for line in lines if not line[0] == "%"]
        assert lines[0] == "\\begin{tikzpicture}"
        assert lines[-1] == "\\end{tikzpicture}"

        current_layer = 0
        for line in lines[1:-1]:
            # print(line)

            # Match \begin{pgfonlayer}{layer}
            match_pgfdeclarelayer = re.search(r"\\pgfdeclarelayer\{(\d+)\}", line)
            if match_pgfdeclarelayer:
                layer = match_pgfdeclarelayer.group(1)
                self.add_layer(layer)
                # print(f"Layer number: {layer}")

            # Match \begin{pgfonlayer}{layer}
            match_begin_pgfonlayer = re.search(r"\\begin\{pgfonlayer\}\{(\d+)\}", line)
            if match_begin_pgfonlayer:
                current_layer = match_begin_pgfonlayer.group(1)
                # print(f'Current layer: {current_layer}')

            # Match \end{pgfonlayer}{layer}
            match_end_pgfonlayer = re.search(r"\\end\{pgfonlayer\}\{(\d+)\}", line)
            if match_end_pgfonlayer:
                current_layer = 0
                # print(f'Current layer: {current_layer}')

            # Match \node[attributes] at (x,y) {content};
            match_node = re.search(
                r"\\node(?:\[([^\]]+)\])? \((\w+)\) at \(([^,]+, [^)]+)\) \{(.*)\};",
                line,
            )
            if match_node:
                attributes = match_node.group(1)
                attributes = [
                    attribute.lstrip().rstrip() for attribute in attributes.split(",")
                ]
                attributes = [
                    attribute for attribute in attributes if not attribute == ""
                ]
                attributes_dict = dict(attr.split("=") for attr in attributes)
                node_name = match_node.group(2)
                coordinates = match_node.group(3)
                coordinates = [c for c in coordinates.split(",")]
                coordinates = [c for c in coordinates]
                coordinates = [c.lstrip().rstrip() for c in coordinates]
                content = match_node.group(4)
                # print(f"Attributes: {attributes_dict}")
                # print(f"Node name: {node_name}")
                # print(f"Coordinates: {coordinates}")
                # print(f"Node text: '{node_text}'")
                # print(coordinates.split(','))

                self.add_node(
                    coordinates[0],
                    coordinates[1],
                    node_name,
                    layer=current_layer,
                    content=content,
                    **attributes_dict,
                )

            # Match \draw[attributes] (node1.center) to (node2.center) to (node2.center)...;
            match_draw = re.search(
                r"\\draw(?:\[([^\]]+)\])? ((?:\(\w+\.*\) to )+\(\w+\.*\));",
                line,
            )
            if match_draw:
                attributes = match_draw.group(1)
                attributes = [
                    attribute.lstrip().rstrip() for attribute in attributes.split(",")
                ]
                attributes = [
                    attribute for attribute in attributes if not attribute == ""
                ]
                path = match_draw.group(2)
                nodes = re.findall(r"\((\w+)\.*\)", path)

                # print(f"Attributes: {attributes}")
                # print(f"Path: {path}")
                # print(f"Nodes: {nodes}")
                self.add_path(nodes, path_actions=attributes, layer=current_layer)

    def add_layer(self, layer):
        if layer not in self.layers:
            self.layers[layer] = Tikzlayer(layer)

    def add_node(
        self,
        x,
        y,
        label=None,
        content: str = "",
        layer=0,
        comment=None,
        **kwargs,
    ):
        """
        Add a node to the TikZ figure.

        Parameters:
        - x (float): X-coordinate of the node.
        - y (float): Y-coordinate of the node.
        - label (str, optional): Label of the node. If None, a default label will be assigned.
        - content: (str, optional): Content of the node
        - comment: (str, optional): Comment to be added before the node
        - **kwargs: Additional TikZ node options (e.g., shape, color).

        Returns:
        - node (Node): The Node object that was added.
        """
        if label is None:
            label = f"node{self._node_counter}"
        node = Node(
            x=x,
            y=y,
            label=label,
            layer=layer,
            content=content,
            comment=comment,
            **kwargs,
        )
        self.nodes.append(node)
        if layer in self.layers:
            self.layers[layer].add(node)
        else:
            self.layers[layer] = Tikzlayer(layer)
            self.layers[layer].add(node)
        self._node_counter += 1
        return node

    def add_path(
        self,
        nodes: list,
        layer: int = 0,
        comment: str | None = None,
        center=False,
        **kwargs,
    ):
        """
        Add a line or path connecting multiple nodes.

        Parameters:
        - nodes (list of str): List of node names to connect OR list of coordinates
        - **kwargs: Additional TikZ path options (e.g., style, color).

        Examples:
        - add_path(['A', 'B', 'C'], color='blue')
          Connects nodes A -> B -> C with a blue line.
        """
        if not isinstance(nodes, list):
            raise ValueError("nodes parameter must be a list of node names.")
        # nodes = [
        #     (
        #         node
        #         if isinstance(node, Node)
        #         else (
        #             self.get_node(node)
        #             if isinstance(node, str)
        #             else ValueError(f"Invalid node type: {type(node)}")
        #         )
        #     )
        #     for node in nodes
        # ]

        nodes_cleaned = []

        for node in nodes:
            if isinstance(node, Node):
                nodes_cleaned.append(node)
            elif isinstance(node, str):
                # Find the node by its label
                nodes_cleaned.append(self.get_node(node))
            elif isinstance(node, tuple) or isinstance(node, list):
                node = tuple(node)
                nodes_cleaned.append(TikzCoordinate(*node, layer=layer))
            else:
                raise NotImplementedError(
                    f"{node = }, {type(node) = } is not a valid node type!"
                )
        # print(nodes_cleaned)
        path = Path(
            nodes_cleaned,
            comment=comment,
            center=center,
            **kwargs,
        )
        self.paths.append(path)
        if layer in self.layers:
            self.layers[layer].add(path)
        else:
            self.layers[layer] = Tikzlayer(layer)
            self.layers[layer].add(path)
        return path

    def add_item(self, item, layer=0):
        if layer in self.layers:
            self.layers[layer].add(item)
        else:
            self.layers[layer] = Tikzlayer(layer)
            self.layers[layer].add(item)
        return item

    def loop(
        self,
        variable,
        values,
        layer=0,
        comment=None,
    ):
        loop_obj = Loop(
            variable=variable,
            values=values,
            layer=layer,
            comment=comment,
        )
        self.add_item(loop_obj, layer)
        return loop_obj

    def add_raw(self, raw_tikz, layer=0, **kwargs):
        tikz = TikzWrapper(raw_tikz)
        if layer in self.layers:
            self.layers[layer].add(tikz)
        else:
            self.layers[layer] = Tikzlayer(layer)
            self.layers[layer].add(tikz)
        return tikz

    def get_node(self, node_label):
        for node in self.nodes:
            if node.label == node_label:
                return node

    def get_layer(self, item):
        for layer, layer_items in self.layers.items():
            if item in [layer_item.label for layer_item in layer_items]:
                return layer
        print(f"Item {item} not found in any layer!")

    def add_tabs(self, tikz_script):
        tikz_script_new = ""
        tab_str = "    "
        num_tabs = 0
        for line in tikz_script.split("\n"):
            if "\\end" in line or "end \\foreach" in line:
                num_tabs = max(num_tabs - 1, 0)
            tikz_script_new += f"{tab_str*num_tabs}{line}\n"
            if "\\begin" in line or "start \\foreach" in line:
                num_tabs += 1
        return tikz_script_new

    def generate_tikz(self):
        """
        Generate the TikZ script for the figure.

        Returns:
        - tikz_script (str): The TikZ script as a string.
        """
        tikz_script = "\\begin{tikzpicture}"
        if self._figure_setup:
            tikz_script += f"[{self._figure_setup}]"
        tikz_script += "\n"

        tikz_script += "% Define the layers library\n"
        layers = sorted([str(layer) for layer in self.layers.keys()])
        for layer in layers:
            tikz_script += f"\\pgfdeclarelayer{{{layer}}}\n"
        tikz_script += f"\\pgfsetlayers{{{','.join(layers)}}}\n"

        # Add grid if enabled
        # TODO: Create a Grid class
        if self._grid:
            tikz_script += (
                "    \\draw[step=1cm, gray, very thin] (-10,-10) grid (10,10);\n"
            )
        ordered_layers = []
        buffered_layers = set()

        for key, layer in self.layers.items():
            # layer_order, buffered_layers = update_layer_order(layer, layer_order, buffered_layers)
            reqs = layer.get_reqs()
            if all([r == layer.label for r in reqs]):
                ordered_layers.append(layer)
            elif all([r in [l.label for l in ordered_layers] for r in reqs]):
                ordered_layers.append(layer)
            else:
                buffered_layers.add(layer)

            for buffered_layer in buffered_layers:
                buff_reqs = buffered_layer.get_reqs()
                if all([r in [l.label for l in ordered_layers] for r in buff_reqs]):
                    print("Move layer from buffer")
                    ordered_layers.append(key)
                    buffered_layers.remove(key)
        assert (
            len(buffered_layers) == 0
        ), f"Layer order is impossible for layer {[layer.label for layer in buffered_layers]}"
        for layer in ordered_layers:
            tikz_script += layer.generate_tikz()

        tikz_script += "\\end{tikzpicture}"

        # Wrap in figure environment if necessary
        if self._caption or self._description or self._label:
            figure_env = "\\begin{figure}\n" + tikz_script + "\n"
            if self._caption:
                figure_env += f"    \\caption{{{self._caption}}}\n"
            if self._label:
                figure_env += f"    \\label{{{self._label}}}\n"
            figure_env += "\\end{figure}"
            tikz_script = figure_env
        tikz_script = self.add_tabs(tikz_script)
        return tikz_script

    def savefig(self, filepath):
        tikz_code = self.generate_tikz()
        with open(filepath, "w") as f:
            f.write(tikz_code)

    def generate_standalone(self):
        tikz_code = self.generate_tikz()

        # Create a minimal LaTeX document
        latex_document = (
            "\\documentclass[border=10pt]{standalone}\n"
            "\\usepackage{tikz}\n"
            "\\usetikzlibrary{arrows.meta}\n"
            "\\begin{document}\n"
            f"{tikz_code}\n"
            "\\end{document}"
        )
        return latex_document

    def compile_pdf(self, filename="output.pdf"):
        """
        Compile the TikZ script into a PDF using pdflatex.

        Parameters:
        - filename (str): The name of the output PDF file (default is 'output.pdf').

        Notes:
        - Requires 'pdflatex' to be installed and accessible from the command line.
        """
        latex_document = self.generate_standalone()

        # Use a temporary directory to store the LaTeX files
        with tempfile.TemporaryDirectory() as tempdir:
            tex_file = os.path.join(tempdir, "figure.tex")
            with open(tex_file, "w") as f:
                f.write(latex_document)
            # Run pdflatex
            try:
                # Split the path
                head_tail = os.path.split(os.path.abspath(filename))
                output_directory = head_tail[0]
                jobname = head_tail[1].replace(".pdf", "")
                cmd = [
                    "pdflatex",
                    "-interaction=nonstopmode",
                    "-jobname",
                    f"{jobname}",
                    "-output-directory",
                    f"{output_directory}",
                    tex_file,
                ]
                # print(f"running {cmd}")
                subprocess.run(
                    cmd,
                    cwd=tempdir,
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                # Remove .aux and .log files
                os.remove(os.path.abspath(filename).replace(".pdf", ".aux"))
                os.remove(os.path.abspath(filename).replace(".pdf", ".log"))
            except subprocess.CalledProcessError as e:
                print("An error occurred while compiling the LaTeX document:")
                print(e.stderr.decode())
                return

    # TODO: This should probably be removed and moved to maxplotlib instead
    def plot_matplotlib(self, ax):
        """
        Plot all nodes and paths on the provided axis using Matplotlib.

        Parameters:
        - ax (matplotlib.axes.Axes): Axis on which to plot the figure.
        """

        # Plot paths first so they appear behind nodes
        for path in self.paths:
            x_coords = [node.x for node in path.nodes]
            y_coords = [node.y for node in path.nodes]

            # Parse path color
            path_color_spec = path.options.get("color", "black")
            try:
                color = Color(path_color_spec).to_rgb()
            except ValueError as e:
                print(e)
                color = "black"

            # Parse line width
            line_width_spec = path.options.get("line_width", 1)
            if isinstance(line_width_spec, str):
                match = re.match(r"([\d.]+)(pt)?", line_width_spec)
                if match:
                    line_width = float(match.group(1))
                else:
                    print(
                        f"Invalid line width specification: '{line_width_spec}', defaulting to 1",
                    )
                    line_width = 1
            else:
                line_width = float(line_width_spec)

            # Parse line style using Linestyle class
            style_spec = path.options.get("style", "solid")
            linestyle = Linestyle(style_spec).to_matplotlib()

            ax.plot(
                x_coords,
                y_coords,
                color=color,
                linewidth=line_width,
                linestyle=linestyle,
                zorder=1,  # Lower z-order to place behind nodes
            )

        # Plot nodes after paths so they appear on top
        for node in self.nodes:
            # Determine shape and size
            shape = node.options.get("shape", "circle")
            fill_color_spec = node.options.get("fill", "white")
            edge_color_spec = node.options.get("draw", "black")
            linewidth = float(node.options.get("line_width", 1))
            size = float(node.options.get("size", 1))

            # Parse colors using the Color class
            try:
                facecolor = Color(fill_color_spec).to_rgb()
            except ValueError as e:
                print(e)
                facecolor = "white"

            try:
                edgecolor = Color(edge_color_spec).to_rgb()
            except ValueError as e:
                print(e)
                edgecolor = "black"

            # Plot shapes
            if shape == "circle":
                radius = size / 2
                circle = patches.Circle(
                    (node.x, node.y),
                    radius,
                    facecolor=facecolor,
                    edgecolor=edgecolor,
                    linewidth=linewidth,
                    zorder=2,  # Higher z-order to place on top of paths
                )
                ax.add_patch(circle)
            elif shape == "rectangle":
                width = height = size
                rect = patches.Rectangle(
                    (node.x - width / 2, node.y - height / 2),
                    width,
                    height,
                    facecolor=facecolor,
                    edgecolor=edgecolor,
                    linewidth=linewidth,
                    zorder=2,  # Higher z-order
                )
                ax.add_patch(rect)
            else:
                # Default to circle if shape is unknown
                radius = size / 2
                circle = patches.Circle(
                    (node.x, node.y),
                    radius,
                    facecolor=facecolor,
                    edgecolor=edgecolor,
                    linewidth=linewidth,
                    zorder=2,
                )
                ax.add_patch(circle)

            # Add text inside the shape
            if node.content:
                ax.text(
                    node.x,
                    node.y,
                    node.content,
                    fontsize=10,
                    ha="center",
                    va="center",
                    wrap=True,
                    zorder=3,  # Even higher z-order for text
                )

        # Remove axes, ticks, and legend
        ax.axis("off")

        # Adjust plot limits
        all_x = [node.x for node in self.nodes]
        all_y = [node.y for node in self.nodes]
        padding = 1  # Adjust padding as needed
        ax.set_xlim(min(all_x) - padding, max(all_x) + padding)
        ax.set_ylim(min(all_y) - padding, max(all_y) + padding)
        ax.set_aspect("equal", adjustable="datalim")


def main():

    tikz = TikzFigure()

    path_actions = ["draw", "rounded corners", "line width=3"]

    # M
    nodes = [[0, 0], [0, 3], [1, 2], [2, 3], [2, 0]]
    for i, node_data in enumerate(nodes):
        tikz.add_node(node_data[0], node_data[1], f"M{i}", layer=0)
    tikz.add_path(
        [f"M{i}" for i in range(len(nodes))],
        path_actions=path_actions,
        layer=1,
    )

    print(tikz.generate_standalone())


if __name__ == "__main__":
    main()

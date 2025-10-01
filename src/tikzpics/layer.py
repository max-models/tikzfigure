from tikzpics.node import Node
from tikzpics.path import Path


class Tikzlayer:
    def __init__(self, label, comment=None):
        self.label = label
        self.items = []

    def add(self, item):
        self.items.append(item)

    def get_reqs(self):
        reqs = set()
        for item in self.items:
            if isinstance(item, Path):
                for node in item._nodes:
                    if not node.layer == self.label:
                        reqs.add(node.layer)
        return reqs

    def generate_tikz(self):
        tikz_script = f"\n% Layer {self.label}\n"
        tikz_script += f"\\begin{{pgfonlayer}}{{{self.label}}}\n"
        for item in self.items:
            tikz_script += item.to_tikz()
        tikz_script += f"\\end{{pgfonlayer}}{{{self.label}}}\n"
        return tikz_script


class LayerCollection:
    def __init__(self) -> None:
        # self._layers = []
        self._layers = {}

    def add_layer(self, layer):
        if layer not in self.layers:
            self._layers[layer] = Tikzlayer(layer)

    def add_item(self, item, layer: int | None = 0, verbose=False):

        if layer in self.layers:
            self._layers[layer].add(item)
        else:
            self.add_layer(layer)
            self._layers[layer].add(item)

        if verbose:
            print(f"Added {item} to layer {layer}, {self._layers[layer] =}")

        return item

    def get_node(self, node_label):
        for layer in self.layers.values():
            print(f"{layer =}")
            for item in layer.items:
                if isinstance(item, Node) and item.label == node_label:
                    return item

    def get_layer(self, item):
        for layer, layer_items in self._layers.items():
            if item in [layer_item.label for layer_item in layer_items]:
                return layer
        print(f"Item {item} not found in any layer!")

    @property
    def layers(self) -> dict:
        return self._layers

        return self._layers

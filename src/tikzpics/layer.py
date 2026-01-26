from tikzpics.node import Node
from tikzpics.path import Path


class Tikzlayer:
    """Represents a single layer in a TikZ figure.

    Layers allow organizing TikZ elements in different drawing levels,
    useful for controlling z-order and managing complex figures.

    Attributes:
        label: Unique identifier for the layer.
        items: List of TikZ items (nodes, paths, etc.) in this layer.
    """

    def __init__(self, label, comment=None):
        """Initialize a TikZ layer.

        Args:
            label: Unique identifier for the layer (typically an integer).
            comment: Optional comment for documentation purposes.
        """
        self.label = label
        self.items = []

    def add(self, item):
        """Add an item (node, path, etc.) to this layer.

        Args:
            item: A TikZ object (Node, Path, etc.) to add to the layer.
        """
        self.items.append(item)

    def get_reqs(self):
        """Get layer requirements (dependencies on other layers).

        Analyzes paths in this layer to find nodes from other layers,
        which establishes layer dependencies for proper rendering order.

        Returns:
            Set of layer labels that this layer depends on.
        """
        reqs = set()
        for item in self.items:
            if isinstance(item, Path):
                for node in item._nodes:
                    if not node.layer == self.label:
                        reqs.add(node.layer)
        return reqs

    def generate_tikz(self):
        """Generate TikZ code for this layer.

        Creates the pgfonlayer environment and includes all items in the layer.

        Returns:
            String containing the complete TikZ code for this layer.
        """
        tikz_script = f"\n% Layer {self.label}\n"
        tikz_script += f"\\begin{{pgfonlayer}}{{{self.label}}}\n"
        for item in self.items:
            tikz_script += item.to_tikz()
        tikz_script += f"\\end{{pgfonlayer}}{{{self.label}}}\n"
        return tikz_script

    def _get_items_by_type(self, item_type) -> list:
        """Get all items of a specific type from this layer.

        Args:
            item_type: The type to filter by (e.g., Node, Path).

        Returns:
            List of items matching the specified type.
        """
        return [item for item in self.items if isinstance(item, item_type)]

    def get_nodes(self) -> list[Node]:
        """Get all nodes in this layer.

        Returns:
            List of Node objects in this layer.
        """
        return self._get_items_by_type(Node)

    def get_paths(self) -> list[Path]:
        """Get all paths in this layer.

        Returns:
            List of Path objects in this layer.
        """
        return self._get_items_by_type(Path)


class LayerCollection:
    """Manages a collection of TikZ layers.

    Provides methods to create layers, add items to layers, and retrieve
    items across all layers. Handles layer creation automatically when
    items are added to non-existent layers.

    Attributes:
        _layers: Dictionary mapping layer labels to Tikzlayer objects.
    """

    def __init__(self) -> None:
        """Initialize an empty layer collection."""
        # self._layers = []
        self._layers = {}

    def add_layer(self, layer):
        """Add a new layer to the collection.

        If the layer already exists, this method does nothing.

        Args:
            layer: Label for the new layer (typically an integer).
        """
        if layer not in self.layers:
            self._layers[layer] = Tikzlayer(layer)

    def add_item(self, item, layer: int | None = 0, verbose=False):
        """Add an item to a specific layer.

        Creates the layer automatically if it doesn't exist.

        Args:
            item: A TikZ object (Node, Path, etc.) to add.
            layer: Layer label to add the item to. Defaults to 0.
            verbose: If True, print debug information.

        Returns:
            The item that was added.
        """

        if layer in self.layers:
            self._layers[layer].add(item)
        else:
            self.add_layer(layer)
            self._layers[layer].add(item)

        if verbose:
            print(f"Added {item} to layer {layer}, {self._layers[layer] =}")

        return item

    def get_node(self, node_label) -> Node:
        """Retrieve a node by its label from any layer.

        Args:
            node_label: The label of the node to find.

        Returns:
            The Node object with the specified label.

        Raises:
            ValueError: If no node with the given label exists in any layer.
        """
        for layer in self.layers.values():
            for item in layer.items:
                if isinstance(item, Node) and item.label == node_label:
                    return item
        raise ValueError(f"Node with label {node_label} not found in any layer!")

    def _get_items_by_type(self, item_type) -> list:
        """Get all items of a specific type across all layers.

        Args:
            item_type: The type to filter by (e.g., Node, Path).

        Returns:
            List of items matching the specified type from all layers.
        """
        items = []
        for layer in self.layers.values():
            items.extend(layer._get_items_by_type(item_type))
        return items

    def get_nodes(self) -> list[Node]:
        """Get all nodes across all layers.

        Returns:
            List of all Node objects in the collection.
        """
        return self._get_items_by_type(Node)

    def get_paths(self) -> list[Path]:
        """Get all paths across all layers.

        Returns:
            List of all Path objects in the collection.
        """
        return self._get_items_by_type(Path)

    def get_layer_by_item(self, item) -> int:
        """Find which layer contains an item with the given label.

        Args:
            item: Label of the item to search for.

        Returns:
            The layer label containing the item.

        Raises:
            ValueError: If the item is not found in any layer.
        """
        for layer, layer_items in self._layers.items():
            if item in [layer_item.label for layer_item in layer_items.items]:
                return layer
        raise ValueError(f"Item {item} not found in any layer!")

    @property
    def layers(self) -> dict:
        """Get the dictionary of all layers.

        Returns:
            Dictionary mapping layer labels to Tikzlayer objects.
        """
        return self._layers

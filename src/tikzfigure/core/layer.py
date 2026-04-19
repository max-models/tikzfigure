from typing import Any

from tikzfigure.core.coordinate import Coordinate
from tikzfigure.core.node import Node
from tikzfigure.core.path import TikzPath


class Tikzlayer:
    """A single named drawing layer inside a TikZ figure.

    Layers allow controlling the z-order of elements by wrapping them
    inside ``\\begin{pgfonlayer}{label}`` … ``\\end{pgfonlayer}`` blocks.

    Attributes:
        label: Unique identifier for this layer (typically an integer).
        items: Ordered list of TikZ objects (nodes, paths, loops, …)
            belonging to this layer.
    """

    def __init__(self, label: int | str, comment: str | None = None) -> None:
        """Initialize a Tikzlayer.

        Args:
            label: Unique identifier for this layer (typically an integer).
            comment: Optional comment for documentation purposes. Currently
                unused in output generation.
        """
        self.label: int | str = label
        self.items: list[Any] = []

    def add(self, item: Any) -> None:
        """Append a TikZ object to this layer.

        Args:
            item: A TikZ object (e.g. :class:`Node`, :class:`TikzPath`)
                to add to this layer.
        """
        self.items.append(item)

    def get_reqs(self) -> set[int | str]:
        """Return the set of layer labels this layer depends on.

        Inspects every :class:`TikzPath` in this layer and collects the
        layer labels of any nodes that live on a *different* layer. This
        information is used to determine a valid rendering order.

        Returns:
            A set of layer labels that must be rendered before this layer.
        """

        def _iter_paths(items: list[Any]) -> list[TikzPath]:
            paths: list[TikzPath] = []
            for item in items:
                if isinstance(item, TikzPath):
                    paths.append(item)
                nested_items = getattr(item, "items", None)
                if nested_items is not None:
                    paths.extend(_iter_paths(nested_items))
            return paths

        reqs = set()
        for item in _iter_paths(self.items):
            for node in item._nodes:
                if not node.layer == self.label:
                    reqs.add(node.layer)
        return reqs

    def generate_tikz(
        self,
        use_layers: bool = True,
        verbose: bool = False,
        output_unit: str | None = None,
    ) -> str:
        """Generate the TikZ code for this layer.

        Args:
            use_layers: If ``True``, wrap the output in a
                ``pgfonlayer`` environment. Defaults to ``True``.
            verbose: Unused; reserved for future debug output.

        Returns:
            The complete TikZ code string for this layer, including the
            ``pgfonlayer`` wrapper when *use_layers* is ``True``.
        """
        tikz_script = ""
        if use_layers:
            tikz_script += f"\n% Layer {self.label}\n"
            tikz_script += f"\\begin{{pgfonlayer}}{{{self.label}}}\n"
        for item in self.items:
            tikz_script += item.to_tikz(output_unit)
        if use_layers:
            tikz_script += f"\\end{{pgfonlayer}}{{{self.label}}}\n"
        return tikz_script

    def _get_items_by_type(self, item_type: type) -> list[Any]:
        """Return all items in this layer that are instances of *item_type*.

        Args:
            item_type: The type to filter by (e.g. :class:`Node`).

        Returns:
            A list of items whose type matches *item_type*.
        """
        return [item for item in self.items if isinstance(item, item_type)]

    def get_nodes(self) -> list[Node]:
        """Return all nodes in this layer.

        Returns:
            A list of :class:`Node` objects belonging to this layer.
        """
        return self._get_items_by_type(Node)

    def get_paths(self) -> list[TikzPath]:
        """Return all paths in this layer.

        Returns:
            A list of :class:`TikzPath` objects belonging to this layer.
        """
        return self._get_items_by_type(TikzPath)


class LayerCollection:
    """An ordered collection of :class:`Tikzlayer` objects.

    Manages layer creation, item insertion, and cross-layer node lookup.
    Layers are created automatically when items are added to a layer label
    that does not yet exist.

    Attributes:
        layers: Dictionary mapping layer labels to :class:`Tikzlayer`
            objects.
        num_layers: Number of layers currently in the collection.
    """

    def __init__(self) -> None:
        """Initialize an empty LayerCollection."""
        self._layers: dict[int | str, Tikzlayer] = {}

    def add_layer(self, layer: int | str) -> None:
        """Add a new layer to the collection.

        If a layer with the given label already exists, this is a no-op.

        Args:
            layer: Label for the new layer (typically an integer).
        """
        if layer not in self.layers:
            self._layers[layer] = Tikzlayer(layer)

    def add_item(
        self, item: Any, layer: int | str | None = 0, verbose: bool = False
    ) -> Any:
        """Add an item to a specific layer, creating the layer if needed.

        Args:
            item: A TikZ object to add (e.g. :class:`Node`,
                :class:`TikzPath`).
            layer: Label of the target layer. ``None`` is treated as ``0``.
                Defaults to ``0``.
            verbose: If ``True``, print a debug message after insertion.

        Returns:
            The *item* that was added.
        """
        if layer is None:
            layer = 0

        if layer in self.layers:
            self._layers[layer].add(item)
        else:
            self.add_layer(layer)
            self._layers[layer].add(item)

        if verbose:
            print(f"Added {item} to layer {layer}, {self._layers[layer] =}")

        return item

    def get_node(self, node_label: str) -> "Node | Coordinate":
        """Retrieve a node or coordinate by its label, searching all layers.

        Args:
            node_label: The label of the node or coordinate to find.

        Returns:
            The :class:`Node` or :class:`Coordinate` with the specified label.

        Raises:
            ValueError: If no node or coordinate with the given label exists
                in any layer.
        """

        def _search(items: list[Any]) -> Node | Coordinate | None:
            for item in items:
                if isinstance(item, (Node, Coordinate)) and item.label == node_label:
                    return item
                nested_items = getattr(item, "items", None)
                if nested_items is not None:
                    found = _search(nested_items)
                    if found is not None:
                        return found
            return None

        for layer in self.layers.values():
            found = _search(layer.items)
            if found is not None:
                return found
        raise ValueError(f"Node with label {node_label} not found in any layer!")

    def _get_items_by_type(self, item_type: type) -> list[Any]:
        """Return all items of *item_type* across all layers.

        Args:
            item_type: The type to filter by (e.g. :class:`Node`).

        Returns:
            A flat list of items matching *item_type* from every layer.
        """
        items = []
        for layer in self.layers.values():
            items.extend(layer._get_items_by_type(item_type))
        return items

    def get_nodes(self) -> list[Node]:
        """Return all nodes across all layers.

        Returns:
            A flat list of all :class:`Node` objects in the collection.
        """
        return self._get_items_by_type(Node)

    def get_paths(self) -> list[TikzPath]:
        """Return all paths across all layers.

        Returns:
            A flat list of all :class:`TikzPath` objects in the collection.
        """
        return self._get_items_by_type(TikzPath)

    def get_layer_by_item(self, item: str) -> int | str:
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
    def layers(self) -> dict[int | str, Tikzlayer]:
        """Dictionary mapping layer labels to :class:`Tikzlayer` objects."""
        return self._layers

    @property
    def num_layers(self) -> int:
        """Number of layers currently in the collection."""
        return len(self._layers)

import pytest

from tikzpics.layer import LayerCollection, Tikzlayer
from tikzpics.node import Node
from tikzpics.path import Path


class TestTikzlayer:
    """Test the Tikzlayer class."""

    def test_init(self):
        """Test layer initialization."""
        layer = Tikzlayer(label=1, comment="Test layer")
        assert layer.label == 1
        assert layer.items == []

    def test_add_node(self):
        """Test adding a node to a layer."""
        layer = Tikzlayer(label=0)
        node = Node(x=0, y=0, label="node1")
        layer.add(node)
        assert len(layer.items) == 1
        assert layer.items[0] == node

    def test_add_path(self):
        """Test adding a path to a layer."""
        layer = Tikzlayer(label=0)
        node1 = Node(x=0, y=0, label="node1")
        node2 = Node(x=1, y=1, label="node2")
        path = Path(nodes=[node1, node2], label="path1")
        layer.add(path)
        assert len(layer.items) == 1
        assert layer.items[0] == path

    def test_add_multiple_items(self):
        """Test adding multiple items to a layer."""
        layer = Tikzlayer(label=0)
        node1 = Node(x=0, y=0, label="node1")
        node2 = Node(x=1, y=1, label="node2")
        path = Path(nodes=[node1, node2], label="path1")

        layer.add(node1)
        layer.add(node2)
        layer.add(path)

        assert len(layer.items) == 3

    def test_get_nodes(self):
        """Test getting all nodes from a layer."""
        layer = Tikzlayer(label=0)
        node1 = Node(x=0, y=0, label="node1")
        node2 = Node(x=1, y=1, label="node2")
        path = Path(nodes=[node1, node2], label="path1")

        layer.add(node1)
        layer.add(node2)
        layer.add(path)

        nodes = layer.get_nodes()
        assert len(nodes) == 2
        assert node1 in nodes
        assert node2 in nodes

    def test_get_paths(self):
        """Test getting all paths from a layer."""
        layer = Tikzlayer(label=0)
        node1 = Node(x=0, y=0, label="node1")
        node2 = Node(x=1, y=1, label="node2")
        path1 = Path(nodes=[node1, node2], label="path1")
        path2 = Path(nodes=[node2, node1], label="path2")

        layer.add(node1)
        layer.add(path1)
        layer.add(path2)

        paths = layer.get_paths()
        assert len(paths) == 2
        assert path1 in paths
        assert path2 in paths

    def test_get_reqs(self):
        """Test getting layer requirements (nodes from other layers)."""
        layer1 = Tikzlayer(label=1)
        node1 = Node(x=0, y=0, label="node1", layer=0)
        node2 = Node(x=1, y=1, label="node2", layer=1)
        path = Path(nodes=[node1, node2], label="path1")

        layer1.add(path)
        reqs = layer1.get_reqs()

        assert 0 in reqs
        assert 1 not in reqs

    def test_generate_tikz(self):
        """Test TikZ code generation."""
        layer = Tikzlayer(label=0)
        node1 = Node(x=0, y=0, label="node1", content="A")
        layer.add(node1)

        tikz_code = layer.generate_tikz()
        assert "\\begin{pgfonlayer}{0}" in tikz_code
        assert "\\end{pgfonlayer}{0}" in tikz_code
        assert "% Layer 0" in tikz_code


class TestLayerCollection:
    """Test the LayerCollection class."""

    def test_init(self):
        """Test layer collection initialization."""
        collection = LayerCollection()
        assert collection.layers == {}

    def test_add_layer(self):
        """Test adding a layer to the collection."""
        collection = LayerCollection()
        collection.add_layer(0)
        assert 0 in collection.layers
        assert isinstance(collection.layers[0], Tikzlayer)

    def test_add_layer_duplicate(self):
        """Test that adding duplicate layer doesn't create multiple layers."""
        collection = LayerCollection()
        collection.add_layer(0)
        collection.add_layer(0)
        assert len(collection.layers) == 1

    def test_add_item_new_layer(self):
        """Test adding an item creates layer if it doesn't exist."""
        collection = LayerCollection()
        node = Node(x=0, y=0, label="node1")
        collection.add_item(node, layer=1)

        assert 1 in collection.layers
        assert node in collection.layers[1].items

    def test_add_item_existing_layer(self):
        """Test adding an item to an existing layer."""
        collection = LayerCollection()
        collection.add_layer(0)
        node = Node(x=0, y=0, label="node1")
        collection.add_item(node, layer=0)

        assert len(collection.layers[0].items) == 1
        assert node in collection.layers[0].items

    def test_add_item_default_layer(self):
        """Test adding an item to default layer 0."""
        collection = LayerCollection()
        node = Node(x=0, y=0, label="node1")
        collection.add_item(node)

        assert 0 in collection.layers
        assert node in collection.layers[0].items

    def test_add_item_returns_item(self):
        """Test that add_item returns the item."""
        collection = LayerCollection()
        node = Node(x=0, y=0, label="node1")
        returned_node = collection.add_item(node)

        assert returned_node == node

    def test_get_node(self):
        """Test retrieving a node by label."""
        collection = LayerCollection()
        node1 = Node(x=0, y=0, label="node1")
        node2 = Node(x=1, y=1, label="node2")

        collection.add_item(node1, layer=0)
        collection.add_item(node2, layer=1)

        retrieved_node = collection.get_node("node1")
        assert retrieved_node == node1

        retrieved_node2 = collection.get_node("node2")
        assert retrieved_node2 == node2

    def test_get_node_not_found(self):
        """Test that getting nonexistent node raises ValueError."""
        collection = LayerCollection()
        node = Node(x=0, y=0, label="node1")
        collection.add_item(node)

        with pytest.raises(ValueError, match="Node with label node2 not found"):
            collection.get_node("node2")

    def test_get_nodes(self):
        """Test getting all nodes from all layers."""
        collection = LayerCollection()
        node1 = Node(x=0, y=0, label="node1")
        node2 = Node(x=1, y=1, label="node2")
        node3 = Node(x=2, y=2, label="node3")
        path = Path(nodes=[node1, node2], label="path1")

        collection.add_item(node1, layer=0)
        collection.add_item(node2, layer=0)
        collection.add_item(node3, layer=1)
        collection.add_item(path, layer=0)

        nodes = collection.get_nodes()
        assert len(nodes) == 3
        assert node1 in nodes
        assert node2 in nodes
        assert node3 in nodes

    def test_get_paths(self):
        """Test getting all paths from all layers."""
        collection = LayerCollection()
        node1 = Node(x=0, y=0, label="node1")
        node2 = Node(x=1, y=1, label="node2")
        path1 = Path(nodes=[node1, node2], label="path1")
        path2 = Path(nodes=[node2, node1], label="path2")

        collection.add_item(node1, layer=0)
        collection.add_item(path1, layer=0)
        collection.add_item(path2, layer=1)

        paths = collection.get_paths()
        assert len(paths) == 2
        assert path1 in paths
        assert path2 in paths

    def test_get_layer_by_item(self):
        """Test retrieving the layer number for an item."""
        collection = LayerCollection()
        node1 = Node(x=0, y=0, label="node1")
        node2 = Node(x=1, y=1, label="node2")

        collection.add_item(node1, layer=0)
        collection.add_item(node2, layer=2)

        layer = collection.get_layer_by_item("node1")
        assert layer == 0

        layer2 = collection.get_layer_by_item("node2")
        assert layer2 == 2

    def test_get_layer_by_item_not_found(self):
        """Test that getting layer for nonexistent item raises ValueError."""
        collection = LayerCollection()
        node = Node(x=0, y=0, label="node1")
        collection.add_item(node)

        with pytest.raises(ValueError, match="Item node2 not found"):
            collection.get_layer_by_item("node2")

    def test_layers_property(self):
        """Test that layers property returns the dictionary."""
        collection = LayerCollection()
        collection.add_layer(0)
        collection.add_layer(1)

        layers_dict = collection.layers
        assert isinstance(layers_dict, dict)
        assert 0 in layers_dict
        assert 1 in layers_dict


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

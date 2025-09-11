from maxtikzlib.path import Path


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
                for node in item.nodes:
                    if not node.layer == self.label:
                        reqs.add(node.layer)
        return reqs

    def generate_tikz(self):
        tikz_script = f"\n% Layer {self.label}\n"
        tikz_script += f"\\begin{{pgfonlayer}}{{{self.label}}}\n"
        for item in self.items:
            tikz_script += item.to_tikz()
        print("add end!")
        tikz_script += f"\\end{{pgfonlayer}}{{{self.label}}}\n"
        return tikz_script

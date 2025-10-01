class TikzWrapper:
    def __init__(self, raw_tikz, label="", content="", layer=0, **kwargs):
        self.raw_tikz = raw_tikz
        self.label = label
        self.content = content
        self.layer = layer
        self.options = kwargs

    def to_tikz(self):
        return self.raw_tikz

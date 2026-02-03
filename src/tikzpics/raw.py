class RawTikz:
    def __init__(self, tikz_code: str):
        self.tikz_code = tikz_code

    def to_tikz(self) -> str:
        return self.tikz_code + "\n"

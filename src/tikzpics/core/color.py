class Color:
    def __init__(self, color_spec):
        """
        Initialize the Color object by parsing the color specification.

        Parameters:
        - color_spec: Can be a TikZ color string (e.g., 'blue!20'), a standard color name,
                      an RGB tuple, a hex code, etc.
        """
        self._color_spec = color_spec

    @property
    def color_spec(self):
        return self._color_spec

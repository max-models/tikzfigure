import re


class Linestyle:
    def __init__(self, style_spec):
        """
        Initialize the Linestyle object by parsing the style specification.

        Parameters:
        - style_spec: Can be a TikZ-style line style string (e.g., 'dashed', 'dotted', 'solid', 'dashdot'),
                      or a custom dash pattern.
        """
        self.style_spec = style_spec
        self.matplotlib_style = self._parse_style(style_spec)

    def _parse_style(self, style_spec):
        """
        Internal method to parse the style specification and convert it to a Matplotlib linestyle.

        Parameters:
        - style_spec: The style specification.

        Returns:
        - linestyle: A Matplotlib linestyle string or dash pattern.
        """
        # Predefined mappings from TikZ to Matplotlib
        linestyle_mapping = {
            "solid": "solid",
            "dashed": "dashed",
            "dotted": "dotted",
            "dashdot": "dashdot",
            # You can add more styles or custom dash patterns
        }

        # Check for predefined styles
        if style_spec in linestyle_mapping:
            return linestyle_mapping[style_spec]
        else:
            # Check if it's a custom dash pattern, e.g., 'dash pattern=on 5pt off 2pt'
            match = re.match(r"dash pattern=on ([\d.]+)pt off ([\d.]+)pt", style_spec)
            if match:
                on_length = float(match.group(1))
                off_length = float(match.group(2))
                # Matplotlib dash pattern is specified in points
                return (0, (on_length, off_length))
            else:
                # Default to solid if style is unknown
                print(f"Unknown line style: '{style_spec}', defaulting to 'solid'")
                return "solid"

    def to_matplotlib(self):
        """
        Return the line style in Matplotlib format.

        Returns:
        - linestyle: A Matplotlib linestyle string or dash sequence.
        """
        return self.matplotlib_style

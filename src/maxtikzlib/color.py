import re

import matplotlib.colors as mcolors
import numpy as np


class Color:
    def __init__(self, color_spec):
        """
        Initialize the Color object by parsing the color specification.

        Parameters:
        - color_spec: Can be a TikZ color string (e.g., 'blue!20'), a standard color name,
                      an RGB tuple, a hex code, etc.
        """
        self.color_spec = color_spec
        self.rgb = self._parse_color(color_spec)

    def _parse_color(self, color_spec):
        """
        Internal method to parse the color specification and convert it to an RGB tuple.

        Parameters:
        - color_spec: The color specification.

        Returns:
        - rgb: A tuple of (r, g, b) values, each between 0 and 1.
        """
        # If it's already an RGB tuple or list
        if isinstance(color_spec, (list, tuple)) and len(color_spec) == 3:
            # Normalize values if necessary
            rgb = tuple(float(c) / 255 if c > 1 else float(c) for c in color_spec)
            return rgb

        # If it's a hex code
        if isinstance(color_spec, str) and color_spec.startswith("#"):
            return mcolors.hex2color(color_spec)

        # If it's a TikZ color string
        match = re.match(r"(\w+)!([\d.]+)", color_spec)
        if match:
            base_color_name, percentage = match.groups()
            percentage = float(percentage)
            base_color = mcolors.to_rgb(base_color_name)
            white = np.array([1.0, 1.0, 1.0])
            mix = percentage / 100.0
            color = mix * np.array(base_color) + (1 - mix) * white
            return tuple(color)

        # Else, try to parse as a standard color name
        try:
            return mcolors.to_rgb(color_spec)
        except ValueError:
            raise ValueError(f"Invalid color specification: '{color_spec}'")

    def to_rgb(self):
        """
        Return the color as an RGB tuple.

        Returns:
        - rgb: A tuple of (r, g, b) values, each between 0 and 1.
        """
        return self.rgb

    def to_hex(self):
        """
        Return the color as a hex code.

        Returns:
        - hex_code: A string representing the color in hex format.
        """
        return mcolors.to_hex(self.rgb)

    def to_rgba(self, alpha=1.0):
        """
        Return the color as an RGBA tuple.

        Parameters:
        - alpha (float): The alpha (opacity) value between 0 and 1.

        Returns:
        - rgba: A tuple of (r, g, b, a) values.
        """
        return (*self.rgb, alpha)

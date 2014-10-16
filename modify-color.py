#!/bin/python
"""modify-color
------------
"""

import sys
import colorsys

def error(reason):
    print(reason)
    sys.exit(1)

class Color(object):
    """Color object, stores colors internally as RGB float"""
    def __init__(self, color_str, color_format="HEX"):
        self._rgb = (0, 0, 0)
        if color_format == "HEX":
            self._rgb = self._hex_to_rgb(color_str)

    @property
    def rgb_float(self):
        r, g, b = self._rgb

        return (round(r,3), round(g, 3), round(b, 3))

    def _hex_to_rgb(self, c):
        # Remove hash if necessary
        if c[0] == '#':
            c = c[1:]

        # Check length
        if len(c) != 6:
            error('Invalid hex input: %s' % (c))

        # Return RGB from hex
        try:
            rgb = (int(c[0:2], 16) / 255.0,
                   int(c[2:4], 16) / 255.0,
                   int(c[4:6], 16) / 255.0)
            return rgb
        except Exception:
            error('Invalid hex input: %s' % (c))

if __name__ == "__main__":
    if len(sys.argv) <= 1 or sys.argv[1] in ['help', '--help']:
        print(__doc__)
        sys.exit()

    c = Color(sys.argv[1])
    print(c.rgb_float)

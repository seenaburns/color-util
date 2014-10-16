#!/bin/python
"""modify-color
------------
"""

import sys
import colorsys

class Color(object):
    def __init__(self, color_str, color_format="hex"):
        pass

if __name__ == "__main__":
    if len(sys.argv) == 1 or sys.argv[1] in ['help', '--help']:
        print(__doc__)
        sys.exit()

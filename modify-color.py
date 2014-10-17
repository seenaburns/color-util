#!/bin/python
"""modify-color
------------
A color manipulation utility for the commandline.

Usage:
    modify-color [options] [<modifier> <amount>] color

Modifiers:
    Modifiers are specified by a type followed by an amount. Sequential
    modifiers are applied in the order they are specified.
    type:
      -h, --hue
      -s, --saturation
      -b, --brightness
      --red
      --green
      --blue

    amount examples:
      note: uses --in to distinguish when to use floats rather than 0-255
        (e.g. --in rgb_float --red +10 0,0,0 would return 1,0,0 not 11)
      +n    add
      -n    sub
      +n%   add percent
      -n%   sub percent
      n     set value
      n%    set percent (10% of 255 -> 25.5)

Options:
    --out [hex|rgb|hsb|rgb_float|hsb_float]
        specify what format to return the output color
        rgb and hsb by default a 3-element tuple with values from 0-255
        default: hex

    --in [hex|rgb|hsb|rgb_float|hsb_float]
        specify what format the input color is being given
        rgb and hsb by default a 3-element tuple with values from 0-255
        default: hex
"""

import sys
import colorsys
import re

def error(reason):
    print(reason)
    sys.exit(1)

class Color(object):
    """Color object, stores colors internally as RGB float"""
    def __init__(self, color_str, color_format="hex"):
        self._rgb = (0, 0, 0)
        if color_format == "hex":
            self._rgb = self._hex_to_rgb(color_str)

    @property
    def rgb_float(self):
        r, g, b = self._rgb

        return (round(r,3), round(g, 3), round(b, 3))

    @property
    def hex(self):
        # Convert from float to hex
        r, g, b = [self._float_to_hex(x) for x in self._rgb]

        return '#' + r + g + b

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

    def _float_to_hex(self, floatv):
        # Convert single float value to hex
        intv = int(round(floatv*255))
        
        # Hex, remove '0x', pad with 0
        hexv = hex(intv)[2:]
        if len(hexv) == 1:
            hexv = '0' + hexv

        return hexv.upper()

# Arugments
# Find arg_name in sys.argv and it's value
# return if accept(arg_value) is true, otherwise fail
# also pop arg_name/arg_value off of sys.argv
def arg_get(arg_name, accept, default):
    # Get index
    arg_index = 0
    try:
        arg_index = sys.argv.index(arg_name)
    except ValueError:
        return default

    # Get value
    arg_value = default
    try:
        arg_value = sys.argv[arg_index + 1]
    except IndexError:
        error("Value of '%s' not provided" % (arg_name))

    arg_value = arg_value.lower()

    # Check if value is in accepted list
    if not accept(arg_value):
        error("'%s' not accepted as a value for '%s', see --help" % (arg_value, arg_name))

    # Remove args from list
    sys.argv.pop(arg_index)
    sys.argv.pop(arg_index)

    return arg_value

if __name__ == "__main__":
    if len(sys.argv) <= 1 or sys.argv[1] in ['help', '--help']:
        print(__doc__)
        sys.exit()

    # Get formats args
    formats = ['hex','rgb','hsb','rgb_float','hsb_float']
    formats_accept = lambda x: x in formats;
    oformat = arg_get('--out', lambda x: x in formats, 'hex')
    iformat = arg_get('--in', lambda x: x in formats, 'hex')

    # Get modifiers args
    accepted_modifiers=['-h','--hue','-s','--saturation','-b','--brightness','--red','--green','--blue']
    modifier_accept = lambda x: re.search('^[\+\-]{0,1}[0-9\.]{1,}[%]{0,1}$', x) != None
    modifiers = []
    args = [x for x in sys.argv]
    for arg in args:
        if arg not in accepted_modifiers:
            continue
        modifiers.append((arg, arg_get(arg, modifier_accept, '+0')))

    # If flags remain error
    remaining_args = [x for x in sys.argv if x[0] == '-']
    if len(remaining_args) != 0:
        error('argument %s unrecognized' % (','.join(remaining_args)))

    c = Color(sys.argv[-1])

    # print result
    if oformat == 'hex':
        print(c.hex)
    if oformat == 'rgb':
        print(c.rgb_float)

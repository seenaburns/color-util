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
      note: n will always affect rgb/hue not the float version
        e.g. --red +10 for rgb 0.5,0,0 will be 138,0,0 not 1.0,0,0
      +n    add
      -n    sub
      +n%   add percent
      -n%   sub percent
      n     set value
      n%    set percent (10% of 255 -> 25.5)

Options:
    --out [hex|rgb|hsb|rgb_float|hsb_float]
        specify what format to return the output color
        default: hex

    --in [hex|rgb|hsb|rgb_float|hsb_float]
        specify what format the input color is being given
        default: hex

    formats:
      hex: #rrggbb
      rgb: 3 element tuple ranging from 0-255
        example: 0,255,100
      hsb: 3 element tuple, hue from 0-360, saturation/brightness from 0-100
        example: 360,100,50
      rgb_float: 3 element tuple, from 0.0-1.0
        example: 0.0, 1.0, 0.5
      hsb_float: 3 element tuple: from 0.0-1.0, note hue = 1.0 corresponds to hue = 360
        example: 1.0, 0.5, 0.2
            
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
        # Default
        self._rgb = (0, 0, 0)
        
        if color_format == "hex":
            self._rgb = self._hex_to_rgb(color_str)
        elif 'rgb' in color_format:
            # In format r,g,b
            is_float = color_format == 'rgb_float'
            try:
                # Extract
                r, g, b = [x for x in color_str.split(',')]
                r = self.normalize(r, 'red', is_float)
                g = self.normalize(g, 'green', is_float)
                b = self.normalize(b, 'blue', is_float)
                self._rgb = (r, g, b)
            except ValueError:
                error("Could not parse %s %s" % (color_format, color_str))
        elif 'hsb' in color_format:
            # In format h,s,b
            is_float = color_format == 'hsb_float'
            try:
                h, s, b = [x for x in color_str.split(',')]
                h = self.normalize(h, 'hue', is_float)
                s = self.normalize(s, 'saturation', is_float)
                b = self.normalize(b, 'brightness', is_float)
                self._rgb = colorsys.hsv_to_rgb(h,s,b)
            except ValueError:
                error("Could not parse %s %s" % (color_format, color_str))

    def modify(self, mtype, amount):
        # Define the operation
        operation = lambda x: x
        amount_value = float(''.join([char for char in amount if char in '0123456789.']))
        if amount[0] == '+':
            # add
            if amount[-1] == '%':
                operation = lambda x: x * (1+(amount_value)/100.0)
            else:
                operation = lambda x: x + amount_value
        elif amount[0] == '-':
            # sub
            if amount[-1] == '%':
                operation = lambda x: x * (1-(amount_value)/100.0)
            else:
                operation = lambda x: x - amount_value
        else:
            # set
            if amount[-1] == '%':
                operation = lambda x: amount_value
            else:
                operation = lambda x: x * (amount_value/100.0)

        norm_operation = lambda x, y: self.normalize(operation(x), y)

        # Apply operation
        if mtype == 'hue':
            self.hue = norm_operation(self.hue*360, 'hue')
        if mtype == 'saturation':
            self.saturation = norm_operation(self.saturation*100, 'saturation')
        if mtype == 'brightness':
            self.brightness = norm_operation(self.brightness*100, 'brightness')
        if mtype == 'red':
            self.red = norm_operation(self.red*255, 'red')
        if mtype == 'green':
            self.green = norm_operation(self.green*255, 'green')
        if mtype == 'blue':
            self.blue = norm_operation(self.blue*255, 'blue')

    @property
    def rgb_float(self):
        return self._rgb

    @property
    def hsb_float(self):
        r, g, b = self._rgb
        h, s, b = colorsys.rgb_to_hsv(r, g, b)
        return (h, s, b)
    @hsb_float.setter
    def hsb_float(self,value):
        h, s, b = value
        self._rgb = colorsys.hsv_to_rgb(h, s, b)

    @property
    def rgb(self):
        r, g, b = self._rgb
        return (int(round(r*255)), int(round(g*255)), int(round(b*255)))

    @property
    def hsb(self):
        h, s, b = self.hsb_float
        return (int(round(h*360)), int(round(s*100)), int(round(b*100)))

    @property
    def hex(self):
        # Convert from float to hex
        r, g, b = [self._float_to_hex(x) for x in self._rgb]
        return '#' + r + g + b

    # All individual properties are floats
    @property
    def hue(self):
        return self.hsb_float[0]
    @hue.setter
    def hue(self, value):
        h, s, b = self.hsb_float
        h = self.apply_float_bounds(value)
        self.hsb_float = (h, s, b)

    @property
    def saturation(self):
        return self.hsb_float[1]
    @saturation.setter
    def saturation(self, value):
        h, s, b = self.hsb_float
        s = self.apply_float_bounds(value)
        self.hsb_float = (h, s, b)

    @property
    def brightness(self):
        return self.hsb_float[2]
    @brightness.setter
    def brightness(self, value):
        h, s, b = self.hsb_float
        b = self.apply_float_bounds(value)
        self.hsb_float = (h, s, b)

    @property
    def red(self):
        return self.rgb_float[0]
    @red.setter
    def red(self, value):
        r, g, b = self.rgb_float
        r = self.apply_float_bounds(value)
        self._rgb = (r, g, b)

    @property
    def green(self):
        return self.rgb_float[1]
    @green.setter
    def green(self, value):
        r, g, b = self.rgb_float
        g = self.apply_float_bounds(value)
        self._rgb = (r, g, b)
    
    @property
    def blue(self):
        return self.rgb_float[2]
    @blue.setter
    def blue(self, value):
        r, g, b = self.rgb_float
        b = self.apply_float_bounds(value)
        self._rgb = (r, g, b)
        
    def str(self, color_tuple):
        return ('%s,%s,%s' % (color_tuple[0], color_tuple[1], color_tuple[2]))

    def round_floats(self, color_tuple):
        a, b, c = color_tuple
        return (round(a, 2), round(b, 2), round(c, 2))

    def normalize(self, v, vtype, is_float=False):
        # Normalize, e.g. for hue int(hue)/360
        # Skip floats
        if is_float:
            return self.apply_float_bounds(float(v))

        # Floats about 1 not allowed, e.g. no 45.3
        new_v = int(v)
        if vtype == 'hue':
            new_v /= 360.0
        elif vtype in ['brightness', 'saturation']:
            new_v /= 100.0
        elif vtype in ['red', 'blue', 'green']:
            new_v /= 255.0
        return self.apply_float_bounds(new_v)

    def apply_float_bounds(self, v):
        v = float(v)
        if v > 1.0:
            return 1.0
        elif v < 0:
            return 0.0
        return v
        

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

    # Create color from remaining arguments
    color_args = sys.argv[1:]
    if len(color_args) == 0:
        error("No color provided")
    color_str = ','.join(color_args)

    # Filter any unacceptable characters for non-hex iformats
    if iformat != 'hex':
        color_str = ''.join([char for char in color_str if char in '0123456789.,'])
    # Create color object
    c = Color(color_str, iformat)

    # Apply modifiers
    mod_mapping = {'-h': 'hue', '-s': 'saturation', '-b': 'brightness'}
    for m in accepted_modifiers:
        if '--' in m:
            mod_mapping[m] = m[2:]
    for m in modifiers:
        c.modify(mod_mapping[m[0]], m[1])

    # print result
    format_mapping = {'hex': c.hex,
                      'rgb': c.str(c.rgb),
                      'rgb_float': c.str(c.round_floats(c.rgb_float)),
                      'hsb': c.str(c.hsb),
                      'hsb_float': c.str(c.round_floats(c.hsb_float))}
    print(format_mapping[oformat])

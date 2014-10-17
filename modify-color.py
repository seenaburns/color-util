#!/bin/python
"""modify-color
------------
A color manipulation utility for the commandline.

Usage:
    modify-color [options] [<modifier> <amount>] color

Examples:
    echo "#001122" | modify-color --out hsb --brightness +10%
    modify-color --in rgb --out rgb_float 125,255,50
    modify-color --red 100 FF3377
    modify-color --hue 360 --brightness 100 --saturation 50 "#000000" | modify-color --red +10%

Color:
    Format specified by --in, can be passed in as an argument or through stdin.
    See Examples.

Modifiers:
    Modifiers are specified by a type followed by an amount. Order is not
    guaranteed, so if it is required, pipe to another call. Also because 
    modifying hsb and rgb can interfere with each other when converting,
    only modify red,green,blue or hue,saturation,brightness in one call
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
        # Internal values, stored as integer numbers
        # red,green,blue from [0-255]
        # hue from [0-360]
        # saturation, brightness from [0-100]
        self.red = 0
        self.green = 0
        self.blue = 0
        self.hue = 0
        self.saturation = 0
        self.brightness = 0
        # If input/modify mode is rgb, derive hsb from rgb
        # otherwise derive rgb from hsb
        self.input_mode = 'rgb'
        self.modify_mode = ''

        # Input hex
        if color_format == "hex":
            r, g, b = self._hex_to_rgb(color_str)
            self.red = self.float_to_int(r, 'red')
            self.green = self.float_to_int(g, 'green')
            self.blue = self.float_to_int(b, 'blue')

        # Input rgb/rgb_float
        elif 'rgb' in color_format:
            # In format r,g,b
            try:
                # Extract
                r, g, b = [float(x)for x in color_str.split(',')]
                # Convert floats to ints if neccessary
                if color_format == 'rgb_float':
                    r = self.float_to_int(r, 'red')
                    g = self.float_to_int(g, 'green')
                    b = self.float_to_int(b, 'blue')
                self.red = r
                self.green = g
                self.blue = b
            except ValueError:
                error("Could not parse %s %s" % (color_format, color_str))

        # Input hsb/hsb_float
        elif 'hsb' in color_format:
            # In format h,s,b
            self.input_mode = 'hsb'
            try:
                h, s, b = [float(x) for x in color_str.split(',')]
                # Convert floats to ints if neccessary
                if color_format == 'hsb_float':
                    h = self.float_to_int(h, 'hue')
                    s = self.float_to_int(s, 'saturation')
                    b = self.float_to_int(b, 'brightness')
                self.hue = h
                self.saturation = s
                self.brightness = b
            except ValueError:
                error("Could not parse %s %s" % (color_format, color_str))

        # Derive hsb/rgb from the other
        self.flush(self.input_mode)

    def __str__(self):
        return "[%s, %s, %s, %s, %s, %s, %s]" % (self.red,self.green,self.blue,self.hue,self.saturation,self.brightness,self.hex)

    def __repr__(self):
        return self.__str__()

    def modify(self, mtype, amount):
        new_mode = 'rgb' if mtype in ['red', 'blue', 'green'] else 'hsb'
        if new_mode != self.modify_mode and self.modify_mode != '':
            error("Cannot modify both [red|green|blue] and [hue|saturation|brightness] in one call, see --help")
        self.modify_mode = new_mode

        # Apply changes to values
        operation = self.construct_modify_operation(amount)
        
        # Apply operation to values
        if mtype == 'hue':
            self.hue = operation(self.hue)
        if mtype == 'saturation':
            self.saturation = operation(self.saturation)
        if mtype == 'brightness':
            self.brightness = operation(self.brightness)
        if mtype == 'red':
            self.red = operation(self.red)
        if mtype == 'green':
            self.green = operation(self.green)
        if mtype == 'blue':
            self.blue = operation(self.blue)

    def construct_modify_operation(self, amount):
        # construct and return an operation function based on amount
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
                operation = lambda x: x * (amount_value/100.0)
            else:
                operation = lambda x: amount_value

        return operation

    def flush(self, mode):
        # if mode is rgb, update hsb values from rgb
        # if mode is hue, update rgb values from hsb
        if mode == '':
            mode = self.input_mode
        if mode == 'rgb':
            h, s, b = colorsys.rgb_to_hsv(self.red/255.0, self.green/255.0, self.blue/255.0)
            self.hue = self.float_to_int(h, 'hue') 
            self.saturation = self.float_to_int(s, 'saturation')
            self.brightness = self.float_to_int(b, 'brightness')
        elif mode == 'hsb':
            r, g, b = colorsys.hsv_to_rgb(self.hue/360.0, self.saturation/100.0, self.brightness/100.0)
            self.red = self.float_to_int(r, 'red')
            self.green = self.float_to_int(g, 'green')
            self.blue = self.float_to_int(b, 'blue')
        else:
            raise Exception("mode not recognized")

        self.apply_bounds()

    def apply_bounds(self):
        bound = lambda x,minx,maxx: min(max(minx,x), maxx)
        self.red = bound(self.red, 0, 255)
        self.green = bound(self.green, 0, 255)
        self.blue = bound(self.blue, 0, 255)
        self.hue = bound(self.hue, 0, 360)
        self.saturation = bound(self.saturation, 0, 100)
        self.brightness = bound(self.brightness, 0, 100)


    @property
    def rgb(self):
        self.flush(self.modify_mode)
        return int(self.red), int(self.green), int(self.blue)

    @property
    def rgb_float(self):
        return tuple([round(x/255.0,2) for x in self.rgb])

    @property
    def hsb(self):
        self.flush(self.modify_mode)
        return int(self.hue), int(self.saturation), int(self.brightness)

    @property
    def hsb_float(self):
        h, s, b = self.hsb
        return tuple([round(x, 2) for x in (h/360.0, s/100.0, b/100.0)])

    @property
    def hex(self):
        # Convert from float to hex
        r, g, b = [self._float_to_hex(x/255.0) for x in self.rgb]
        return '#' + r + g + b

        
    def str(self, color_tuple):
        return ('%s,%s,%s' % (color_tuple[0], color_tuple[1], color_tuple[2]))

    def round_floats(self, color_tuple):
        a, b, c = color_tuple
        return (round(a, 2), round(b, 2), round(c, 2))

    def float_to_int(self, v, vtype):
        bounded = lambda x: min(max(x, 0),1)
        fti = lambda x: int(round( bounded(v) * x))
        if vtype == 'hue':
            return fti(360.0)
        elif vtype in ['saturation', 'brightness']:
            return fti(100.0)
        elif vtype in ['red', 'blue', 'green']:
            return fti(255.0)
        else:
            raise Exception("Unknown vtype %s" % (vtype))

    def apply_float_bounds(self, v):
        v = float(v)
        if v > 1.0:
            return 1.0
        elif v < 0:
            return 0.0
        return v
        

    def _hex_to_rgb(self, c):
        # Remove hash if necessary, extraneous whitespace
        c = c.strip()
        if len(c) == 0:
            error('Invalid hex input: %s' % (c))
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

    # Create color from remaining arguments or by reading stdin
    color_args = sys.argv[1:]
    color_str = ''
    if len(color_args) == 0:
        color_str = sys.stdin.read()
    else:
        color_str = ','.join(color_args)
    if len(color_str) == 0:
        error("No color provided (either stdin or as argument)")

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

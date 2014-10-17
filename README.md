color-util
============

A color manipulation utility for the command-line.

color-util takes a starting color and a series of commands to the modify red, green, blue, hue, saturation and/or brightness by a given amount and then returns the resulting color.

For example, let's make red (#FF0000) into green (#00FF00):

```
$ color-util --red 0 --green 255 "#FF0000"
#00FF00
```

Requires Python (tested in 2.7.8 and 3.4.2).

Usage
---

```
color-util [options] [<modifier> <amount>] color
```

Modifiers are specified by a type and an amount.

**Types:**
```
-h, --hue
-s, --saturation
-b, --brightness
--red
--green
--blue
```
**Amounts:**
```
+n    add            (100 +10 -> 110)
-n    sub            (100 -10 -> 90)
+n%   add percent    (100 +50% -> 150, or 100*1.5)
-n%   sub percent    (100 -50% -> 50, or 100*0.5)
n     set value      (100 10 -> 10)
n%    set percent    (100 40% -> 40, or 100*0.4)
```

See --help for more documentation.

Examples
---

From a hex value, manipulate the rgb by adding 50% to red, subtract 10 from green, set blue to 10
```
$ color-util --red +50% --green -10 --blue 10 "#777777"
#B26D0A
```

Read from stdin, accepting a rgb_float tuple and outputing in hsb after increasing the brightness by 10%
```
$ echo "0.0,0.07,0.13" | color-util --in rgb_float --out hsb --brightness +10%
207,100,14
```

Find all hex values in the file, for each set the hue to 148 (a greenish tone)
```
$ grep -o '#[0-9A-Fa-f]\{6\} file.txt | xargs -I % color-util --hue 148 
#33453B
#4F6659
#647D70
#8FB29F
#96B5A5
...
```

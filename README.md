color-util
============

A color manipulation utility for the command-line. Given a color, it can modify the red,green,blue,hue,saturation,brightness properties and output the resulting color.


Usage
---

    color-util [options] [<modifier> <amount>] color

See --help for documentation.

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
$ grep '#[0-9A-Fa-f]\{6\} file.txt | xargs -I % color-util --hue 148 
#33453B
#4F6659
#647D70
#8FB29F
#96B5A5
...
```

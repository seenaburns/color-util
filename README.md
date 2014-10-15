modify-color
============

A color manipulation utility for the commandline.


Usage
---

    modify-color [options] [<modifier> <amount>] color

See --help for documentation.

Examples
---

From a hex value, manipulate the rgb by adding 50% to red, subtract 10 from green, set blue to 10
```
$ modify-color --red +50% --green -10 --blue 10 "#777777"
#B26D0A
```

Read from stdin, accepting a rgb_float tuple and outputing in hsb after increasing the brightness by 10%
```
$ echo "0.0,0.07,0.13" | modify-color --in rgb_float --out hsb --brightness +10%
207,100,14
```

Find all hex values in the file, for each set the hue to 148 (a greenish tone)
```
$ grep '#[0-9A-Fa-f]\{6\} file.txt | xargs -I % modify-color --hue 148 
#33453B
#4F6659
#647D70
#8FB29F
#96B5A5
...
```

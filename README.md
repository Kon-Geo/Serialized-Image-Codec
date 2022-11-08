# Serialized Image Codec:
Serialized Image Codec is an open source conversion software for images. It's purpose is to create a new image codec that gives the user the ability to directly edit the image using a text editor.

# How It Works (Technical Details):
## Without Compression (SIC Converter):
The program takes every pixel in the image and gets the hexadecimal value of it. It creates a new text file where each line represents a row of pixels and every value between commas is the hexadecimal value of the corresponding pixel.
## With Compression (CSIC Converter):
* The program finds the 35 most frequent pixels in the image and creates a map of them which is stored in the first line of the text file. Every occurrence of one of the most frequent pixels gets replaced by a spelial character assigned to every pixel in the map
* The program replaces consecutive repeating occurunces of hexadecimal or special character values and writes them in the form of a value multiplied by the number of consecutive occurences. (value*occurrences)

# Converter Usage:
## Command
```bash
main.py [-h] [-i INPUT FILENAME/PATH] [-o OUTPUT FILENAME/PATH] [-e] [-d] [-r WIDTHxHEIGHT] [-c {csic,sic}] [-v]
```

## Arguments:
```
-h, --help    show a help message and exit
-i INPUT FILENAME/PATH, --input INPUT FILENAME/PATH    Filename or path of input file.
-o OUTPUT FILENAME/PATH, --output OUTPUT FILENAME/PATH    Filename or path of output file.
-e, --encode    Use encode mode.
-d, --decode    Use decode mode.
-r WIDTHxHEIGHT, --random WIDTHxHEIGHT    Generate random PNG image.
-c {0,1}, --complevel {0,1}    The compression level you want to use (0=No Compression)
-v, --verbose    Print useful information to the console.
```
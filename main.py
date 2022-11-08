from argparse import ArgumentParser
from cv2 import imread, imwrite
from numpy import zeros, uint8
from numpy.random import randint
from time import time

class SIC():
    def __init__(self, input_file, mode="encode", output_file=None):
        start = time() # Store start time
        # Create or store existant output filename or path
        if not output_file: output_file = ".".join((input_file or "").split(".")[0:-1]) + (".sic" if mode == "encode" else ".png")
        # Check mode and execute the coresponding function
        if mode == "encode": self.encode(input_file, output_file)
        if mode == "decode": self.decode(input_file, output_file)
        # Print time taken to complete
        if verbose: print(f"Completed in %.2f seconds" % (time() - start))

    def encode(self, input_file, output_file):
        # Open input file and get the dimensions
        img = imread(input_file)
        rows, cols, _ = img.shape
        # Create dictionary and list to save most frequent hex value and rows of the image
        frequencies = {}
        buffer_lines = []
        # Iterate through the rows and columns of the image
        for i in range(rows):
            buffer_lines.append("")
            for j in range(cols):
                if verbose: print(f"X{i} Y{j}", end="\r") # Print current row and column
                # Convert rgb value of pixel to hexadecimal
                pixel = img[i, j]
                hex_value = ('%02x%02x%02x' % (pixel[0], pixel[1], pixel[2])).upper()
                # Save pixel in the curent line of the buffer and in the frequency map
                buffer_lines[i] += hex_value + ","
                if complevel >= 1: frequencies[hex_value] = frequencies.get(hex_value, 0) + 1
            buffer_lines[i] = buffer_lines[i][:-1] # Remove trailing comma
        # Create a map of the first 35 most freuqent hexadecimal pixel values
        most_frequent = [[chr(91 + i), j[0]] for i, j in enumerate([k for k in sorted(frequencies.items(), key=lambda item: item[1], reverse=True)][0:35])]
        if complevel == 2:
            # Iterate the lines of the buffer
            for i, line in enumerate(buffer_lines):
                count = 1
                occurrences = []
                # Find consecutive repeating pixel values
                if len(line) > 1:
                    splitted = line.split(",")
                    for j, text in enumerate(splitted):
                        if j + 1 != len(splitted) and text == splitted[j+1]:
                            count += 1
                        else:
                            occurrences.append([text, str(count)])
                            count = 1
                else:
                    occurrences.append([line, "1"])
                # Merge the consecutive repeating pixel values by writing them as 'value*times_found'
                buffer_lines[i] = ",".join(map(lambda l: l[0] if l[1] == "1" else "*".join(l), occurrences))
        # Join the lines of the buffer into a single 'buffer' string
        buffer = "\n".join(buffer_lines)
        # Replace the original hexadecimal values with the shorthands of the frequncy map
        if complevel >= 1:
            for l, v in most_frequent: buffer = buffer.replace(v, l)
        # Create the new image file and write the frequency map and buffer to it
        with open(output_file, "w+") as wf:
            if complevel >= 1: wf.write(",".join([f"{i}:{j}" for i, j in most_frequent]) + "\n")
            wf.write(buffer)

    def decode(self, input_file, output_file):
        # Open input file
        with open(input_file, "r") as rf:
            # Read the data in lines
            lines = rf.readlines()
            # Read the frequency map in the first line
            frequency_map = [[*i.split(":")] for i in lines[0][:-1].split(",")]
            data = ""
            # Replace the shorthand pixel values of each row with the original hexadecimal values and save them to the 'data' variable
            for line in lines[1:]:
                temp = line
                for k, v in frequency_map:
                    temp = temp.replace(k, v)
                data += temp
            # Split data back into lines
            data = data.split("\n")
            # Iterate the rows again and decode the short written consecutive repeating pixel values
            for i, line in enumerate(data):
                decoded_pixels = []
                for pixel in line.split(","):
                    # If the asterisc character is not present in the pixel immediately append it to the decoded pixels
                    # Else decode the pixel by multiplying the pixel value in the left of the asterisc with the factor in the right
                    if "*" not in pixel:
                        decoded_pixels.append(pixel)
                    else:
                        value, factor = pixel.split("*")
                        decoded_pixels.append(",".join([value] * int(factor)))
                # Join the pixel into a single string representing the row
                data[i] = ",".join(decoded_pixels)
        # Create a blank numpy array serving as the new image
        new_image = zeros((len(data), len(data[0].split(",")), 3), uint8)
        # Iterate through the rows and columns of the decoded input image and and change them accordingly in the new image
        for i, line in enumerate(data):
            for j, y in enumerate(line.split(",")):
                new_image[i][j] = tuple(int(y[i:i+2], 16) for i in (0, 2, 4))
        # Save the new image
        imwrite(output_file, new_image)

class Parser(ArgumentParser):
    def __init__(self):
        super().__init__()
        # Add arguments
        self.add_argument("-i", "--input", help="Filename or path of input file.", metavar="INPUT FILENAME/PATH")
        self.add_argument("-o", "--output", help="Filename or path of output file.", metavar="OUTPUT FILENAME/PATH")
        self.add_argument("-e", "--encode", action="store_const", const="encode", help="Use encode mode.")
        self.add_argument("-d", "--decode", action="store_const", const="decode", help="Use decode mode.")
        self.add_argument("-r", "--random", help="Generate random PNG image.", metavar="WIDTHxHEIGHT")
        self.add_argument("-c", "--complevel", help="The compression level you want to use (0=No Compression)", choices=range(0, 3), default=0, type=int)
        self.add_argument("-v", "--verbose", help="Print useful information to the console.", action="store_true")
        args = self.parse_args()
        # Create a global variable with the value of the verbose argument and print warning message if verbose mode is enabled
        global verbose
        verbose = args.verbose
        global complevel
        complevel = args.complevel
        if verbose: print("WARNING: Verbose mode slows down the process significantly!")
        # If random is enabled then generate a random image of given dimensions
        # Else check if the input file argument is present, if not print error and exit the program
        if args.random:
            imwrite('random.png', randint(255, size=(*map(lambda x: int(x), args.random.split("x")), 3), dtype=uint8))
            return
        elif not args.input:
            print("error: the following argument is required: -i/--input")
            return
        # Check the converter the user wants to use and pass the argument to the corresponding class
        SIC(args.input, args.encode or args.decode or "encode", args.output)

# If the program is run as is and not imported then start the program
if __name__ == "__main__":
    Parser()
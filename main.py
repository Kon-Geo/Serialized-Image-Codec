from argparse import ArgumentParser
from cv2 import imread, imwrite
from numpy import zeros, uint8
from time import time

class CSIC():
    def __init__(self, input_file, mode="encode", output_file=None):
        start = time()
        if not output_file: output_file = ".".join((input_file or "").split(".")[0:-1]) + (".csic" if mode == "encode" else ".png")
        if mode == "encode": self.encode(input_file, output_file)
        if mode == "decode": self.decode(input_file, output_file)
        if verbose: print(f"Completed in %.2f seconds" % (time() - start))

    def encode(self, input_file, output_file):
        img = imread(input_file)
        rows, cols, _ = img.shape
        frequencies = {}
        buffer = ""
        for i in range(rows):
            for j in range(cols):
                if verbose: print(f"X{i} Y{j}", end="\r")
                pixel = img[i, j]
                hex_value = ('%02x%02x%02x' % (pixel[0], pixel[1], pixel[2])).upper()
                buffer += hex_value + ","
                frequencies[hex_value] = frequencies.get(hex_value, 0) + 1
            buffer = buffer[:-1] + "\n"
        buffer = buffer[:-1]
        most_frequent = [[chr(91 + i), j[0]] for i, j in enumerate([k for k in sorted(frequencies.items(), key=lambda item: item[1], reverse=True)][0:35])]
        with open(output_file, "w+") as wf:
            wf.write(",".join([f"{i}:{j}" for i, j in most_frequent]))
            wf.write("\n")
            for l, v in most_frequent: buffer = buffer.replace(v, l)
            wf.write(buffer)

    def decode(self, input_file, output_file):
        with open(input_file, "r") as rf:
            lines = rf.readlines()
            frequency_map = [[*i.split(":")] for i in lines[0][:-1].split(",")]
            data = ""
            for line in lines[1:]:
                temp = line
                for k, v in frequency_map:
                    temp = temp.replace(k, v)
                data += temp
            data = data.split("\n")
            height = len(data)
            width = len(data[0].split(","))
        new_image = zeros((height, width, 3), uint8)
        for i, line in enumerate(data):
            for j, y in enumerate(line.split(",")):
                new_image[i][j] = tuple(int(y[i:i+2], 16) for i in (0, 2, 4))
        imwrite(output_file, new_image)

class SIC():
    def __init__(self, input_file, mode="encode", output_file=None):
        start = time()
        if not output_file: output_file = ".".join((input_file or "").split(".")[0:-1]) + (".sic" if mode == "encode" else ".png")
        if mode == "encode": self.encode(input_file, output_file)
        if mode == "decode": self.decode(input_file, output_file)
        if verbose: print(f"Completed in %.2f seconds" % (time() - start))

    def encode(self, input_file, output_file):
        img = imread(input_file)
        rows, cols, _ = img.shape
        buffer = ""
        for i in range(rows):
            for j in range(cols):
                if verbose: print(f"X{i} Y{j}", end="\r")
                pixel = img[i, j]
                hex_value = ('%02x%02x%02x' % (pixel[0], pixel[1], pixel[2])).upper()
                buffer += hex_value + ","
            buffer = buffer[:-1] + "\n"
        buffer = buffer[:-1]
        with open(output_file, "w+") as wf: wf.write(buffer)

    def decode(self, input_file, output_file):
        with open(input_file, "r") as rf: data = rf.readlines()
        new_image = zeros((len(data), len(data[0].split(",")), 3), uint8)
        for i, line in enumerate(data):
            for j, y in enumerate(line.split(",")):
                new_image[i][j] = tuple(int(y[i:i+2], 16) for i in (0, 2, 4))
        imwrite(output_file, new_image)

class Parser(ArgumentParser):
    def __init__(self):
        super().__init__()
        self.add_argument("-i", "--input", required=True, help="Filename or path of input file.")
        self.add_argument("-e", "--encode", action="store_const", const="encode", help="Use encode mode.")
        self.add_argument("-d", "--decode", action="store_const", const="decode", help="Use decode mode.")
        self.add_argument("-o", "--output", help="Filename or path of output file.")
        self.add_argument("-c", "--converter", help="The converter you want to use. (csic = Compressed Serialized Image Coded | sic = Serialized Image Codec)", choices=["csic", "sic"], default="csic")
        self.add_argument("-v", "--verbose", help="Print useful information to the console.", action="store_true")
        args = self.parse_args()
        global verbose
        verbose = args.verbose
        if verbose: print("WARNING: Verbose mode slows down the process significantly!")
        if args.converter == "csic": CSIC(args.input, args.encode or args.decode, args.output)
        if args.converter == "sic": SIC(args.input, args.encode or args.decode, args.output)

if __name__ == "__main__":
    Parser()
import argparse
import struct
import sys


# Assumes little-endianness
def sac_reader(filename):
    data = []
    with open(filename.strip(), "rb") as input_file:
        # Read the header information
        try:
            # Get beginning value of the independent variable
            input_file.seek(20)
            binary = struct.unpack("<f", input_file.read(4))
            # Get LEVEN variable to see if data is evenly spaced
            input_file.seek(420)
            leven = struct.unpack("<i", input_file.read(4))
            if not leven:
                print("The data in this SAC file is not evenly spaced.")
                sys.exit(2)
            # Get the increment between evenly spaced samples
            input_file.seek(0)
            delta = struct.unpack("<f", input_file.read(4))
            # Get all of the data and store it to memory
            input_file.seek(632)
            byte = input_file.read(4)
            while byte != "":
                data.append(struct.unpack("<f", byte)[0])
                byte = input_file.read(4)
        except Exception as err:
            raise err
    return (data, binary[0], delta[0])


def main():
    # Create the command-line options
    parser = argparse.ArgumentParser(description="Read SAC file for plotting")
    args = parser.parse_args()
    if len(args) != 1:
        parser.error("Incorrect number of arguments")

    sac_reader(sys.argv[1:][0])


if __name__ == "__main__":
    main()

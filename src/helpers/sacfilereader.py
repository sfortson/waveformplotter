import struct
import sys
from optparse import OptionParser


# Assumes little-endianness
def sac_reader(filename):
    data = []
    f = open(filename.strip(), "rb")
    # Read the header information
    try:
        # Get beginning value of the independent variable
        f.seek(20)
        b = struct.unpack("<f", f.read(4))
        # Get LEVEN variable to see if data is evenly spaced
        f.seek(420)
        leven = struct.unpack("<i", f.read(4))
        if not leven:
            print("The data in this SAC file is not evenly spaced.")
            sys.exit(2)
        # Get the increment between evenly spaced samples
        f.seek(0)
        delta = struct.unpack("<f", f.read(4))
        # Get all of the data and store it to memory
        f.seek(632)
        byte = f.read(4)
        while byte != "":
            data.append(struct.unpack("<f", byte)[0])
            byte = f.read(4)
    finally:
        f.close()
    return (data, b[0], delta[0])


def main():
    # Create the command-line options
    usage = "usage: %prog [-h] filename"
    parser = OptionParser(
        usage=usage, description="Read SAC file for plotting"
    )
    (_, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("Incorrect number of arguments")

    sac_reader(sys.argv[1:][0])


if __name__ == "__main__":
    main()

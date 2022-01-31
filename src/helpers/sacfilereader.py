"""Helper module for common rdseed and sac operations."""

import argparse
import struct
import sys
from typing import Any, List, Tuple


# pylint: disable=line-too-long
def rdseed_name(seed_name: str, start_time: str, end_time: str, channels="") -> str:
    """Get rdseed CLI tool and args to run as subprocess

    :param seed_name: Name of SEED file
    :type seed_name: str
    :param start_time: Start time
    :type start_time: str
    :param end_time: End time
    :type end_time: str
    :param channels: Channel names, defaults to ""
    :type channels: str, optional
    :return: rdseed CLI tool and args to run as subprocess
    :rtype: str
    """
    return (
        "echo"
        f" '{seed_name}\n\n\n\n\n\n{channels}\n\n\n\n\n\n\n\n{start_time}\n{end_time}\n\n\nQuit\n'|"
        " rdseed"
    )


# Assumes little-endianness
def sac_reader(filename: str) -> Tuple(List[float], Any, Any):
    """Read SAC file.

    :param filename: SAC file name to read
    :type filename: str
    :raises err: Raise error if there is an issue reading the SEED file
    :return: Tuple of list of data, binary, and delta information
    :rtype: Tuple(List[float], Any, Any)
    """
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


def main() -> None:
    """Main driver for creating command line arguments and calling sac
    reader if running this as a stand-alone tool.
    """
    parser = argparse.ArgumentParser(description="Read SAC file for plotting")
    args = parser.parse_args()
    if len(args) != 1:
        parser.error("Incorrect number of arguments")

    sac_reader(sys.argv[1:][0])


if __name__ == "__main__":
    main()

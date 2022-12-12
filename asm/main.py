# Standard
import sys
import os

# Local
from utils.module import Module


def print_help() -> None:
    """Print a help message"""

    print("----")
    print("HELP")
    print("----")


def main(args: list[str]) -> int:
    """The main function of the assembler"""
    
    if len(args) < 2:
        print("Missing file argument! Type '-h' for help ...")
        return 1

    if "-h" in args:
        print_help()
        return 0

    file = args[-1]

    if not os.path.exists(file):
        print("Invalid file path! File don't exists. Type '-h' for help ...")
        return 1
    if not os.path.isfile(file):
        print("Invalid file path! Not a file. Type '-h' for help ...")
        return 1
    if os.path.splitext(file)[1] not in (".asm", ".asmn1"):
        print("Invalid file type! File extension needs to be '.asm'. Type '-h' for help ...")
        return 1

    main = Module.file(file)

    return 0


# Main
if __name__ == "__main__":

    sys.exit(main(sys.argv))


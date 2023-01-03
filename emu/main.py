# Standard modules
import sys
import os

# Environment variables
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = ""

# Path
sys.path.append(os.path.abspath("../common"))

# Local modules
from common import *
from win import Win
from n1 import N1


class Global:
    """Global information"""

    def __init__(self):

        self.debug: bool = False
        self.path: str = ""

        self.win: Win = None

        self.n1: N1 = None


def print_help() -> None:
    """Print a help message"""

    print("-----------------------")
    print("N1 TOOLCHAIN - EMULATOR")
    print("-----------------------")
    print()
    print("--- Usage ---")
    print()
    print("python emu.py [-h/--help] [-d/--debug] path")
    print()
    print("-h/--help     Show this help message")
    print("-d/--debug    Print debug information")
    print()
    print("path          File path of .n1 file to execute")
    print()


def main(args: list[str]) -> int:
    """Main function of the emulator"""

    if "-h" in args or "--help" in args:
        print_help()
        return 0

    glob: Global = Global()

    glob.debug = "-d" in args or "--debug" in args

    if glob.debug:
        if "-d" in args:
            args.remove('-d')
        if "--debug" in args:
            args.remove('--debug')

    if len(args) < 2:
        print("Missing file argument! Add '-h' or '--help' for help ...")
        return 1

    glob.path = os.path.abspath(args[-1])

    if not os.path.exists(glob.path):
        print("Invalid file path! File don't exists. Add '-h' or '--help' for help ...")
        return 1
    if not os.path.isfile(glob.path):
        print("Invalid file path! Not a file. Add '-h' or '--help' for help ...")
        return 1

    with open(glob.path, 'r') as f:
        code = f.read()

    glob.n1 = N1()
    glob.n1.load_rom(code)

    glob.win = Win(glob)
    glob.win.start()

    print(glob.n1.rom)

    return 0


# Main
if __name__ == "__main__":
    sys.exit(main(sys.argv))


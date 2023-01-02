# Standard modules
import sys


class N1:

    def __init__(self):

        self.registers = {"a": 0, "b": 0, "c": 0, "d": 0, "h": 0, "l": 0, "z": 0}
        self.mb = 0
        self.sp = 0xF000
        self.pc = 0
        self.rom = {}
        self.bank = {0: {}, 1: {}}
        self.ram = {}
        self.stack = {}
        self.exit = -1


def main(args: list[str]) -> int:
    """Main function of the emulator"""

    return 0


# Main
if __name__ == "__main__":
    sys.exit(main(sys.argv))


# Standard
import sys
import os

# Local
from errors import *
from instruction import Instruction
from module import Module


def main(args: list[str]) -> int:
    """The main function of the assembler"""
    
    if len(args) < 2:
        return "Missing arguments! Type '-h' for help ..."

    file = args[-1]

    if not os.path.exists(file):
        raise InvalidArgumentError("Invalid path to program! Type '-h' for help ...")
    if os.path.splitext(file)[1] != ".asm":
        raise InvalidArgumentError("Invalid file type! Need '*.asm' file! Type '-h' for help ...")

    module = Module.file(file)
    print(module.namespace)
    print(module.lines)
    print(module.instructions)
    print(module.modules)
    print(module.macros)

    return 0


# Main
if __name__ == "__main__":
    sys.exit(main(sys.argv))


# Standard
import sys
import os

# Local
from utils.module import Module
from utils.token import Token, TokenType, token_list_remove
from utils.error import Error, ErrorType


STDLIB = os.path.dirname(__file__) + "/stdlib"


def print_help() -> None:
    """Print a help message"""

    print("----")
    print("HELP")
    print("----")


def get_path(main_path: str, path: str) -> str:
    """Get the real path"""

    main_path = os.path.dirname(main_path)

    if os.path.exists(path):
        return os.path.abspath(path)

    if os.path.exists(path + ".asm"):
        return os.path.abspath(path + ".asm")

    if os.path.exists(path + ".asmn1"):
        return os.path.abspath(path + ".asmn1")

    if os.path.exists(main_path + "/" + path):
        return os.path.abspath(main_path + "/" + path)

    if os.path.exists(main_path + "/" + path + ".asm"):
        return os.path.abspath(main_path + "/" + path + ".asm")

    if os.path.exists(main_path + "/" + path + ".asmn1"):
        return os.path.abspath(main_path + "/" + path + ".asmn1")

    if os.path.exists(STDLIB + "/" + path):
        return os.path.abspath(STDLIB + "/" + path)

    if os.path.exists(STDLIB + "/" + path + ".asm"):
        return os.path.abspath(STDLIB + "/" + path + ".asm")

    if os.path.exists(STDLIB + "/" + path + ".asmn1"):
        return os.path.abspath(STDLIB + "/" + path + ".asmn1")


def load_module(modules: dict[str, Module], path: str, debug: bool, main_path: str, main: bool = False) -> None:
    """Load a module"""

    print(f"Load module '{path}'")

    module = Module.file(path, modules, main)

    print("Tokenize ...")
    module.tokenize()

    if debug:
        for line in module.token_lines:
            for token in line:
                print(token)

    print("Parse ...")
    module.parse()

    if debug:
        for include in module.includes:
            print(include)
        for export in module.exports:
            print(export)
        for constant in module.constants:
            print(constant)
        for variable in module.variables:
            print(variable)
        for resource in module.resources:
            print(resource)
        for macro in module.macros:
            print(macro)
        for instruction in module.instructions:
            print(instruction)
        for label in module.labels:
            print(label)

    modules[path] = module

    if os.path.abspath(STDLIB + "/builtins.asmn1") not in modules:
        load_module(modules, os.path.abspath(STDLIB + "/builtins.asmn1"), debug, main_path)

    if path != os.path.abspath(STDLIB + "/builtins.asmn1"):
        module.include_paths.append(path)

    for include in module.includes:

        if len(include.path) == 1 and include.path[0].type == TokenType.STRING:
            path = get_path(main_path, include.path[0].value)
        elif token_list_remove(token_list_remove(include.path, TokenType.SLASH), TokenType.NAME):
            Error(module, include.path[0].line, ErrorType.SYNTAX,
                  "Invalid include definition!\n" +
                  "One string or a combination of names and slashes is expected.").exit()
        else:
            path = ""
            for token in include.path:
                path += token.value if token.type == TokenType.NAME else "/"
            path = get_path(main_path, path)

        if path is None:
            Error(module, include.path[0].line, ErrorType.INCLUDE,
                  "Module not found!").exit()

        module.include_paths.append(path)

        if path not in modules:
            load_module(modules, path, debug, main_path)


def mode_default(file: str, override: bool, debug: bool) -> int:

    if os.path.splitext(file)[1] not in (".asm", ".asmn1"):
        print("Invalid file type! File extension needs to be '.asm' or '.asmn1'. Type '-h' for help ...")
        return 1

    if not override:
        for path in (os.path.splitext(file)[0] + ".n1",):
            if os.path.exists(path):
                print(f"The file '{path}' already exists. Use '-o' to overwrite it ...")
                return 1

    print(f"Assemble file '{file}'")

    modules: dict = {}

    load_module(modules, file, debug, file, True)

    return 0


def mode_mc_schem(file: str, override: bool, debug: bool) -> int:

    if os.path.splitext(file)[1] in (".asm", ".asmn1"):
        exit_code = mode_default(file, override, debug)
        if exit_code != 0:
            return exit_code
        file = os.path.splitext(file)[0] + ".n1"

    elif os.path.splitext(file)[1] != ".n1":
        print("Invalid file type! File extension needs to be '.asm', '.asmn1' or '.n1'. Type '-h' for help ...")
        return 1

    print(f"Generate MC schematic from file '{file}'")


def mode_regenerate(file: str, override: bool, debug: bool) -> int:

    if os.path.splitext(file)[1] != ".n1":
        print("Invalid file type! File extension needs to be '.n1'. Type '-h' for help ...")
        return 1

    print(f"Regenerate from file '{file}'")


def main(args: list[str]) -> int:
    """The main function of the assembler"""

    if "-h" in args:
        print_help()
        return 0

    mc_schem: bool = "-m" in args
    override: bool = "-o" in args
    debug: bool = "-d" in args
    regenerate: bool = "-r" in args

    if len(args) < 2:
        print("Missing arguments! Type '-h' for help ...")
        return 1

    if mc_schem and regenerate:
        print("Invalid combination of '-m' and '-r' flags! Type '-h' for help ...")
        return 1

    if len([arg for arg in args if arg not in ("-m", "-o", "-d", "-r")]) != 2:
        print("Missing file argument! Type '-h' for help ...")
        return 1

    file = args[-1]

    if not os.path.exists(file):
        print("Invalid file path! File don't exists. Type '-h' for help ...")
        return 1
    if not os.path.isfile(file):
        print("Invalid file path! Not a file. Type '-h' for help ...")
        return 1

    file = os.path.abspath(file)

    if mc_schem:
        return mode_mc_schem(file, override, debug)

    if regenerate:
        return mode_regenerate(file, override, debug)

    return mode_default(file, override, debug)


# Main
if __name__ == "__main__":

    sys.exit(main(sys.argv))


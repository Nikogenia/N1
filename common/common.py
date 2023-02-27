REGISTER = [
    ("a", "000"),
    ("b", "001"),
    ("c", "010"),
    ("d", "011"),
    ("h", "100"),
    ("l", "101"),
    ("z", "110"),
    ("f", "111"),
]


INSTRUCTION = [
    ("mvi",    "00000", ("r", "i"), 2),
    ("mvr",    "00001", ("r", "r"), 2),
    ("lda",    "00010", ("r", "a"), 3),
    ("ldhl",   "00011", ("r"),      1),
    ("sta",    "00100", ("r", "a"), 3),
    ("sthl",   "00101", ("r"),      1),
    ("pushi",  "00110", ("i"),      2),
    ("pushr",  "00111", ("r"),      1),
    ("pop",    "01000", ("r"),      1),
    ("nop",    "01001", (),         1),
    ("jnz",    "01010", ("r"),      1),
    ("jmp",    "01011", (),         1),
    ("ini",    "01100", ("r", "i"), 2),
    ("inr",    "01101", ("r", "r"), 2),
    ("outi",   "01110", ("r", "i"), 2),
    ("outr",   "01111", ("r", "r"), 2),
    ("addi",   "10000", ("r", "i"), 2),
    ("addr",   "10001", ("r", "r"), 2),
    ("adci",   "10010", ("r", "i"), 2),
    ("adcr",   "10011", ("r", "r"), 2),
    ("andi",   "10100", ("r", "i"), 2),
    ("andr",   "10101", ("r", "r"), 2),
    ("ori",    "10110", ("r", "i"), 2),
    ("orr",    "10111", ("r", "r"), 2),
    ("nori",   "11000", ("r", "i"), 2),
    ("norr",   "11001", ("r", "r"), 2),
    ("cmpi",   "11010", ("r", "i"), 2),
    ("cmpr",   "11011", ("r", "r"), 2),
    ("sbbi",   "11100", ("r", "i"), 2),
    ("sbbr",   "11101", ("r", "r"), 2),
    ("shl",    "11110", ("r"),      1),
    ("shr",    "11111", ("r"),      1),
]


SIZE_ROM = 0x8000
SIZE_BANK = 0x4000
SIZE_RAM = 0x3000
SIZE_STACK = 0x0FEF

ADDR_ROM = 0x0000
ADDR_BANK = ADDR_ROM + SIZE_ROM
ADDR_RAM = ADDR_BANK + SIZE_BANK
ADDR_STACK = ADDR_RAM + SIZE_RAM

ADDR_MB = 0xFFFB
ADDR_SP = 0xFFFC
ADDR_PC = 0xFFFE


BANK_RAM = 0
BANK_VRAM = 1


PORT_EXIT = 0
PORT_GPU = 1


EXIT_CLEAN = 0
EXIT_UNKNOWN = 1
EXIT_ST_OVERFLOW = 2
EXIT_ST_EMPTY = 3
EXIT_R_O_ACCESS = 4
EXIT_INVALID_BANK = 5
EXIT_INVALID_ADDR = 6


def number2str(number: int, size: int = 0) -> str:
    return hex(number).replace('0x', '').zfill(size)


def str2number(string: str) -> int:
    return int(string, 16)


def split16(number: int) -> tuple[int, int]:
    string = number2str(number, 4)
    return str2number(string[:2]), str2number(string[2:])


def instruction2binary(name: str) -> str:
    for n, b, a, l in INSTRUCTION:
        if n == name:
            return b


def binary2instruction(binary: str) -> str:
    for n, b, a, l in INSTRUCTION:
        if b == binary:
            return n


def instruction_args(name: str) -> str:
    for n, b, a, l in INSTRUCTION:
        if n == name:
            return a


def instruction_length(name: str) -> str:
    for n, b, a, l in INSTRUCTION:
        if n == name:
            return l


def register2binary(name: str) -> str:
    for n, b in REGISTER:
        if n == name:
            return b


def binary2register(binary: str) -> str:
    for n, b in REGISTER:
        if b == binary:
            return n


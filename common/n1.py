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


def instruction2binary(name: str) -> str:
    for n, b, a, l in INSTRUCTION:
        if n == name:
            return b


def register2binary(name: str) -> str:
    for n, b in REGISTER:
        if n == name:
            return b


def binary2instruction(binary: str) -> str:
    for n, b, a, l in INSTRUCTION:
        if b == binary:
            return n


def binary2register(binary: str) -> str:
    for n, b in REGISTER:
        if b == binary:
            return n


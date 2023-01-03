# Local modules
from common import *


class N1:
    """N1 machine"""

    def __init__(self) -> None:

        self.registers: dict[str, int] = {"a": 0, "b": 0, "c": 0, "d": 0, "h": 0, "l": 0, "z": 0, "f": 0}
        self.mb: int = BANK_RAM
        self.sp: tuple[int, int] = split16(ADDR_STACK)
        self.pc: tuple[int, int] = split16(ADDR_ROM)

        self.rom: dict[int, int] = {}
        self.bank: dict[int, dict[int, int]] = {BANK_RAM: {}, BANK_VRAM: {}}
        self.ram: dict[int, int] = {}
        self.stack: list[int] = []

        self.exit: int = -1

    def reset(self) -> None:

        self.registers = {"a": 0, "b": 0, "c": 0, "d": 0, "h": 0, "l": 0, "z": 0, "f": 0}
        self.mb = BANK_RAM
        self.sp = split16(ADDR_STACK)
        self.pc = split16(ADDR_ROM)

        for bank in self.bank:
            bank.clear()
        self.ram.clear()
        self.stack.clear()

        self.exit = -1

    def load_rom(self, string: str) -> None:

        self.rom.clear()

        for i in range(0, len(string), 8):
            self.rom[ADDR_ROM + i // 8] = string[i:i+8]

    def addr_get(self, addr: int) -> int:

        if ADDR_ROM <= addr < ADDR_ROM + SIZE_ROM:
            return self.rom[addr] if addr in self.rom else 0

        if ADDR_BANK <= addr < ADDR_BANK + SIZE_BANK:
            if self.mb not in self.bank:
                self.exit = EXIT_INVALID_BANK
                return 0
            return self.bank[self.mb][addr] if addr in self.bank[self.mb] else 0

        if ADDR_RAM <= addr < ADDR_RAM + SIZE_RAM:
            return self.ram[addr] if addr in self.ram else 0

        if ADDR_MB == addr:
            return self.mb
        
        if ADDR_SP <= addr < ADDR_SP + 1:
            return self.sp[addr - ADDR_SP]

        if ADDR_PC <= addr < ADDR_PC + 1:
            return self.pc[addr - ADDR_PC]

        self.exit = EXIT_INVALID_ADDR
        return 0
    
    def addr_set(self, addr: int, value: int) -> None:

        if ADDR_BANK <= addr < ADDR_BANK + SIZE_BANK:
            if self.mb not in self.bank:
                self.exit = EXIT_INVALID_BANK
                return
            self.bank[self.mb][addr] = value
            return

        if ADDR_RAM <= addr < ADDR_RAM + SIZE_RAM:
            self.ram[addr] = value
            return

        if ADDR_MB == addr:
            self.mb = value
            return

        if ADDR_SP <= addr < ADDR_SP + 1:
            if addr == ADDR_SP:
                self.sp = value, self.sp[1]
            else:
                self.sp = self.sp[0], value
            return

        if ADDR_PC <= addr < ADDR_PC + 1 or ADDR_ROM <= addr < ADDR_ROM + SIZE_ROM:
            self.exit = EXIT_R_O_ACCESS
            return

        self.exit = EXIT_INVALID_ADDR


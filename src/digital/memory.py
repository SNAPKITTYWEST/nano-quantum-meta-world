"""Memory cell, register file, and simple cache model."""

from __future__ import annotations
from typing import List, Dict, Any


class MemoryCell:
    """Single-bit or multi-bit storage cell (SRAM-like abstract model)."""

    def __init__(self, width: int = 1):
        self.width = width
        self.value = 0
        self._mask = (1 << width) - 1

    def write(self, data: int) -> None:
        self.value = data & self._mask

    def read(self) -> int:
        return self.value

    def structural_decomposition(self) -> Dict[str, Any]:
        return {"type": "MemoryCell", "width": self.width,
                "note": "Abstract; real cell is 6T SRAM or DRAM capacitor + access transistor"}


class RegisterFile:
    """Multi-port register file."""

    def __init__(self, n_regs: int = 16, width: int = 32, n_read_ports: int = 2, n_write_ports: int = 1):
        self.n_regs = n_regs
        self.width = width
        self.n_read_ports = n_read_ports
        self.n_write_ports = n_write_ports
        self.regs = [0] * n_regs
        self._mask = (1 << width) - 1

    def read(self, index: int) -> int:
        if not 0 <= index < self.n_regs:
            raise ValueError(f"RegisterFile: index {index} out of range")
        return self.regs[index]

    def write(self, index: int, value: int) -> None:
        if not 0 <= index < self.n_regs:
            raise ValueError(f"RegisterFile: index {index} out of range")
        if index == 0:
            return
        self.regs[index] = value & self._mask

    def structural_decomposition(self) -> Dict[str, Any]:
        return {"type": "RegisterFile", "n_regs": self.n_regs, "width": self.width,
                "ports": {"read": self.n_read_ports, "write": self.n_write_ports},
                "built_from": "array of registers + decoder + muxes"}


class CacheModel:
    """Direct-mapped cache model (software simulation only)."""

    def __init__(self, n_lines: int = 64, line_size: int = 16, address_bits: int = 32):
        self.n_lines = n_lines
        self.line_size = line_size
        self.address_bits = address_bits
        self.offset_bits = (line_size - 1).bit_length()
        self.index_bits = (n_lines - 1).bit_length()
        self.tag_bits = address_bits - self.index_bits - self.offset_bits
        self.valid = [False] * n_lines
        self.tag = [0] * n_lines
        self.data = [[0] * line_size for _ in range(n_lines)]
        self.hits = 0
        self.misses = 0

    def _split(self, addr: int):
        offset = addr & ((1 << self.offset_bits) - 1)
        index = (addr >> self.offset_bits) & ((1 << self.index_bits) - 1)
        tag = addr >> (self.offset_bits + self.index_bits)
        return tag, index, offset

    def access(self, addr: int, write: bool = False, value: int = 0) -> tuple:
        tag, index, offset = self._split(addr)
        if self.valid[index] and self.tag[index] == tag:
            self.hits += 1
            if write:
                self.data[index][offset] = value
            return True, self.data[index][offset]
        else:
            self.misses += 1
            self.valid[index] = True
            self.tag[index] = tag
            if write:
                self.data[index][offset] = value
            return False, self.data[index][offset]

    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total else 0.0

    def structural_decomposition(self) -> Dict[str, Any]:
        return {"type": "CacheModel", "organization": "direct-mapped",
                "n_lines": self.n_lines, "line_size": self.line_size,
                "tag_bits": self.tag_bits, "index_bits": self.index_bits, "offset_bits": self.offset_bits,
                "note": "Abstract timing model only; no real SRAM arrays"}

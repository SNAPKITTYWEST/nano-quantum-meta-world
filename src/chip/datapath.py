"""Datapath: registers, ALU, muxes, buses."""

from __future__ import annotations
from typing import Dict, Any
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from digital.alu import ALU
from digital.memory import RegisterFile
from digital.bus import Bus
from digital.sequential import Register


class DataPath:
    def __init__(self, width: int = 32, n_regs: int = 16):
        self.width = width
        self.regfile = RegisterFile(n_regs=n_regs, width=width)
        self.alu = ALU(width=width)
        self.pc = Register(width=width)
        self.ir = Register(width=width)
        self.bus = Bus(width=width, name="DataBus")
        self.acc = 0

    def reset(self) -> None:
        self.regfile.regs = [0] * self.regfile.n_regs
        self.pc.reset()
        self.ir.reset()
        self.acc = 0

    def alu_op(self, a_idx: int, b_idx: int, opcode: int) -> int:
        a = self.regfile.read(a_idx)
        b = self.regfile.read(b_idx)
        result, flags = self.alu.run(a, b, opcode)
        return result

    def structural_decomposition(self) -> Dict[str, Any]:
        return {
            "type": "DataPath", "width": self.width,
            "components": {
                "regfile": self.regfile.structural_decomposition(),
                "alu": self.alu.structural_decomposition(),
                "pc": self.pc.structural_decomposition(),
                "ir": self.ir.structural_decomposition(),
                "bus": self.bus.structural_decomposition(),
            },
        }

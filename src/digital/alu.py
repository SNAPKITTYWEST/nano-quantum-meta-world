"""Arithmetic Logic Unit built from FullAdders, XOR, AND, OR, MUX etc."""

from __future__ import annotations
from typing import List, Dict, Any, Tuple
from .gates import Gate


class ALU(Gate):
    """
    Simple N-bit ALU.
    Operations selected by 3-bit opcode:
      000 ADD    001 SUB    010 AND    011 OR
      100 XOR    101 NOT A  110 PASS A 111 PASS B
    Flags: zero, carry/borrow, negative (MSB)
    """
    name = "ALU"

    OPCODES = {
        0b000: "ADD", 0b001: "SUB", 0b010: "AND", 0b011: "OR",
        0b100: "XOR", 0b101: "NOTA", 0b110: "PASSA", 0b111: "PASSB",
    }

    def __init__(self, width: int = 8):
        self.width = width
        self.n_inputs = 2 * width + 3
        self.n_outputs = width + 3
        self.delay = 12.0
        self._inputs = [0] * self.n_inputs
        self._outputs = [0] * self.n_outputs
        self._history: List[Dict] = []

    def _bits_to_int(self, bits: List[int]) -> int:
        v = 0
        for b in bits:
            v = (v << 1) | b
        return v

    def _int_to_bits(self, v: int, width: int) -> List[int]:
        return [(v >> i) & 1 for i in range(width - 1, -1, -1)]

    def evaluate(self, inputs: List[int]) -> List[int]:
        if len(inputs) != self.n_inputs:
            raise ValueError(f"ALU({self.width}): expected {self.n_inputs} inputs")
        a_bits = inputs[:self.width]
        b_bits = inputs[self.width:2 * self.width]
        opcode = self._bits_to_int(inputs[2 * self.width:])
        a = self._bits_to_int(a_bits)
        b = self._bits_to_int(b_bits)
        carry = 0
        result = 0
        if opcode == 0b000:
            result = a + b
            carry = 1 if result >= (1 << self.width) else 0
            result &= (1 << self.width) - 1
        elif opcode == 0b001:
            result = a - b
            carry = 0 if result < 0 else 1
            result &= (1 << self.width) - 1
        elif opcode == 0b010:
            result = a & b
        elif opcode == 0b011:
            result = a | b
        elif opcode == 0b100:
            result = a ^ b
        elif opcode == 0b101:
            result = (~a) & ((1 << self.width) - 1)
        elif opcode == 0b110:
            result = a
        elif opcode == 0b111:
            result = b
        zero = 1 if result == 0 else 0
        neg = (result >> (self.width - 1)) & 1
        out_bits = self._int_to_bits(result, self.width)
        return out_bits + [zero, carry, neg]

    def boolean_expression(self) -> str:
        return (f"{self.width}-bit ALU: result, Z, C, N = f(A, B, opcode)\n"
                "ADD via ripple FullAdders; SUB via invert B + cin=1; "
                "logic via bitwise gates; select via MUX tree")

    def structural_decomposition(self) -> Dict[str, Any]:
        return {
            "type": "ALU", "width": self.width,
            "datapath": {"adder": f"{self.width} × FullAdder (ripple-carry)", "logic": "bitwise AND/OR/XOR/NOT", "mux": "result select by opcode"},
            "flags": ["zero (NOR of all bits)", "carry out", "negative (MSB)"],
            "opcodes": self.OPCODES, "primitive": False,
        }

    def run(self, a: int, b: int, opcode: int) -> Tuple[int, Dict[str, int]]:
        a_bits = self._int_to_bits(a & ((1 << self.width) - 1), self.width)
        b_bits = self._int_to_bits(b & ((1 << self.width) - 1), self.width)
        op_bits = self._int_to_bits(opcode & 7, 3)
        out = self.evaluate(a_bits + b_bits + op_bits)
        result = self._bits_to_int(out[:self.width])
        flags = {"Z": out[self.width], "C": out[self.width + 1], "N": out[self.width + 2]}
        return result, flags

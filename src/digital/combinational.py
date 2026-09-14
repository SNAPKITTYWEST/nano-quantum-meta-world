"""Decoder, Encoder and related combinational blocks."""

from __future__ import annotations
from typing import List, Dict, Any
from .gates import Gate


class Decoder(Gate):
    """n-to-2^n binary decoder. Active-high one-hot output."""
    name = "Decoder"

    def __init__(self, n: int = 2):
        self.n = n
        self.n_inputs = n
        self.n_outputs = 1 << n
        self.delay = float(n)
        self._inputs = [0] * self.n_inputs
        self._outputs = [0] * self.n_outputs
        self._history: List[Dict] = []

    def evaluate(self, inputs: List[int]) -> List[int]:
        if len(inputs) != self.n:
            raise ValueError(f"Decoder({self.n}): expected {self.n} inputs")
        idx = 0
        for b in inputs:
            idx = (idx << 1) | b
        out = [0] * self.n_outputs
        out[idx] = 1
        return out

    def boolean_expression(self) -> str:
        return f"{self.n}-to-{self.n_outputs} decoder: Y_i = 1 iff input == i"

    def structural_decomposition(self) -> Dict[str, Any]:
        return {
            "type": "Decoder", "n": self.n,
            "built_from": "AND gates of all input combinations (with NOT on zeros)",
            "primitive": False,
        }


class Encoder(Gate):
    """2^n-to-n priority encoder (highest index wins)."""
    name = "Encoder"

    def __init__(self, n: int = 2):
        self.n = n
        self.n_inputs = 1 << n
        self.n_outputs = n
        self.delay = float(n)
        self._inputs = [0] * self.n_inputs
        self._outputs = [0] * self.n_outputs
        self._history: List[Dict] = []

    def evaluate(self, inputs: List[int]) -> List[int]:
        if len(inputs) != self.n_inputs:
            raise ValueError(f"Encoder({self.n}): expected {self.n_inputs} inputs")
        for i in range(self.n_inputs - 1, -1, -1):
            if inputs[i]:
                bits = [(i >> k) & 1 for k in range(self.n - 1, -1, -1)]
                return bits
        return [0] * self.n

    def boolean_expression(self) -> str:
        return f"{self.n_inputs}-to-{self.n} priority encoder"

    def structural_decomposition(self) -> Dict[str, Any]:
        return {"type": "Encoder", "n": self.n, "built_from": "priority logic + OR trees", "primitive": False}

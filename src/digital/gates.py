"""
Core digital gates built from first principles.
NAND is the primitive; everything else is composed from it where practical.
"""

from __future__ import annotations
from typing import List, Dict, Tuple, Any, Optional, Callable
from abc import ABC, abstractmethod
import json


class Gate(ABC):
    """Base class for all digital gates / circuits."""

    name: str = "Gate"
    n_inputs: int = 0
    n_outputs: int = 1
    delay: float = 1.0

    def __init__(self):
        self._inputs: List[int] = [0] * self.n_inputs
        self._outputs: List[int] = [0] * self.n_outputs
        self._history: List[Dict] = []

    @abstractmethod
    def evaluate(self, inputs: List[int]) -> List[int]:
        ...

    def set_inputs(self, inputs: List[int]) -> None:
        if len(inputs) != self.n_inputs:
            raise ValueError(f"{self.name}: expected {self.n_inputs} inputs, got {len(inputs)}")
        for v in inputs:
            if v not in (0, 1):
                raise ValueError(f"{self.name}: inputs must be 0 or 1, got {v}")
        self._inputs = list(inputs)
        self._outputs = self.evaluate(self._inputs)
        self._history.append({"inputs": self._inputs[:], "outputs": self._outputs[:]})

    @property
    def outputs(self) -> List[int]:
        return self._outputs[:]

    def truth_table(self) -> List[Tuple[Tuple[int, ...], Tuple[int, ...]]]:
        n = self.n_inputs
        rows = []
        for i in range(2 ** n):
            inp = [(i >> k) & 1 for k in range(n - 1, -1, -1)]
            out = self.evaluate(inp)
            rows.append((tuple(inp), tuple(out)))
        return rows

    def boolean_expression(self) -> str:
        return f"{self.name}(...)"

    def structural_decomposition(self) -> Dict[str, Any]:
        return {"type": self.name, "primitive": True}

    def input_output_spec(self) -> Dict[str, Any]:
        return {"name": self.name, "inputs": self.n_inputs, "outputs": self.n_outputs, "delay": self.delay}

    def propagation_model(self) -> Dict[str, float]:
        return {"delay_units": self.delay}

    def serialize(self) -> Dict[str, Any]:
        return {
            "class": self.__class__.__name__,
            "name": self.name,
            "n_inputs": self.n_inputs,
            "n_outputs": self.n_outputs,
            "delay": self.delay,
            "boolean": self.boolean_expression(),
            "structure": self.structural_decomposition(),
        }

    def __repr__(self) -> str:
        return f"{self.name}(in={self._inputs}, out={self._outputs})"


class NAND(Gate):
    name = "NAND"
    n_inputs = 2
    n_outputs = 1
    delay = 1.0

    def evaluate(self, inputs: List[int]) -> List[int]:
        a, b = inputs
        return [1 - (a & b)]

    def boolean_expression(self) -> str:
        return "¬(A ∧ B)"

    def structural_decomposition(self) -> Dict[str, Any]:
        return {"type": "NAND", "primitive": True, "note": "Universal gate primitive"}


class NOT(Gate):
    name = "NOT"
    n_inputs = 1
    n_outputs = 1
    delay = 1.0

    def evaluate(self, inputs: List[int]) -> List[int]:
        a = inputs[0]
        return [1 - a]

    def boolean_expression(self) -> str:
        return "¬A"

    def structural_decomposition(self) -> Dict[str, Any]:
        return {"type": "NOT", "built_from": "NAND(A, A)", "primitive": False}


class NOR(Gate):
    name = "NOR"
    n_inputs = 2
    n_outputs = 1
    delay = 1.0

    def evaluate(self, inputs: List[int]) -> List[int]:
        a, b = inputs
        return [1 if not (a | b) else 0]

    def boolean_expression(self) -> str:
        return "¬(A ∨ B)"

    def structural_decomposition(self) -> Dict[str, Any]:
        return {"type": "NOR", "primitive": True, "note": "Universal gate primitive"}


class AND(Gate):
    name = "AND"
    n_inputs = 2
    n_outputs = 1
    delay = 2.0

    def evaluate(self, inputs: List[int]) -> List[int]:
        a, b = inputs
        return [a & b]

    def boolean_expression(self) -> str:
        return "A ∧ B"

    def structural_decomposition(self) -> Dict[str, Any]:
        return {"type": "AND", "built_from": "NOT(NAND(A, B))", "primitive": False}


class OR(Gate):
    name = "OR"
    n_inputs = 2
    n_outputs = 1
    delay = 2.0

    def evaluate(self, inputs: List[int]) -> List[int]:
        a, b = inputs
        return [a | b]

    def boolean_expression(self) -> str:
        return "A ∨ B"

    def structural_decomposition(self) -> Dict[str, Any]:
        return {"type": "OR", "built_from": "NAND(NOT(A), NOT(B))", "primitive": False}


class XOR(Gate):
    name = "XOR"
    n_inputs = 2
    n_outputs = 1
    delay = 3.0

    def evaluate(self, inputs: List[int]) -> List[int]:
        a, b = inputs
        return [a ^ b]

    def boolean_expression(self) -> str:
        return "A ⊕ B = (A ∧ ¬B) ∨ (¬A ∧ B)"

    def structural_decomposition(self) -> Dict[str, Any]:
        return {"type": "XOR", "built_from": "OR(AND(A, NOT(B)), AND(NOT(A), B))", "primitive": False}


class XNOR(Gate):
    name = "XNOR"
    n_inputs = 2
    n_outputs = 1
    delay = 3.0

    def evaluate(self, inputs: List[int]) -> List[int]:
        a, b = inputs
        return [1 - (a ^ b)]

    def boolean_expression(self) -> str:
        return "¬(A ⊕ B)"

    def structural_decomposition(self) -> Dict[str, Any]:
        return {"type": "XNOR", "built_from": "NOT(XOR(A, B))", "primitive": False}


class MUX(Gate):
    """2-to-1 multiplexer. Inputs: A, B, S. Output: A if S=0, else B."""
    name = "MUX"
    n_inputs = 3
    n_outputs = 1
    delay = 3.0

    def evaluate(self, inputs: List[int]) -> List[int]:
        a, b, s = inputs
        return [a if s == 0 else b]

    def boolean_expression(self) -> str:
        return "(A ∧ ¬S) ∨ (B ∧ S)"

    def structural_decomposition(self) -> Dict[str, Any]:
        return {"type": "MUX2to1", "built_from": "OR(AND(A, NOT(S)), AND(B, S))", "primitive": False}


class DEMUX(Gate):
    """1-to-2 demultiplexer. Inputs: A, S. Outputs: Y0, Y1."""
    name = "DEMUX"
    n_inputs = 2
    n_outputs = 2
    delay = 2.0

    def evaluate(self, inputs: List[int]) -> List[int]:
        a, s = inputs
        return [a if s == 0 else 0, a if s == 1 else 0]

    def boolean_expression(self) -> str:
        return "Y0 = A ∧ ¬S; Y1 = A ∧ S"

    def structural_decomposition(self) -> Dict[str, Any]:
        return {"type": "DEMUX1to2", "built_from": "AND(A, NOT(S)) and AND(A, S)", "primitive": False}


class HalfAdder(Gate):
    name = "HalfAdder"
    n_inputs = 2
    n_outputs = 2
    delay = 3.0

    def evaluate(self, inputs: List[int]) -> List[int]:
        a, b = inputs
        return [a ^ b, a & b]

    def boolean_expression(self) -> str:
        return "S = A ⊕ B; C = A ∧ B"

    def structural_decomposition(self) -> Dict[str, Any]:
        return {"type": "HalfAdder", "built_from": "XOR(A,B) for sum, AND(A,B) for carry", "primitive": False}


class FullAdder(Gate):
    name = "FullAdder"
    n_inputs = 3
    n_outputs = 2
    delay = 6.0

    def evaluate(self, inputs: List[int]) -> List[int]:
        a, b, cin = inputs
        s1 = a ^ b
        c1 = a & b
        s = s1 ^ cin
        c2 = s1 & cin
        cout = c1 | c2
        return [s, cout]

    def boolean_expression(self) -> str:
        return "S = A ⊕ B ⊕ Cin; Cout = (A ∧ B) ∨ (Cin ∧ (A ⊕ B))"

    def structural_decomposition(self) -> Dict[str, Any]:
        return {
            "type": "FullAdder",
            "built_from": "Two HalfAdders + OR: (A,B)->HA->(s1,c1), (s1,Cin)->HA->(S,c2), OR(c1,c2)->Cout",
            "primitive": False,
        }


class Comparator(Gate):
    """1-bit comparator. Outputs: EQ, GT, LT."""
    name = "Comparator"
    n_inputs = 2
    n_outputs = 3
    delay = 3.0

    def evaluate(self, inputs: List[int]) -> List[int]:
        a, b = inputs
        eq = 1 if a == b else 0
        gt = 1 if a > b else 0
        lt = 1 if a < b else 0
        return [eq, gt, lt]

    def boolean_expression(self) -> str:
        return "EQ = ¬(A ⊕ B); GT = A ∧ ¬B; LT = ¬A ∧ B"

    def structural_decomposition(self) -> Dict[str, Any]:
        return {"type": "Comparator", "built_from": "XNOR for EQ, AND+NOT for GT/LT", "primitive": False}

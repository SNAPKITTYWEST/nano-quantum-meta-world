"""Quantum circuit representation and composition."""

from __future__ import annotations
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, field
from .gates import QuantumGate, GateLibrary
import numpy as np


@dataclass
class CircuitOp:
    gate: QuantumGate
    qubits: List[int]
    label: Optional[str] = None


class QuantumCircuit:
    def __init__(self, n_qubits: int, name: str = "circuit"):
        if n_qubits < 1:
            raise ValueError("n_qubits must be >= 1")
        self.n_qubits = n_qubits
        self.name = name
        self.ops: List[CircuitOp] = []

    def _add(self, gate: QuantumGate, qubits: List[int], label: Optional[str] = None) -> QuantumCircuit:
        for q in qubits:
            if not 0 <= q < self.n_qubits:
                raise ValueError(f"Qubit {q} out of range [0, {self.n_qubits})")
        if len(qubits) != gate.n_qubits:
            raise ValueError(f"Gate {gate.name} expects {gate.n_qubits} qubits, got {len(qubits)}")
        self.ops.append(CircuitOp(gate, qubits, label))
        return self

    def i(self, q: int) -> QuantumCircuit: return self._add(GateLibrary.I, [q])
    def x(self, q: int) -> QuantumCircuit: return self._add(GateLibrary.X, [q])
    def y(self, q: int) -> QuantumCircuit: return self._add(GateLibrary.Y, [q])
    def z(self, q: int) -> QuantumCircuit: return self._add(GateLibrary.Z, [q])
    def h(self, q: int) -> QuantumCircuit: return self._add(GateLibrary.H, [q])
    def s(self, q: int) -> QuantumCircuit: return self._add(GateLibrary.S, [q])
    def t(self, q: int) -> QuantumCircuit: return self._add(GateLibrary.T, [q])
    def cx(self, c: int, t: int) -> QuantumCircuit: return self._add(GateLibrary.CNOT, [c, t])
    def cz(self, c: int, t: int) -> QuantumCircuit: return self._add(GateLibrary.CZ, [c, t])
    def swap(self, a: int, b: int) -> QuantumCircuit: return self._add(GateLibrary.SWAP, [a, b])
    def ccx(self, c1: int, c2: int, t: int) -> QuantumCircuit: return self._add(GateLibrary.TOFFOLI, [c1, c2, t])

    def rx(self, q: int, theta: float) -> QuantumCircuit: return self._add(GateLibrary.RX(theta), [q])
    def ry(self, q: int, theta: float) -> QuantumCircuit: return self._add(GateLibrary.RY(theta), [q])
    def rz(self, q: int, theta: float) -> QuantumCircuit: return self._add(GateLibrary.RZ(theta), [q])

    def barrier(self) -> QuantumCircuit:
        return self

    def depth(self) -> int:
        if not self.ops:
            return 0
        layers = [0] * self.n_qubits
        for op in self.ops:
            max_layer = max(layers[q] for q in op.qubits)
            for q in op.qubits:
                layers[q] = max_layer + 1
        return max(layers)

    def count_ops(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for op in self.ops:
            counts[op.gate.name] = counts.get(op.gate.name, 0) + 1
        return counts

    def draw(self) -> str:
        lines = [f"q{i}: " for i in range(self.n_qubits)]
        for op in self.ops:
            width = max(len(op.gate.name) + 2, 5)
            for i in range(self.n_qubits):
                if i in op.qubits:
                    label = op.gate.name.center(width - 2)
                    lines[i] += f"[{label}]—"
                else:
                    lines[i] += "—" * width
        return "\n".join(lines)

    def __repr__(self) -> str:
        return f"QuantumCircuit({self.n_qubits}q, {len(self.ops)} ops, depth={self.depth()})"


class CircuitComposer:
    @staticmethod
    def compose(a: QuantumCircuit, b: QuantumCircuit) -> QuantumCircuit:
        if a.n_qubits != b.n_qubits:
            raise ValueError("Circuits must have same qubit count")
        c = QuantumCircuit(a.n_qubits, name=f"{a.name}+{b.name}")
        c.ops = list(a.ops) + list(b.ops)
        return c

    @staticmethod
    def repeat(circuit: QuantumCircuit, n: int) -> QuantumCircuit:
        c = QuantumCircuit(circuit.n_qubits, name=f"{circuit.name}x{n}")
        for _ in range(n):
            c.ops.extend(circuit.ops)
        return c

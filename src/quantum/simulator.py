"""State-vector quantum circuit simulator."""

from __future__ import annotations
from typing import Optional, Dict
import numpy as np
from .statevector import StateVector
from .circuit import QuantumCircuit


class CircuitSimulator:
    def __init__(self, seed: Optional[int] = None):
        self.seed = seed
        self._last_sv: Optional[StateVector] = None

    def _build_operator(self, gate_matrix: np.ndarray, target_qubits: list, n_qubits: int) -> np.ndarray:
        n_gate = int(np.log2(gate_matrix.shape[0]))
        dim = 2 ** n_qubits
        op = np.zeros((dim, dim), dtype=np.complex128)
        for col in range(dim):
            bits = [(col >> i) & 1 for i in range(n_qubits)]
            gate_col = 0
            for k, q in enumerate(target_qubits):
                gate_col |= bits[q] << (n_gate - 1 - k)
            for gate_row in range(gate_matrix.shape[0]):
                if abs(gate_matrix[gate_row, gate_col]) < 1e-15:
                    continue
                new_bits = list(bits)
                for k, q in enumerate(target_qubits):
                    new_bits[q] = (gate_row >> (n_gate - 1 - k)) & 1
                row = sum(b << i for i, b in enumerate(new_bits))
                op[row, col] += gate_matrix[gate_row, gate_col]
        return op

    def get_statevector(self, circuit: QuantumCircuit) -> StateVector:
        sv = StateVector(circuit.n_qubits)
        for op in circuit.ops:
            full_op = self._build_operator(op.gate.matrix, op.qubits, circuit.n_qubits)
            sv.apply_gate(full_op)
        self._last_sv = sv
        return sv

    def run(self, circuit: QuantumCircuit, shots: int = 1024) -> Dict[str, int]:
        sv = self.get_statevector(circuit)
        probs = np.real(np.conj(sv.data) * sv.data)
        rng = np.random.default_rng(self.seed)
        outcomes = rng.choice(sv.dim, size=shots, p=probs)
        counts: Dict[str, int] = {}
        for o in outcomes:
            bs = bin(o)[2:].zfill(circuit.n_qubits)
            counts[bs] = counts.get(bs, 0) + 1
        return counts

    def measure(self, circuit: QuantumCircuit) -> str:
        sv = self.get_statevector(circuit)
        return sv.measure(seed=self.seed)

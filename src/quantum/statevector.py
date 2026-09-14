"""State-vector representation and tensor-product utilities."""

from __future__ import annotations
from typing import List, Optional, Dict
import numpy as np

TOLERANCE = 1e-10


class StateVector:
    def __init__(self, n_qubits: int, data: Optional[np.ndarray] = None):
        if n_qubits < 1:
            raise ValueError("n_qubits must be >= 1")
        self.n_qubits = n_qubits
        self.dim = 2 ** n_qubits
        if data is not None:
            if data.shape != (self.dim,):
                raise ValueError(f"State shape {data.shape} invalid for {n_qubits} qubits")
            norm = np.linalg.norm(data)
            if norm < TOLERANCE:
                raise ValueError("Zero-norm state")
            self.data = (data / norm).astype(np.complex128)
        else:
            self.data = np.zeros(self.dim, dtype=np.complex128)
            self.data[0] = 1.0

    def copy(self) -> StateVector:
        sv = StateVector(self.n_qubits)
        sv.data = self.data.copy()
        return sv

    def probabilities(self) -> Dict[str, float]:
        probs = np.real(np.conj(self.data) * self.data)
        result = {}
        for i, p in enumerate(probs):
            if p > TOLERANCE:
                result[bin(i)[2:].zfill(self.n_qubits)] = float(p)
        return result

    def amplitude(self, bitstring: str) -> complex:
        if len(bitstring) != self.n_qubits:
            raise ValueError(f"Bitstring length {len(bitstring)} != {self.n_qubits}")
        return complex(self.data[int(bitstring, 2)])

    def is_normalized(self) -> bool:
        return np.isclose(np.linalg.norm(self.data), 1.0, atol=TOLERANCE)

    def apply_gate(self, matrix: np.ndarray) -> None:
        if matrix.shape != (self.dim, self.dim):
            raise ValueError(f"Matrix shape {matrix.shape} != ({self.dim}, {self.dim})")
        self.data = matrix @ self.data

    def measure(self, seed: Optional[int] = None) -> str:
        probs = np.real(np.conj(self.data) * self.data)
        rng = np.random.default_rng(seed)
        outcome = rng.choice(self.dim, p=probs)
        result = bin(outcome)[2:].zfill(self.n_qubits)
        self.data = np.zeros(self.dim, dtype=np.complex128)
        self.data[outcome] = 1.0
        return result

    def __repr__(self) -> str:
        nonzero = [(bin(i)[2:].zfill(self.n_qubits), self.data[i])
                   for i in range(self.dim) if abs(self.data[i]) > TOLERANCE]
        terms = [f"({a.real:+.4f}{a.imag:+.4f}j)|{bs}>" for bs, a in nonzero]
        return " + ".join(terms) if terms else "|void>"

    @staticmethod
    def tensor(a: StateVector, b: StateVector) -> StateVector:
        data = np.kron(a.data, b.data)
        return StateVector(a.n_qubits + b.n_qubits, data)

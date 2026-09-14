"""Measurement utilities and probability analysis."""

from __future__ import annotations
from typing import Dict, List, Optional
import numpy as np
from .statevector import StateVector


class Measurement:
    @staticmethod
    def probabilities(sv: StateVector) -> Dict[str, float]:
        return sv.probabilities()

    @staticmethod
    def expectation(sv: StateVector, observable: np.ndarray) -> float:
        if observable.shape != (sv.dim, sv.dim):
            raise ValueError("Observable dimension mismatch")
        return float(np.real(np.conj(sv.data) @ observable @ sv.data))

    @staticmethod
    def entropy(sv: StateVector) -> float:
        probs = np.real(np.conj(sv.data) * sv.data)
        probs = probs[probs > 1e-15]
        return float(-np.sum(probs * np.log2(probs)))

    @staticmethod
    def fidelity(a: StateVector, b: StateVector) -> float:
        if a.n_qubits != b.n_qubits:
            raise ValueError("Qubit count mismatch")
        overlap = np.abs(np.conj(a.data) @ b.data) ** 2
        return float(overlap)

    @staticmethod
    def sample(sv: StateVector, shots: int = 1024, seed: Optional[int] = None) -> Dict[str, int]:
        probs = np.real(np.conj(sv.data) * sv.data)
        rng = np.random.default_rng(seed)
        outcomes = rng.choice(sv.dim, size=shots, p=probs)
        counts: Dict[str, int] = {}
        for o in outcomes:
            bs = bin(o)[2:].zfill(sv.n_qubits)
            counts[bs] = counts.get(bs, 0) + 1
        return counts

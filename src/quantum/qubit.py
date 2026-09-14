"""Qubit, QuantumRegister, ClassicalRegister primitives."""

from __future__ import annotations
from typing import List, Optional


class Qubit:
    def __init__(self, index: int, name: Optional[str] = None):
        if index < 0:
            raise ValueError(f"Qubit index must be non-negative, got {index}")
        self.index = index
        self.name = name or f"q{index}"

    def __repr__(self) -> str:
        return self.name

    def __eq__(self, other) -> bool:
        return isinstance(other, Qubit) and self.index == other.index

    def __hash__(self) -> int:
        return hash(self.index)


class QuantumRegister:
    def __init__(self, size: int, name: str = "q"):
        if size < 1:
            raise ValueError("QuantumRegister size must be >= 1")
        self.size = size
        self.name = name
        self.qubits = [Qubit(i, name=f"{name}{i}") for i in range(size)]

    def __getitem__(self, key):
        if isinstance(key, slice):
            return [self.qubits[i] for i in range(*key.indices(self.size))]
        if not 0 <= key < self.size:
            raise IndexError(f"Qubit index {key} out of range [0, {self.size})")
        return self.qubits[key]

    def __len__(self) -> int:
        return self.size

    def __repr__(self) -> str:
        return f"QuantumRegister(size={self.size}, name={self.name!r})"


class ClassicalRegister:
    def __init__(self, size: int, name: str = "c"):
        if size < 1:
            raise ValueError("ClassicalRegister size must be >= 1")
        self.size = size
        self.name = name
        self.bits = [0] * size

    def __getitem__(self, key) -> int:
        return self.bits[key]

    def __setitem__(self, key, value: int) -> None:
        if value not in (0, 1):
            raise ValueError("Classical bit must be 0 or 1")
        self.bits[key] = value

    def __len__(self) -> int:
        return self.size

    def to_int(self) -> int:
        v = 0
        for i, b in enumerate(self.bits):
            v |= b << i
        return v

    def reset(self) -> None:
        self.bits = [0] * self.size

    def __repr__(self) -> str:
        return f"ClassicalRegister(size={self.size}, bits={self.bits})"

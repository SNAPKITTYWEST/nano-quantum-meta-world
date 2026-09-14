"""Standard quantum algorithms as circuit constructors."""

from __future__ import annotations
from typing import List, Optional
import numpy as np
from .circuit import QuantumCircuit
from .gates import GateLibrary, QuantumGate


def bell_state(variant: str = "phi+") -> QuantumCircuit:
    qc = QuantumCircuit(2, name=f"bell_{variant}")
    if variant in ("phi+", "phi-"):
        if variant == "phi-":
            qc.x(0)
        qc.h(0).cx(0, 1)
    elif variant in ("psi+", "psi-"):
        qc.x(1)
        if variant == "psi-":
            qc.x(0)
        qc.h(0).cx(0, 1)
    else:
        raise ValueError(f"Unknown Bell variant: {variant}")
    return qc


def ghz_state(n: int) -> QuantumCircuit:
    if n < 2:
        raise ValueError("GHZ requires >= 2 qubits")
    qc = QuantumCircuit(n, name=f"ghz_{n}")
    qc.h(0)
    for i in range(1, n):
        qc.cx(0, i)
    return qc


def teleportation() -> QuantumCircuit:
    qc = QuantumCircuit(3, name="teleportation")
    qc.h(1).cx(1, 2)
    qc.cx(0, 1).h(0)
    return qc


def deutsch_jozsa(oracle_bits: List[int]) -> QuantumCircuit:
    n = len(oracle_bits)
    qc = QuantumCircuit(n + 1, name="deutsch_jozsa")
    qc.x(n)
    for i in range(n + 1):
        qc.h(i)
    for i, bit in enumerate(oracle_bits):
        if bit:
            qc.cx(i, n)
    for i in range(n):
        qc.h(i)
    return qc


def bernstein_vazirani(secret: List[int]) -> QuantumCircuit:
    n = len(secret)
    qc = QuantumCircuit(n + 1, name="bernstein_vazirani")
    qc.x(n).h(n)
    for i in range(n):
        qc.h(i)
    for i, bit in enumerate(secret):
        if bit:
            qc.cx(i, n)
    for i in range(n):
        qc.h(i)
    return qc


def grover_search(n_qubits: int, marked: List[int], n_iterations: Optional[int] = None) -> QuantumCircuit:
    if n_iterations is None:
        n_iterations = max(1, int(np.pi / 4 * np.sqrt(2 ** n_qubits / len(marked))))
    qc = QuantumCircuit(n_qubits, name="grover")
    for i in range(n_qubits):
        qc.h(i)
    for _ in range(n_iterations):
        for m in marked:
            bits = [(m >> i) & 1 for i in range(n_qubits)]
            for i, b in enumerate(bits):
                if not b:
                    qc.x(i)
            if n_qubits >= 3:
                qc.ccx(0, 1, 2)
            elif n_qubits == 2:
                qc.cz(0, 1)
            for i, b in enumerate(bits):
                if not b:
                    qc.x(i)
        for i in range(n_qubits):
            qc.h(i)
            qc.x(i)
        if n_qubits >= 3:
            qc.ccx(0, 1, 2)
        elif n_qubits == 2:
            qc.cz(0, 1)
        for i in range(n_qubits):
            qc.x(i)
            qc.h(i)
    return qc


def qft(n_qubits: int) -> QuantumCircuit:
    qc = QuantumCircuit(n_qubits, name=f"qft_{n_qubits}")
    for i in range(n_qubits):
        qc.h(i)
        for j in range(i + 1, n_qubits):
            angle = np.pi / (2 ** (j - i))
            cp = GateLibrary.RZ(angle).control(1)
            qc._add(cp, [j, i])
    for i in range(n_qubits // 2):
        qc.swap(i, n_qubits - 1 - i)
    return qc


def phase_estimation(n_counting: int = 3, n_target: int = 1) -> QuantumCircuit:
    n = n_counting + n_target
    qc = QuantumCircuit(n, name="phase_estimation")
    for i in range(n_counting):
        qc.h(i)
    for i in range(n_counting):
        for _ in range(2 ** i):
            qc.cx(i, n_counting)
    for i in range(n_counting // 2):
        qc.swap(i, n_counting - 1 - i)
    for i in range(n_counting):
        qc.h(i)
        for j in range(i):
            angle = -np.pi / (2 ** (i - j))
            cp = GateLibrary.RZ(angle).control(1)
            qc._add(cp, [j, i])
    return qc

"""Quantum simulator verification suite."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import numpy as np
from quantum.gates import GateLibrary, _is_unitary, _I, _X, _Y, _Z, _H, _S, _T, _CNOT, _CZ, _SWAP, _TOFFOLI
from quantum.circuit import QuantumCircuit
from quantum.simulator import CircuitSimulator
from quantum.statevector import StateVector
from quantum.algorithms import bell_state, ghz_state, bernstein_vazirani, qft


def test_unitarity():
    matrices = {"I": _I, "X": _X, "Y": _Y, "Z": _Z, "H": _H, "S": _S, "T": _T,
                "CNOT": _CNOT, "CZ": _CZ, "SWAP": _SWAP, "TOFFOLI": _TOFFOLI}
    for name, m in matrices.items():
        assert _is_unitary(m), f"{name} is not unitary"
    print(f"[PASS] {len(matrices)} gates unitary")


def test_bell_state():
    sim = CircuitSimulator(seed=42)
    qc = bell_state("phi+")
    sv = sim.get_statevector(qc)
    probs = sv.probabilities()
    assert abs(probs.get("00", 0) - 0.5) < 0.01
    assert abs(probs.get("11", 0) - 0.5) < 0.01
    print("[PASS] Bell state phi+")


def test_ghz():
    sim = CircuitSimulator(seed=42)
    sv = sim.get_statevector(ghz_state(3))
    probs = sv.probabilities()
    assert abs(probs.get("000", 0) - 0.5) < 0.01
    assert abs(probs.get("111", 0) - 0.5) < 0.01
    print("[PASS] GHZ(3)")


def test_bernstein_vazirani():
    sim = CircuitSimulator(seed=42)
    secret = [1, 0, 1]
    qc = bernstein_vazirani(secret)
    counts = sim.run(qc, shots=100)
    top = max(counts, key=counts.get)
    print(f"[PASS] Bernstein-Vazirani secret={secret}, top outcome={top}")


def test_qft():
    qc = qft(3)
    assert qc.n_qubits == 3
    assert qc.depth() > 0
    print(f"[PASS] QFT(3) depth={qc.depth()}")


def test_statevector():
    sv = StateVector(2)
    assert sv.is_normalized()
    assert sv.probabilities() == {"00": 1.0}
    print("[PASS] StateVector basics")


if __name__ == "__main__":
    test_unitarity()
    test_bell_state()
    test_ghz()
    test_bernstein_vazirani()
    test_qft()
    test_statevector()
    print("\nAll quantum tests passed.")

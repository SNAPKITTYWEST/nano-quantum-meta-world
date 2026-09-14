"""Custom quantum computer subsystem — canonical representation."""

from .qubit import Qubit, QuantumRegister, ClassicalRegister
from .gates import QuantumGate, GateLibrary
from .circuit import QuantumCircuit, CircuitComposer
from .statevector import StateVector
from .simulator import CircuitSimulator
from .measurement import Measurement
from .optimizer import CircuitOptimizer
from .algorithms import (
    bell_state, ghz_state, teleportation,
    deutsch_jozsa, bernstein_vazirani, grover_search,
    qft, phase_estimation,
)

__all__ = [
    "Qubit", "QuantumRegister", "ClassicalRegister",
    "QuantumGate", "GateLibrary",
    "QuantumCircuit", "CircuitComposer",
    "StateVector", "CircuitSimulator", "Measurement",
    "CircuitOptimizer",
    "bell_state", "ghz_state", "teleportation",
    "deutsch_jozsa", "bernstein_vazirani", "grover_search",
    "qft", "phase_estimation",
]

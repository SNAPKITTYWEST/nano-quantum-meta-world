"""Quantum gates as explicit unitary matrices."""

from __future__ import annotations
from typing import List, Optional, Dict, Any
import numpy as np


TOLERANCE = 1e-10


def _is_unitary(m: np.ndarray, tol: float = TOLERANCE) -> bool:
    ident = np.eye(m.shape[0], dtype=np.complex128)
    return np.allclose(m.conj().T @ m, ident, atol=tol)


class QuantumGate:
    def __init__(self, name: str, matrix: np.ndarray, qubits: Optional[List[int]] = None,
                 params: Optional[Dict[str, float]] = None):
        mat = np.asarray(matrix, dtype=np.complex128)
        if mat.ndim != 2 or mat.shape[0] != mat.shape[1]:
            raise ValueError(f"Gate {name}: matrix must be square, got {mat.shape}")
        n = int(np.log2(mat.shape[0]))
        if 2 ** n != mat.shape[0]:
            raise ValueError(f"Gate {name}: dimension {mat.shape[0]} is not a power of 2")
        if not _is_unitary(mat):
            raise ValueError(f"Gate {name}: matrix is not unitary")
        self.name = name
        self.matrix = mat
        self.n_qubits = n
        self.qubits = list(qubits) if qubits is not None else list(range(n))
        self.params = dict(params) if params else {}

    def inverse(self) -> QuantumGate:
        return QuantumGate(f"{self.name}†", self.matrix.conj().T, self.qubits, self.params)

    def control(self, n_controls: int = 1) -> QuantumGate:
        if n_controls < 1:
            raise ValueError("n_controls must be >= 1")
        dim = 2 ** (self.n_qubits + n_controls)
        mat = np.eye(dim, dtype=np.complex128)
        offset = dim - self.matrix.shape[0]
        mat[offset:, offset:] = self.matrix
        return QuantumGate("C" * n_controls + self.name, mat, params=self.params)

    def tensor(self, other: QuantumGate) -> QuantumGate:
        return QuantumGate(f"{self.name}⊗{other.name}", np.kron(self.matrix, other.matrix))

    def __repr__(self) -> str:
        qs = ",".join(str(q) for q in self.qubits)
        return f"QuantumGate({self.name} on [{qs}])"

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "n_qubits": self.n_qubits, "qubits": self.qubits, "params": self.params}


# Standard gate matrices
_I = np.array([[1, 0], [0, 1]], dtype=np.complex128)
_X = np.array([[0, 1], [1, 0]], dtype=np.complex128)
_Y = np.array([[0, -1j], [1j, 0]], dtype=np.complex128)
_Z = np.array([[1, 0], [0, -1]], dtype=np.complex128)
_H = (1 / np.sqrt(2)) * np.array([[1, 1], [1, -1]], dtype=np.complex128)
_S = np.array([[1, 0], [0, 1j]], dtype=np.complex128)
_T = np.array([[1, 0], [0, np.exp(1j * np.pi / 4)]], dtype=np.complex128)
_CNOT = np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]], dtype=np.complex128)
_CZ = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,-1]], dtype=np.complex128)
_SWAP = np.array([[1,0,0,0],[0,0,1,0],[0,1,0,0],[0,0,0,1]], dtype=np.complex128)
_TOFFOLI = np.eye(8, dtype=np.complex128)
_TOFFOLI[6, 6], _TOFFOLI[7, 7] = 0, 0
_TOFFOLI[6, 7], _TOFFOLI[7, 6] = 1, 1


def rx(theta: float) -> np.ndarray:
    c, s = np.cos(theta/2), np.sin(theta/2)
    return np.array([[c, -1j*s], [-1j*s, c]], dtype=np.complex128)

def ry(theta: float) -> np.ndarray:
    c, s = np.cos(theta/2), np.sin(theta/2)
    return np.array([[c, -s], [s, c]], dtype=np.complex128)

def rz(theta: float) -> np.ndarray:
    return np.array([[np.exp(-1j*theta/2), 0], [0, np.exp(1j*theta/2)]], dtype=np.complex128)


class GateLibrary:
    I = QuantumGate("I", _I)
    X = QuantumGate("X", _X)
    Y = QuantumGate("Y", _Y)
    Z = QuantumGate("Z", _Z)
    H = QuantumGate("H", _H)
    S = QuantumGate("S", _S)
    T = QuantumGate("T", _T)
    CNOT = QuantumGate("CNOT", _CNOT)
    CZ = QuantumGate("CZ", _CZ)
    SWAP = QuantumGate("SWAP", _SWAP)
    TOFFOLI = QuantumGate("TOFFOLI", _TOFFOLI)

    @staticmethod
    def RX(theta: float) -> QuantumGate:
        return QuantumGate(f"RX({theta:.4f})", rx(theta), params={"theta": theta})

    @staticmethod
    def RY(theta: float) -> QuantumGate:
        return QuantumGate(f"RY({theta:.4f})", ry(theta), params={"theta": theta})

    @staticmethod
    def RZ(theta: float) -> QuantumGate:
        return QuantumGate(f"RZ({theta:.4f})", rz(theta), params={"theta": theta})

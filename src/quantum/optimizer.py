"""Circuit optimization passes."""

from __future__ import annotations
from typing import List
import numpy as np
from .circuit import QuantumCircuit, CircuitOp
from .gates import QuantumGate, _I, TOLERANCE


class CircuitOptimizer:
    def optimize(self, circuit: QuantumCircuit) -> QuantumCircuit:
        ops = list(circuit.ops)
        ops = self._cancel_adjacent_inverses(ops)
        ops = self._merge_single_qubit(ops)
        result = QuantumCircuit(circuit.n_qubits, name=circuit.name + "_opt")
        result.ops = ops
        return result

    def _cancel_adjacent_inverses(self, ops: List[CircuitOp]) -> List[CircuitOp]:
        result = []
        skip = set()
        for i in range(len(ops)):
            if i in skip:
                continue
            if i + 1 < len(ops) and ops[i].qubits == ops[i+1].qubits:
                product = ops[i+1].gate.matrix @ ops[i].gate.matrix
                if np.allclose(product, np.eye(product.shape[0]), atol=TOLERANCE):
                    skip.add(i + 1)
                    continue
            result.append(ops[i])
        return result

    def _merge_single_qubit(self, ops: List[CircuitOp]) -> List[CircuitOp]:
        result = []
        i = 0
        while i < len(ops):
            if (ops[i].gate.n_qubits == 1 and i + 1 < len(ops) and
                    ops[i+1].gate.n_qubits == 1 and ops[i].qubits == ops[i+1].qubits):
                merged = ops[i+1].gate.matrix @ ops[i].gate.matrix
                if np.allclose(merged, _I, atol=TOLERANCE):
                    i += 2
                    continue
                result.append(CircuitOp(QuantumGate(f"U_{i}", merged, ops[i].qubits), ops[i].qubits))
                i += 2
            else:
                result.append(ops[i])
                i += 1
        return result

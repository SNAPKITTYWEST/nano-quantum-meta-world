"""Verification helpers for digital circuits."""

from __future__ import annotations
from typing import List, Tuple
from .gates import Gate


def verify_truth_table(gate: Gate, expected: List[Tuple[Tuple[int, ...], Tuple[int, ...]]]) -> bool:
    actual = gate.truth_table()
    if len(actual) != len(expected):
        raise AssertionError(f"{gate.name}: truth table length {len(actual)} != expected {len(expected)}")
    for i, (a, e) in enumerate(zip(actual, expected)):
        if a != e:
            raise AssertionError(f"{gate.name}: row {i}: got {a}, expected {e}")
    return True


def verify_boolean_equivalence(gate_a: Gate, gate_b: Gate) -> bool:
    if gate_a.n_inputs != gate_b.n_inputs or gate_a.n_outputs != gate_b.n_outputs:
        raise AssertionError(f"Dimension mismatch: {gate_a.name} vs {gate_b.name}")
    ta = gate_a.truth_table()
    tb = gate_b.truth_table()
    if ta != tb:
        raise AssertionError(f"{gate_a.name} and {gate_b.name} are not equivalent")
    return True


def assert_all_gates_self_consistent(gates: List[Gate]) -> None:
    for g in gates:
        for inp, expected_out in g.truth_table():
            out = g.evaluate(list(inp))
            if tuple(out) != expected_out:
                raise AssertionError(f"{g.name}: evaluate({inp}) = {out}, expected {expected_out}")

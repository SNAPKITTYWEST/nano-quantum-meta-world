"""Control Unit and Finite-State Machine primitives."""

from __future__ import annotations
from typing import List, Dict, Any, Tuple


class FSM:
    """Explicit finite-state machine. Deterministic."""

    def __init__(self, states: List[str], initial: str, alphabet: List[str],
                 transitions: Dict[Tuple[str, str], Tuple[str, str]], name: str = "FSM"):
        if initial not in states:
            raise ValueError(f"Initial state {initial} not in states")
        self.name = name
        self.states = list(states)
        self.initial = initial
        self.alphabet = list(alphabet)
        self.transitions = dict(transitions)
        self.current = initial
        self.history: List[Dict[str, Any]] = []

    def reset(self) -> None:
        self.current = self.initial
        self.history.clear()

    def step(self, symbol: str) -> str:
        if symbol not in self.alphabet:
            raise ValueError(f"{self.name}: unknown input symbol '{symbol}'")
        key = (self.current, symbol)
        if key not in self.transitions:
            raise ValueError(f"{self.name}: no transition from {self.current} on '{symbol}'")
        next_state, output = self.transitions[key]
        self.history.append({"from": self.current, "input": symbol, "to": next_state, "output": output})
        self.current = next_state
        return output

    def run(self, inputs: List[str]) -> List[str]:
        return [self.step(s) for s in inputs]

    def structural_decomposition(self) -> Dict[str, Any]:
        return {
            "type": "FSM", "states": self.states, "initial": self.initial,
            "alphabet": self.alphabet, "n_transitions": len(self.transitions),
            "implementation_note": "Can be realized with state register + combinational next-state/output logic",
        }

    def serialize(self) -> Dict[str, Any]:
        return {
            "name": self.name, "states": self.states, "initial": self.initial,
            "alphabet": self.alphabet,
            "transitions": {f"{k[0]}|{k[1]}": list(v) for k, v in self.transitions.items()},
            "current": self.current,
        }


class ControlUnit:
    """Simple hardwired control unit for a toy processor."""

    def __init__(self):
        self.fsm = FSM(
            states=["FETCH", "DECODE", "EXECUTE", "WRITEBACK"],
            initial="FETCH", alphabet=["tick"],
            transitions={
                ("FETCH", "tick"): ("DECODE", "PC_inc, MemRead"),
                ("DECODE", "tick"): ("EXECUTE", "RegRead"),
                ("EXECUTE", "tick"): ("WRITEBACK", "ALU_op"),
                ("WRITEBACK", "tick"): ("FETCH", "RegWrite"),
            },
            name="ControlFSM",
        )
        self.control_signals: Dict[str, int] = {
            "PC_inc": 0, "MemRead": 0, "RegRead": 0,
            "ALU_op": 0, "RegWrite": 0, "MemWrite": 0,
        }

    def reset(self) -> None:
        self.fsm.reset()
        for k in self.control_signals:
            self.control_signals[k] = 0

    def tick(self) -> Dict[str, int]:
        raw = self.fsm.step("tick")
        for k in self.control_signals:
            self.control_signals[k] = 0
        for sig in raw.split(","):
            sig = sig.strip()
            if sig in self.control_signals:
                self.control_signals[sig] = 1
        return dict(self.control_signals)

    def structural_decomposition(self) -> Dict[str, Any]:
        return {
            "type": "ControlUnit",
            "fsm": self.fsm.structural_decomposition(),
            "signals": list(self.control_signals.keys()),
            "note": "Hardwired micro-state sequencer: FETCH->DECODE->EXECUTE->WRITEBACK",
        }

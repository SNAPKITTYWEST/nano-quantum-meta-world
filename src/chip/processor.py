"""Processor core and complete chip model."""

from __future__ import annotations
from typing import Dict, Any, List
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from digital.control import ControlUnit
from digital.pipeline import SimplePipeline
from digital.clock import Clock
from .datapath import DataPath
from .interconnect import Interconnect


class ProcessorCore:
    def __init__(self, width: int = 32, pipelined: bool = False):
        self.width = width
        self.datapath = DataPath(width=width)
        self.control = ControlUnit()
        self.pipeline = SimplePipeline() if pipelined else None
        self.clock = Clock(period=10.0)
        self.halted = False

    def reset(self) -> None:
        self.datapath.reset()
        self.control.reset()
        if self.pipeline:
            self.pipeline.reset()
        self.halted = False

    def step(self) -> Dict[str, Any]:
        if self.halted:
            return {"status": "halted"}
        signals = self.control.tick()
        self.clock.tick()
        return {
            "cycle": self.clock.cycle,
            "control": signals,
            "pc": self.datapath.pc.get_value(),
            "fsm_state": self.control.fsm.current,
        }

    def structural_decomposition(self) -> Dict[str, Any]:
        return {
            "type": "ProcessorCore", "width": self.width,
            "datapath": self.datapath.structural_decomposition(),
            "control": self.control.structural_decomposition(),
            "pipelined": self.pipeline is not None,
            "pipeline": self.pipeline.structural_decomposition() if self.pipeline else None,
        }


class Chip:
    """Complete chip: cores + interconnect + memory hierarchy."""

    def __init__(self, n_cores: int = 1, width: int = 32, pipelined: bool = False):
        self.n_cores = n_cores
        self.cores = [ProcessorCore(width=width, pipelined=pipelined) for _ in range(n_cores)]
        self.interconnect = Interconnect(n_cores=n_cores)
        self.name = "NanoQuantumExperimentalChip"

    def reset(self) -> None:
        for c in self.cores:
            c.reset()

    def step(self) -> List[Dict[str, Any]]:
        return [c.step() for c in self.cores]

    def structural_decomposition(self) -> Dict[str, Any]:
        return {
            "type": "Chip", "name": self.name, "n_cores": self.n_cores,
            "cores": [c.structural_decomposition() for c in self.cores],
            "interconnect": self.interconnect.structural_decomposition(),
            "hierarchy": [
                "TRANSISTOR / DEVICE MODEL", "LOGIC GATE",
                "COMBINATIONAL / SEQUENTIAL CIRCUIT", "REGISTER / ALU / CONTROL / FSM",
                "PROCESSOR CORE", "MEMORY / INTERCONNECT", "COMPLETE CHIP",
            ],
        }

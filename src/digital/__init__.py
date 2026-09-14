"""Hand-rolled digital circuit primitives and higher-level blocks."""

from .gates import (
    Gate, NOT, NAND, NOR, AND, OR, XOR, XNOR, MUX, DEMUX,
    HalfAdder, FullAdder, Comparator,
)
from .sequential import (
    Latch, DFlipFlop, JKFlipFlop, TFlipFlop,
    Register, ShiftRegister, Counter,
)
from .combinational import Decoder, Encoder
from .alu import ALU
from .control import ControlUnit, FSM
from .pipeline import PipelineStage, SimplePipeline
from .bus import Bus
from .memory import MemoryCell, RegisterFile, CacheModel
from .clock import Clock, TimingModel
from .serialization import CircuitSerializer
from .verification import verify_truth_table, verify_boolean_equivalence

__all__ = [
    "Gate", "NOT", "NAND", "NOR", "AND", "OR", "XOR", "XNOR", "MUX", "DEMUX",
    "HalfAdder", "FullAdder", "Comparator",
    "Latch", "DFlipFlop", "JKFlipFlop", "TFlipFlop",
    "Register", "ShiftRegister", "Counter",
    "Decoder", "Encoder", "ALU", "ControlUnit", "FSM",
    "PipelineStage", "SimplePipeline", "Bus",
    "MemoryCell", "RegisterFile", "CacheModel",
    "Clock", "TimingModel", "CircuitSerializer",
    "verify_truth_table", "verify_boolean_equivalence",
]

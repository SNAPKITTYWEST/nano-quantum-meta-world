"""Interconnect and memory hierarchy stubs."""

from __future__ import annotations
from typing import Dict, Any
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from digital.memory import CacheModel
from digital.bus import Bus


class Interconnect:
    """Simple hierarchical interconnect: cores <-> L1 <-> shared bus <-> memory."""

    def __init__(self, n_cores: int = 1):
        self.n_cores = n_cores
        self.l1_caches = [CacheModel(n_lines=32, line_size=8) for _ in range(n_cores)]
        self.shared_bus = Bus(width=32, name="SharedBus")
        self.main_memory = [0] * 1024

    def read(self, core_id: int, addr: int) -> int:
        hit, val = self.l1_caches[core_id].access(addr, write=False)
        if not hit:
            self.shared_bus.request(f"core{core_id}")
            self.shared_bus.grant()
            if 0 <= addr < len(self.main_memory):
                val = self.main_memory[addr]
            self.shared_bus.transfer(addr, val, write=False)
            self.shared_bus.release()
        return val

    def write(self, core_id: int, addr: int, value: int) -> None:
        self.l1_caches[core_id].access(addr, write=True, value=value)
        self.shared_bus.request(f"core{core_id}")
        self.shared_bus.grant()
        if 0 <= addr < len(self.main_memory):
            self.main_memory[addr] = value
        self.shared_bus.transfer(addr, value, write=True)
        self.shared_bus.release()

    def structural_decomposition(self) -> Dict[str, Any]:
        return {
            "type": "Interconnect", "n_cores": self.n_cores,
            "l1": "direct-mapped private caches",
            "bus": self.shared_bus.structural_decomposition(),
            "memory": f"{len(self.main_memory)} words",
        }

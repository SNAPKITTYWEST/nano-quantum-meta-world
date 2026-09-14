"""Simple shared bus model."""

from __future__ import annotations
from typing import List, Dict, Any, Optional


class Bus:
    """Multi-master / multi-slave bus with simple arbitration (priority)."""

    def __init__(self, width: int = 32, name: str = "SystemBus"):
        self.width = width
        self.name = name
        self.data = 0
        self.address = 0
        self.write_enable = 0
        self.valid = 0
        self.owner: Optional[str] = None
        self._request_queue: List[str] = []
        self.history: List[Dict[str, Any]] = []

    def request(self, master: str) -> None:
        if master not in self._request_queue:
            self._request_queue.append(master)

    def grant(self) -> Optional[str]:
        if not self._request_queue:
            self.owner = None
            return None
        self.owner = self._request_queue.pop(0)
        return self.owner

    def transfer(self, address: int, data: int, write: bool) -> None:
        if self.owner is None:
            raise RuntimeError(f"{self.name}: no owner for transfer")
        self.address = address & ((1 << 32) - 1)
        self.data = data & ((1 << self.width) - 1)
        self.write_enable = 1 if write else 0
        self.valid = 1
        self.history.append({"owner": self.owner, "address": self.address, "data": self.data, "write": write})

    def release(self) -> None:
        self.valid = 0
        self.write_enable = 0
        self.owner = None

    def structural_decomposition(self) -> Dict[str, Any]:
        return {"type": "Bus", "width": self.width, "arbitration": "priority queue (first-come)",
                "signals": ["address", "data", "write_enable", "valid", "owner"]}

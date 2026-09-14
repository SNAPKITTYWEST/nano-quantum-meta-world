"""Clock and timing model."""

from __future__ import annotations
from typing import List, Dict, Any, Callable


class Clock:
    def __init__(self, period: float = 10.0, name: str = "clk"):
        self.period = period
        self.name = name
        self.cycle = 0
        self.phase = 0.0
        self.subscribers: List[Callable[[int, float], None]] = []

    def tick(self) -> int:
        self.cycle += 1
        self.phase = 0.0
        for cb in self.subscribers:
            cb(self.cycle, self.phase)
        return self.cycle

    def half_tick(self) -> None:
        self.phase = 0.5
        for cb in self.subscribers:
            cb(self.cycle, self.phase)

    def subscribe(self, callback: Callable[[int, float], None]) -> None:
        self.subscribers.append(callback)

    def structural_decomposition(self) -> Dict[str, Any]:
        return {"type": "Clock", "period": self.period,
                "note": "Ideal clock; real designs include jitter, skew, PLL models"}


class TimingModel:
    """Simple static timing analysis stub for abstract delays."""

    def __init__(self):
        self.path_delays: Dict[str, float] = {}

    def add_path(self, name: str, delay: float) -> None:
        self.path_delays[name] = delay

    def critical_path(self) -> tuple:
        if not self.path_delays:
            return ("none", 0.0)
        name = max(self.path_delays, key=self.path_delays.get)
        return (name, self.path_delays[name])

    def meets_timing(self, clock_period: float) -> bool:
        _, crit = self.critical_path()
        return crit < clock_period

    def structural_decomposition(self) -> Dict[str, Any]:
        return {"type": "TimingModel", "paths": dict(self.path_delays), "note": "Abstract delay units only"}

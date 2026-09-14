"""Simple pipeline model with hazard detection stubs."""

from __future__ import annotations
from typing import List, Dict, Any


class PipelineStage:
    def __init__(self, name: str):
        self.name = name
        self.valid = False
        self.data: Dict[str, Any] = {}
        self.stall = False

    def clear(self) -> None:
        self.valid = False
        self.data = {}
        self.stall = False

    def load(self, data: Dict[str, Any]) -> None:
        self.valid = True
        self.data = dict(data)
        self.stall = False


class SimplePipeline:
    """Classic 5-stage pipeline: IF -> ID -> EX -> MEM -> WB. Supports bubble insertion on hazards."""

    STAGES = ["IF", "ID", "EX", "MEM", "WB"]

    def __init__(self):
        self.stages = {s: PipelineStage(s) for s in self.STAGES}
        self.cycle = 0
        self.history: List[Dict[str, Any]] = []
        self._instruction_queue: List[Dict[str, Any]] = []

    def reset(self) -> None:
        for s in self.stages.values():
            s.clear()
        self.cycle = 0
        self.history.clear()
        self._instruction_queue.clear()

    def enqueue(self, instr: Dict[str, Any]) -> None:
        self._instruction_queue.append(instr)

    def _detect_data_hazard(self) -> bool:
        id_stage = self.stages["ID"]
        ex_stage = self.stages["EX"]
        mem_stage = self.stages["MEM"]
        if not id_stage.valid:
            return False
        srcs = set(id_stage.data.get("src_regs", []))
        for st in (ex_stage, mem_stage):
            if st.valid and st.data.get("dst_reg") in srcs:
                return True
        return False

    def tick(self) -> Dict[str, Any]:
        self.cycle += 1
        snapshot = {"cycle": self.cycle, "stages": {}}
        if self.stages["WB"].valid:
            snapshot["retired"] = dict(self.stages["WB"].data)
            self.stages["WB"].clear()
        if self.stages["MEM"].valid and not self.stages["MEM"].stall:
            self.stages["WB"].load(self.stages["MEM"].data)
            self.stages["MEM"].clear()
        if self.stages["EX"].valid and not self.stages["EX"].stall:
            self.stages["MEM"].load(self.stages["EX"].data)
            self.stages["EX"].clear()
        hazard = self._detect_data_hazard()
        if hazard:
            self.stages["ID"].stall = True
            self.stages["EX"].clear()
            snapshot["hazard"] = "RAW"
        else:
            if self.stages["ID"].valid and not self.stages["ID"].stall:
                self.stages["EX"].load(self.stages["ID"].data)
                self.stages["ID"].clear()
        if self.stages["IF"].valid and not self.stages["IF"].stall:
            if not self.stages["ID"].valid:
                self.stages["ID"].load(self.stages["IF"].data)
                self.stages["IF"].clear()
        if not self.stages["IF"].valid and self._instruction_queue:
            instr = self._instruction_queue.pop(0)
            self.stages["IF"].load(instr)
        for name, st in self.stages.items():
            snapshot["stages"][name] = {"valid": st.valid, "stall": st.stall, "data": dict(st.data) if st.valid else None}
        self.history.append(snapshot)
        return snapshot

    def structural_decomposition(self) -> Dict[str, Any]:
        return {
            "type": "SimplePipeline", "stages": self.STAGES,
            "hazards": ["RAW data hazard -> stall + bubble"],
            "note": "Abstract model; real pipelines add forwarding, branch prediction, etc.",
        }

"""Circuit serialization / deserialization format."""

from __future__ import annotations
from typing import Dict, Any
import json
from .gates import Gate


class CircuitSerializer:
    @staticmethod
    def to_dict(gate: Gate) -> Dict[str, Any]:
        return gate.serialize()

    @staticmethod
    def to_json(gate: Gate, indent: int = 2) -> str:
        return json.dumps(gate.serialize(), indent=indent)

    @staticmethod
    def truth_table_to_dict(gate: Gate) -> Dict[str, Any]:
        rows = []
        for inp, out in gate.truth_table():
            rows.append({"inputs": list(inp), "outputs": list(out)})
        return {"name": gate.name, "truth_table": rows, "boolean": gate.boolean_expression(),
                "structure": gate.structural_decomposition()}

    @staticmethod
    def dump_truth_table(gate: Gate) -> str:
        return json.dumps(CircuitSerializer.truth_table_to_dict(gate), indent=2)

"""META-WORLD: formal, deterministic state-transition system."""

from __future__ import annotations
from typing import Dict, List, Tuple, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import json


class ObjectType(Enum):
    AGENT = "agent"
    RESOURCE = "resource"
    OBSTACLE = "obstacle"
    SIGNAL = "signal"
    QUANTUM_STATE = "quantum_state"


@dataclass
class WorldObject:
    object_id: str
    object_type: ObjectType
    spiral_node: int
    attributes: Dict[str, Any] = field(default_factory=dict)

    def __hash__(self): return hash(self.object_id)
    def __eq__(self, other): return isinstance(other, WorldObject) and self.object_id == other.object_id


@dataclass
class Relation:
    rel_type: str
    obj_a: WorldObject
    obj_b: WorldObject
    strength: float = 1.0

    def __hash__(self): return hash((self.rel_type, self.obj_a.object_id, self.obj_b.object_id))
    def __eq__(self, other):
        return (isinstance(other, Relation) and self.rel_type == other.rel_type and
                self.obj_a == other.obj_a and self.obj_b == other.obj_b)


class TransitionRule:
    def __init__(self, name: str, preconditions, action):
        self.name = name
        self.preconditions = preconditions
        self.action = action

    def applies(self, world: MetaWorld) -> bool:
        try: return self.preconditions(world)
        except Exception: return False

    def apply(self, world: MetaWorld) -> MetaWorld:
        if not self.applies(world):
            raise ValueError(f"Rule '{self.name}' preconditions not satisfied")
        return self.action(world)


@dataclass
class WorldState:
    timestamp: int
    objects: Set[WorldObject] = field(default_factory=set)
    relations: Set[Relation] = field(default_factory=set)
    property_values: Dict[str, float] = field(default_factory=dict)

    def copy(self) -> WorldState:
        return WorldState(
            timestamp=self.timestamp,
            objects=self.objects.copy(),
            relations=self.relations.copy(),
            property_values=self.property_values.copy(),
        )


class MetaWorld:
    def __init__(self, spiral_topology=None):
        self.spiral_topology = spiral_topology
        self.state = WorldState(timestamp=0)
        self.rules: List[TransitionRule] = []
        self.history: List[WorldState] = [self.state.copy()]
        self.transition_log: List[Tuple[int, str, WorldState]] = []

    def add_object(self, obj: WorldObject):
        if obj in self.state.objects:
            raise ValueError(f"Object {obj.object_id} already exists")
        self.state.objects.add(obj)

    def remove_object(self, obj: WorldObject):
        self.state.objects.discard(obj)
        self.state.relations = {r for r in self.state.relations if r.obj_a != obj and r.obj_b != obj}

    def add_relation(self, rel: Relation):
        self.state.relations.add(rel)

    def remove_relation(self, rel: Relation):
        self.state.relations.discard(rel)

    def get_object(self, object_id: str) -> Optional[WorldObject]:
        for obj in self.state.objects:
            if obj.object_id == object_id:
                return obj
        return None

    def get_neighbors(self, obj: WorldObject) -> List[WorldObject]:
        neighbors = []
        for rel in self.state.relations:
            if rel.rel_type == "neighbor":
                if rel.obj_a == obj: neighbors.append(rel.obj_b)
                elif rel.obj_b == obj: neighbors.append(rel.obj_a)
        return neighbors

    def add_rule(self, rule: TransitionRule):
        self.rules.append(rule)

    def observe(self) -> Dict[str, Any]:
        obs = {"num_objects": len(self.state.objects), "object_types": {},
               "relations_count": len(self.state.relations), "timestamp": self.state.timestamp}
        for obj in self.state.objects:
            t = obj.object_type.value
            obs["object_types"][t] = obs["object_types"].get(t, 0) + 1
        return obs

    def step(self) -> bool:
        applicable = [r for r in self.rules if r.applies(self)]
        if not applicable:
            return False
        rule = applicable[0]
        old_state = self.state.copy()
        new_world = MetaWorld(self.spiral_topology)
        new_world.state = self.state.copy()
        new_world.rules = self.rules
        rule.apply(new_world)
        self.state = new_world.state
        self.state.timestamp += 1
        self.history.append(self.state.copy())
        self.transition_log.append((self.state.timestamp - 1, rule.name, old_state))
        return True

    def run_until_stable(self, max_steps: int = 1000) -> int:
        steps = 0
        while steps < max_steps and self.step():
            steps += 1
        return steps

    def verify_invariant(self, invariant) -> bool:
        for state in self.history:
            temp = MetaWorld(self.spiral_topology)
            temp.state = state
            if not invariant(temp):
                return False
        return True

    def get_state_snapshot(self) -> Dict:
        return {
            "timestamp": self.state.timestamp,
            "num_objects": len(self.state.objects),
            "num_relations": len(self.state.relations),
            "objects": [{"id": o.object_id, "type": o.object_type.value,
                         "spiral_node": o.spiral_node, "attributes": o.attributes}
                        for o in self.state.objects],
            "relations": [{"type": r.rel_type, "obj_a": r.obj_a.object_id,
                           "obj_b": r.obj_b.object_id, "strength": r.strength}
                          for r in self.state.relations],
        }


# Aliases for demo compatibility
Object = WorldObject
Agent = lambda oid, node, **attrs: WorldObject(oid, ObjectType.AGENT, node, attrs)

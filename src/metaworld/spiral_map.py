"""Spiral-mapped meta-world integration."""

from __future__ import annotations
from typing import Dict, Any, Optional
from .world import MetaWorld, WorldObject, ObjectType, Relation, TransitionRule


class SpiralMetaWorld(MetaWorld):
    """Meta-world with objects mapped to spiral topology nodes."""

    def __init__(self, spiral_topology=None):
        super().__init__(spiral_topology)

    def add_agent(self, agent_id: str, spiral_node: int, **attributes) -> WorldObject:
        obj = WorldObject(agent_id, ObjectType.AGENT, spiral_node, attributes)
        self.add_object(obj)
        return obj

    def add_resource(self, res_id: str, spiral_node: int, **attributes) -> WorldObject:
        obj = WorldObject(res_id, ObjectType.RESOURCE, spiral_node, attributes)
        self.add_object(obj)
        return obj

    def connect_neighbors(self) -> int:
        if self.spiral_topology is None:
            return 0
        count = 0
        objs = list(self.state.objects)
        for i, a in enumerate(objs):
            for b in objs[i+1:]:
                if b.spiral_node in [n.node_id for n in self.spiral_topology.get_neighbors(a.spiral_node)]:
                    self.add_relation(Relation("neighbor", a, b))
                    count += 1
        return count

    def move_object(self, obj: WorldObject, new_node: int) -> None:
        obj.spiral_node = new_node

    def objects_at_node(self, node_id: int):
        return [o for o in self.state.objects if o.spiral_node == node_id]

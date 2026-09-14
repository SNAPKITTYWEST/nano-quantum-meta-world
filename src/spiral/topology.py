"""Logarithmic-spiral topology for computational node organization."""

from __future__ import annotations
from typing import List, Dict, Tuple
from dataclasses import dataclass
import math
import numpy as np


@dataclass
class SpiralParameters:
    a: float = 1.0
    b: float = 0.3
    max_turns: float = 10.0

    def radius(self, theta: float) -> float:
        return self.a * math.exp(self.b * theta)

    def cartesian(self, theta: float) -> Tuple[float, float]:
        r = self.radius(theta)
        return (r * math.cos(theta), r * math.sin(theta))


@dataclass
class ComputationalNode:
    node_id: int
    theta: float
    r: float
    x: float
    y: float
    node_type: str = "compute"

    def euclidean_distance(self, other: ComputationalNode) -> float:
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)


class LogSpiralTopology:
    def __init__(self, params: SpiralParameters, num_nodes: int):
        self.params = params
        self.num_nodes = num_nodes
        self.nodes: Dict[int, ComputationalNode] = {}
        self.adjacency: Dict[int, List[int]] = {}
        self._init_nodes()
        self._build_adjacency()

    def _init_nodes(self):
        max_theta = self.params.max_turns * 2 * np.pi
        for i in range(self.num_nodes):
            theta = (i / self.num_nodes) * max_theta
            r = self.params.radius(theta)
            x, y = self.params.cartesian(theta)
            norm = i / self.num_nodes
            ntype = "io" if norm < 0.25 else "quantum" if norm < 0.5 else "compute" if norm < 0.75 else "memory"
            self.nodes[i] = ComputationalNode(i, theta, r, x, y, ntype)

    def _build_adjacency(self):
        threshold = 2 * np.pi / self.num_nodes * 2.5
        for nid, node in self.nodes.items():
            neighbors = []
            for oid, other in self.nodes.items():
                if nid == oid:
                    continue
                dt = min(abs(node.theta - other.theta), 2 * np.pi - abs(node.theta - other.theta))
                if dt <= threshold:
                    neighbors.append(oid)
            self.adjacency[nid] = neighbors

    def get_neighbors(self, node_id: int) -> List[ComputationalNode]:
        return [self.nodes[n] for n in self.adjacency.get(node_id, [])]

    def path_length(self, a: int, b: int) -> float:
        visited = {a}
        queue = [(a, 0.0)]
        while queue:
            current, dist = queue.pop(0)
            if current == b:
                return dist
            for n in self.adjacency.get(current, []):
                if n not in visited:
                    visited.add(n)
                    edge = self.nodes[current].euclidean_distance(self.nodes[n])
                    queue.append((n, dist + edge))
        return float('inf')

    def average_degree(self) -> float:
        total = sum(len(v) for v in self.adjacency.values())
        return total / self.num_nodes if self.num_nodes else 0

    def connectivity_analysis(self) -> Dict:
        degrees = [len(self.adjacency[n]) for n in self.nodes]
        sample = list(self.nodes.keys())[:10]
        diam = 0.0
        for i, a in enumerate(sample):
            for b in sample[i+1:]:
                d = self.path_length(a, b)
                if d != float('inf') and d > diam:
                    diam = d
        return {
            "num_nodes": self.num_nodes, "average_degree": self.average_degree(),
            "max_degree": max(degrees) if degrees else 0,
            "min_degree": min(degrees) if degrees else 0,
            "diameter_sample": diam,
            "spiral_parameters": {"a": self.params.a, "b": self.params.b, "max_turns": self.params.max_turns},
        }


class GridTopology:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.num_nodes = width * height
        self.nodes: Dict[int, ComputationalNode] = {}
        self.adjacency: Dict[int, List[int]] = {}
        nid = 0
        for y in range(height):
            for x in range(width):
                self.nodes[nid] = ComputationalNode(nid, 0.0, 0.0, float(x), float(y), "compute")
                nid += 1
        for nid in self.nodes:
            x = nid % width
            y = nid // width
            neighbors = []
            if x > 0: neighbors.append(nid - 1)
            if x < width - 1: neighbors.append(nid + 1)
            if y > 0: neighbors.append(nid - width)
            if y < height - 1: neighbors.append(nid + width)
            self.adjacency[nid] = neighbors

    def average_degree(self) -> float:
        total = sum(len(v) for v in self.adjacency.values())
        return total / self.num_nodes if self.num_nodes else 0


def compare_topologies(spiral: LogSpiralTopology, grid: GridTopology) -> Dict:
    return {
        "spiral": {"nodes": spiral.num_nodes, "avg_degree": spiral.average_degree()},
        "grid": {"nodes": grid.num_nodes, "avg_degree": grid.average_degree()},
    }

"""Spiral topology and meta-world verification."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from spiral.topology import SpiralParameters, LogSpiralTopology, GridTopology, compare_topologies
from metaworld.world import MetaWorld, WorldObject, ObjectType, Relation, TransitionRule
from metaworld.spiral_map import SpiralMetaWorld


def test_spiral_topology():
    params = SpiralParameters(a=1.0, b=0.3, max_turns=3)
    spiral = LogSpiralTopology(params, num_nodes=16)
    assert len(spiral.nodes) == 16
    assert spiral.average_degree() > 0
    analysis = spiral.connectivity_analysis()
    print(f"[PASS] Spiral topology: {analysis['num_nodes']} nodes, avg_degree={analysis['average_degree']:.2f}")


def test_grid_topology():
    grid = GridTopology(4, 4)
    assert grid.num_nodes == 16
    assert grid.average_degree() > 0
    print(f"[PASS] Grid topology: {grid.num_nodes} nodes, avg_degree={grid.average_degree():.2f}")


def test_metaworld_determinism():
    def make_world():
        w = MetaWorld()
        w.add_object(WorldObject("a1", ObjectType.AGENT, 0, {"energy": 10}))
        w.add_object(WorldObject("a2", ObjectType.AGENT, 1))
        w.add_object(WorldObject("r1", ObjectType.RESOURCE, 2, {"quantity": 5}))
        def pre(mw): return len([o for o in mw.state.objects if o.object_type == ObjectType.AGENT]) >= 2
        def act(mw):
            agents = [o for o in mw.state.objects if o.object_type == ObjectType.AGENT]
            mw.add_relation(Relation("neighbor", agents[0], agents[1]))
            return mw
        w.add_rule(TransitionRule("connect", pre, act))
        return w

    w1 = make_world()
    w2 = make_world()
    s1 = w1.run_until_stable(10)
    s2 = w2.run_until_stable(10)
    assert s1 == s2
    assert len(w1.state.objects) == len(w2.state.objects)
    print(f"[PASS] Meta-world determinism ({s1} steps)")


def test_spiral_metaworld():
    params = SpiralParameters(a=1.0, b=0.2, max_turns=2)
    spiral = LogSpiralTopology(params, num_nodes=8)
    smw = SpiralMetaWorld(spiral)
    smw.add_agent("agent_0", 0, energy=10)
    smw.add_agent("agent_1", 2, energy=8)
    smw.add_resource("res_0", 1, quantity=20)
    assert len(smw.state.objects) == 3
    print("[PASS] SpiralMetaWorld")


if __name__ == "__main__":
    test_spiral_topology()
    test_grid_topology()
    test_metaworld_determinism()
    test_spiral_metaworld()
    print("\nAll spiral/metaworld tests passed.")

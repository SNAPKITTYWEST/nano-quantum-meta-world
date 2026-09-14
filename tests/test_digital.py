"""Digital circuit verification suite."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from digital.gates import NAND, NOT, NOR, AND, OR, XOR, XNOR, MUX, DEMUX, HalfAdder, FullAdder, Comparator
from digital.sequential import DFlipFlop, Register, Counter
from digital.alu import ALU
from digital.control import FSM, ControlUnit
from digital.pipeline import SimplePipeline
from digital.verification import assert_all_gates_self_consistent


def test_gates():
    gates = [NAND(), NOT(), NOR(), AND(), OR(), XOR(), XNOR(), MUX(), DEMUX(), HalfAdder(), FullAdder(), Comparator()]
    assert_all_gates_self_consistent(gates)
    print(f"[PASS] {len(gates)} gates self-consistent")


def test_nand_universality():
    nand = NAND()
    assert nand.evaluate([0, 0]) == [1]
    assert nand.evaluate([1, 1]) == [0]
    print("[PASS] NAND universal gate")


def test_full_adder():
    fa = FullAdder()
    assert fa.evaluate([1, 1, 0]) == [0, 1]
    assert fa.evaluate([1, 1, 1]) == [1, 1]
    assert fa.evaluate([0, 0, 0]) == [0, 0]
    print("[PASS] FullAdder")


def test_alu():
    alu = ALU(width=8)
    r, f = alu.run(42, 21, 0b000)
    assert r == 63
    r, f = alu.run(0xFF, 0x0F, 0b010)
    assert r == 0x0F
    print("[PASS] ALU")


def test_fsm():
    cu = ControlUnit()
    states_seen = set()
    for _ in range(8):
        cu.tick()
        states_seen.add(cu.fsm.current)
    assert states_seen == {"FETCH", "DECODE", "EXECUTE", "WRITEBACK"}
    print("[PASS] FSM/ControlUnit")


def test_pipeline():
    pipe = SimplePipeline()
    pipe.enqueue({"op": "ADD", "src_regs": [1, 2], "dst_reg": 3})
    pipe.enqueue({"op": "SUB", "src_regs": [3, 4], "dst_reg": 5})
    for _ in range(8):
        pipe.tick()
    assert pipe.cycle == 8
    print("[PASS] Pipeline")


if __name__ == "__main__":
    test_gates()
    test_nand_universality()
    test_full_adder()
    test_alu()
    test_fsm()
    test_pipeline()
    print("\nAll digital tests passed.")

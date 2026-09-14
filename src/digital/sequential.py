"""Sequential elements: latches, flip-flops, registers, counters."""

from __future__ import annotations
from typing import List, Dict, Any
from .gates import Gate


class Latch(Gate):
    """SR Latch (NOR-based). Inputs: S, R. Output: Q, Qbar."""
    name = "Latch"
    n_inputs = 2
    n_outputs = 2
    delay = 2.0

    def __init__(self):
        super().__init__()
        self._q = 0
        self._qbar = 1

    def evaluate(self, inputs: List[int]) -> List[int]:
        s, r = inputs
        if s == 1 and r == 0:
            self._q, self._qbar = 1, 0
        elif s == 0 and r == 1:
            self._q, self._qbar = 0, 1
        elif s == 1 and r == 1:
            pass  # invalid / hold
        return [self._q, self._qbar]

    def boolean_expression(self) -> str:
        return "Q = ¬(R ∨ Qbar), Qbar = ¬(S ∨ Q) (cross-coupled NOR)"

    def structural_decomposition(self) -> Dict[str, Any]:
        return {"type": "SR-Latch", "built_from": "two cross-coupled NOR gates", "primitive": False}


class DFlipFlop(Gate):
    """Edge-triggered D flip-flop (positive edge). Inputs: D, CLK. Output: Q."""
    name = "DFlipFlop"
    n_inputs = 2
    n_outputs = 1
    delay = 4.0

    def __init__(self):
        super().__init__()
        self._q = 0
        self._prev_clk = 0

    def evaluate(self, inputs: List[int]) -> List[int]:
        d, clk = inputs
        if self._prev_clk == 0 and clk == 1:
            self._q = d
        self._prev_clk = clk
        return [self._q]

    def boolean_expression(self) -> str:
        return "Q(next) = D on rising CLK"

    def structural_decomposition(self) -> Dict[str, Any]:
        return {"type": "D-FF", "built_from": "master-slave latches or edge detection + latch", "primitive": False}

    def reset(self) -> None:
        self._q = 0
        self._prev_clk = 0


class JKFlipFlop(Gate):
    """JK flip-flop. Inputs: J, K, CLK. Output: Q."""
    name = "JKFlipFlop"
    n_inputs = 3
    n_outputs = 1
    delay = 5.0

    def __init__(self):
        super().__init__()
        self._q = 0
        self._prev_clk = 0

    def evaluate(self, inputs: List[int]) -> List[int]:
        j, k, clk = inputs
        if self._prev_clk == 0 and clk == 1:
            if j == 0 and k == 0:
                pass
            elif j == 0 and k == 1:
                self._q = 0
            elif j == 1 and k == 0:
                self._q = 1
            else:
                self._q = 1 - self._q
        self._prev_clk = clk
        return [self._q]

    def boolean_expression(self) -> str:
        return "Q(next) = J¬Q + ¬K Q (on rising CLK)"

    def structural_decomposition(self) -> Dict[str, Any]:
        return {"type": "JK-FF", "built_from": "gated SR or D-FF with feedback", "primitive": False}

    def reset(self) -> None:
        self._q = 0
        self._prev_clk = 0


class TFlipFlop(Gate):
    """T (toggle) flip-flop. Inputs: T, CLK. Output: Q."""
    name = "TFlipFlop"
    n_inputs = 2
    n_outputs = 1
    delay = 5.0

    def __init__(self):
        super().__init__()
        self._q = 0
        self._prev_clk = 0

    def evaluate(self, inputs: List[int]) -> List[int]:
        t, clk = inputs
        if self._prev_clk == 0 and clk == 1:
            if t == 1:
                self._q = 1 - self._q
        self._prev_clk = clk
        return [self._q]

    def boolean_expression(self) -> str:
        return "Q(next) = T ⊕ Q (on rising CLK)"

    def structural_decomposition(self) -> Dict[str, Any]:
        return {"type": "T-FF", "built_from": "JK with J=K=T", "primitive": False}

    def reset(self) -> None:
        self._q = 0
        self._prev_clk = 0


class Register(Gate):
    """N-bit register of D flip-flops. Parallel load on rising CLK when load=1."""
    name = "Register"

    def __init__(self, width: int = 8):
        self.width = width
        self.n_inputs = width + 2  # data bits + CLK + LOAD
        self.n_outputs = width
        self.delay = 5.0
        self._inputs = [0] * self.n_inputs
        self._outputs = [0] * self.n_outputs
        self._history: List[Dict] = []
        self._value = 0
        self._prev_clk = 0

    def evaluate(self, inputs: List[int]) -> List[int]:
        data = inputs[:self.width]
        clk = inputs[self.width]
        load = inputs[self.width + 1]
        if self._prev_clk == 0 and clk == 1 and load == 1:
            self._value = 0
            for i, b in enumerate(data):
                self._value |= (b << (self.width - 1 - i))
        self._prev_clk = clk
        return [(self._value >> (self.width - 1 - i)) & 1 for i in range(self.width)]

    def get_value(self) -> int:
        return self._value

    def reset(self) -> None:
        self._value = 0
        self._prev_clk = 0

    def boolean_expression(self) -> str:
        return f"{self.width}-bit parallel load register (D-FF array)"

    def structural_decomposition(self) -> Dict[str, Any]:
        return {"type": "Register", "width": self.width, "built_from": f"{self.width} × D-FF with shared CLK/LOAD", "primitive": False}


class ShiftRegister(Gate):
    """N-bit shift register. Inputs: Din, CLK, direction (0=left, 1=right). Output: N bits."""
    name = "ShiftRegister"

    def __init__(self, width: int = 8):
        self.width = width
        self.n_inputs = 3  # Din, CLK, Direction
        self.n_outputs = width
        self.delay = 5.0
        self._inputs = [0] * self.n_inputs
        self._outputs = [0] * self.n_outputs
        self._history: List[Dict] = []
        self._bits = [0] * width
        self._prev_clk = 0

    def evaluate(self, inputs: List[int]) -> List[int]:
        din, clk, direction = inputs
        if self._prev_clk == 0 and clk == 1:
            if direction == 0:  # shift left
                self._bits = self._bits[1:] + [din]
            else:  # shift right
                self._bits = [din] + self._bits[:-1]
        self._prev_clk = clk
        return list(self._bits)

    def reset(self) -> None:
        self._bits = [0] * self.width
        self._prev_clk = 0

    def boolean_expression(self) -> str:
        return f"{self.width}-bit shift register"

    def structural_decomposition(self) -> Dict[str, Any]:
        return {"type": "ShiftRegister", "width": self.width, "built_from": "chain of D-FFs with MUX for direction", "primitive": False}


class Counter(Gate):
    """N-bit binary counter. Inputs: CLK, RESET, ENABLE. Output: N bits."""
    name = "Counter"

    def __init__(self, width: int = 8):
        self.width = width
        self.n_inputs = 3  # CLK, RESET, ENABLE
        self.n_outputs = width
        self.delay = 6.0
        self._inputs = [0] * self.n_inputs
        self._outputs = [0] * self.n_outputs
        self._history: List[Dict] = []
        self._count = 0
        self._prev_clk = 0

    def evaluate(self, inputs: List[int]) -> List[int]:
        clk, reset, enable = inputs
        if reset == 1:
            self._count = 0
        elif self._prev_clk == 0 and clk == 1 and enable == 1:
            self._count = (self._count + 1) % (1 << self.width)
        self._prev_clk = clk
        return [(self._count >> (self.width - 1 - i)) & 1 for i in range(self.width)]

    def get_count(self) -> int:
        return self._count

    def reset(self) -> None:
        self._count = 0
        self._prev_clk = 0

    def boolean_expression(self) -> str:
        return f"{self.width}-bit binary up counter"

    def structural_decomposition(self) -> Dict[str, Any]:
        return {"type": "Counter", "width": self.width, "built_from": "chain of T-FFs (ripple) or synchronous with carry look-ahead", "primitive": False}

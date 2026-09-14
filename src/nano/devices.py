"""Abstract nanoscale device models. Software abstraction only."""

from __future__ import annotations
from typing import Dict, Any
from abc import ABC, abstractmethod
import math


class NanoDevice(ABC):
    name: str = "NanoDevice"

    def __init__(self, **params):
        self.params = dict(params)

    @abstractmethod
    def abstract_to_gate(self) -> Dict[str, Any]:
        ...

    def describe(self) -> Dict[str, Any]:
        return {"type": self.name, "parameters": self.params,
                "note": "Software abstraction only; not a fabricated device"}


class NanoTransistor(NanoDevice):
    name = "NanoTransistor"

    def __init__(self, L_nm: float = 5.0, W_nm: float = 10.0, tox_nm: float = 1.0,
                 Vth: float = 0.2, mobility_proxy: float = 1.0, **kwargs):
        super().__init__(L_nm=L_nm, W_nm=W_nm, tox_nm=tox_nm, Vth=Vth,
                         mobility_proxy=mobility_proxy, **kwargs)

    def abstract_to_gate(self) -> Dict[str, Any]:
        delay_proxy = self.params["L_nm"] / max(self.params["mobility_proxy"], 1e-9)
        return {"gate_type": "abstract_switch", "delay_proxy": delay_proxy,
                "drive_strength_proxy": self.params["W_nm"] / self.params["L_nm"],
                "note": "Idealized digital abstraction; not a SPICE model"}


class QuantumDot(NanoDevice):
    name = "QuantumDot"

    def __init__(self, diameter_nm: float = 5.0, charging_energy_proxy: float = 1.0,
                 tunnel_rate_proxy: float = 1.0, **kwargs):
        super().__init__(diameter_nm=diameter_nm, charging_energy_proxy=charging_energy_proxy,
                         tunnel_rate_proxy=tunnel_rate_proxy, **kwargs)

    def abstract_to_gate(self) -> Dict[str, Any]:
        return {"gate_type": "single_electron_switch_proxy",
                "energy_scale": self.params["charging_energy_proxy"],
                "rate_proxy": self.params["tunnel_rate_proxy"],
                "note": "Conceptual only; not a real Coulomb-blockade simulation"}


class NanoWire(NanoDevice):
    name = "NanoWire"

    def __init__(self, length_nm: float = 50.0, diameter_nm: float = 2.0,
                 resistivity_proxy: float = 1.0, **kwargs):
        super().__init__(length_nm=length_nm, diameter_nm=diameter_nm,
                         resistivity_proxy=resistivity_proxy, **kwargs)

    def abstract_to_gate(self) -> Dict[str, Any]:
        R = self.params["resistivity_proxy"] * self.params["length_nm"] / max(self.params["diameter_nm"] ** 2, 1e-12)
        return {"interconnect_resistance_proxy": R, "note": "Abstract RC delay contribution"}


class TunnelJunction(NanoDevice):
    name = "TunnelJunction"

    def __init__(self, barrier_height_proxy: float = 1.0, width_nm: float = 1.0, **kwargs):
        super().__init__(barrier_height_proxy=barrier_height_proxy, width_nm=width_nm, **kwargs)

    def abstract_to_gate(self) -> Dict[str, Any]:
        T = math.exp(-self.params["barrier_height_proxy"] * self.params["width_nm"])
        return {"tunnel_probability_proxy": T, "note": "Phenomenological only"}


class NanoCapacitor(NanoDevice):
    name = "NanoCapacitor"

    def __init__(self, area_nm2: float = 25.0, separation_nm: float = 1.0,
                 epsilon_proxy: float = 1.0, **kwargs):
        super().__init__(area_nm2=area_nm2, separation_nm=separation_nm,
                         epsilon_proxy=epsilon_proxy, **kwargs)

    def abstract_to_gate(self) -> Dict[str, Any]:
        C = self.params["epsilon_proxy"] * self.params["area_nm2"] / max(self.params["separation_nm"], 1e-12)
        return {"capacitance_proxy": C, "note": "Abstract timing contribution"}


class NanoResistor(NanoDevice):
    name = "NanoResistor"

    def __init__(self, length_nm: float = 10.0, cross_section_nm2: float = 4.0,
                 resistivity_proxy: float = 1.0, **kwargs):
        super().__init__(length_nm=length_nm, cross_section_nm2=cross_section_nm2,
                         resistivity_proxy=resistivity_proxy, **kwargs)

    def abstract_to_gate(self) -> Dict[str, Any]:
        R = self.params["resistivity_proxy"] * self.params["length_nm"] / max(self.params["cross_section_nm2"], 1e-12)
        return {"resistance_proxy": R, "note": "Abstract model"}


class MolecularSwitch(NanoDevice):
    name = "MolecularSwitch"

    def __init__(self, switching_energy_proxy: float = 0.5, retention_proxy: float = 0.9, **kwargs):
        super().__init__(switching_energy_proxy=switching_energy_proxy,
                         retention_proxy=retention_proxy, **kwargs)

    def abstract_to_gate(self) -> Dict[str, Any]:
        return {"gate_type": "molecular_bistable",
                "switching_energy": self.params["switching_energy_proxy"],
                "retention": self.params["retention_proxy"],
                "note": "Conceptual molecular logic element"}

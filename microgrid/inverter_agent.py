"""
Distributed Energy Resource (DER) Converter Agent.
Models non-linear primary P-f droop dynamics and secondary frequency restoration loops.
"""
from dataclasses import dataclass
from typing import Dict


@dataclass
class InverterParameters:
    inverter_id: int
    rated_power_kw: float
    droop_kp: float = 0.05       # Droop gain (Hz/kW)
    nominal_freq_hz: float = 50.0
    soc_capacity_kwh: float = 100.0


class DERInverterAgent:
    def __init__(self, params: InverterParameters, initial_soc: float = 0.85):
        self.params = params
        self.soc = float(initial_soc)  # Normalised SoC [0.0, 1.0]
        self.p_output_kw = 0.0
        self.local_frequency = self.params.nominal_freq_hz
        self.secondary_correction = 0.0

    def compute_primary_droop(self, load_demand_kw: float) -> float:
        """
        Primary droop control: f_local = f_nom - Kp * (P_load) + Delta_f_sec
        """
        self.p_output_kw = load_demand_kw
        droop_drop = self.params.droop_kp * self.p_output_kw
        self.local_frequency = (
            self.params.nominal_freq_hz - droop_drop + self.secondary_correction
        )
        return self.local_frequency

    def update_soc(self, dt_seconds: float) -> float:
        """Coulomb counting battery SoC discharge dynamics."""
        energy_kwh = (self.p_output_kw * dt_seconds) / 3600.0
        self.soc -= energy_kwh / self.params.soc_capacity_kwh
        self.soc = max(0.0, min(1.0, self.soc))
        return self.soc

    def telemetry_packet(self) -> Dict[str, float]:
        """Broadcast state vector across the multi-agent mesh."""
        return {
            "node_id": float(self.params.inverter_id),
            "frequency_hz": float(self.local_frequency),
            "soc": float(self.soc),
            "p_kw": float(self.p_output_kw),
        }
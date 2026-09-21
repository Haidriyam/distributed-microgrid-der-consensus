import unittest
import numpy as np
from microgrid.inverter_agent import DERInverterAgent, InverterParameters
from microgrid.byzantine_consensus import WMSRConsensusCoordinator


class TestMicrogridConsensus(unittest.TestCase):

    def setUp(self):
        # 6-node fully connected communication graph
        self.num_nodes = 6
        self.adj = np.ones((self.num_nodes, self.num_nodes)) - np.eye(self.num_nodes)
        self.coordinator = WMSRConsensusCoordinator(
            num_nodes=self.num_nodes, byzantine_tolerance_f=1, alpha=0.4
        )

        # Initialize inverters under different load demands
        self.agents = [
            DERInverterAgent(
                InverterParameters(inverter_id=i, rated_power_kw=100.0, droop_kp=0.004),
                initial_soc=0.80 + i * 0.02,
            )
            for i in range(self.num_nodes)
        ]

    def test_primary_droop_response(self):
        # 50 kW load induces 50 * 0.004 = 0.2 Hz drop -> 49.8 Hz
        agent = self.agents[0]
        freq = agent.compute_primary_droop(load_demand_kw=50.0)
        self.assertAlmostEqual(freq, 49.8, places=2)

    def test_wmsr_mitigation_under_fdi_injection(self):
        # Node 2 is compromised, broadcasting 55.0 Hz (+5.0 Hz anomaly)
        corrupted_node = 2
        fdi_attack = {corrupted_node: 55.0}

        # Initialize honest nodes with droop-depressed frequencies (49.4 to 49.7 Hz)
        frequencies = [49.4, 49.5, 55.0, 49.6, 49.7, 49.5]

        # Iterate consensus for 40 steps
        for _ in range(40):
            frequencies = self.coordinator.step_mesh(
                frequencies=frequencies,
                adjacency_matrix=self.adj,
                fdi_corruptions=fdi_attack,
            )

        honest_indices = [i for i in range(self.num_nodes) if i != corrupted_node]
        honest_freqs = [frequencies[i] for i in honest_indices]

        # All honest nodes must converge to the same value despite the +5.0 Hz attacker
        spread = max(honest_freqs) - min(honest_freqs)
        self.assertLess(spread, 0.02)
        # Attacker's false 55 Hz must NOT pull honest nodes away from the nominal band
        self.assertLess(max(honest_freqs), 50.0)


if __name__ == "__main__":
    unittest.main()
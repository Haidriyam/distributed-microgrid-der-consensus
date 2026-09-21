"""
Weighted Mean Subsequence Reduced (W-MSR) Byzantine-Resilient Consensus Engine.
Ensures frequency restoration and balanced SoC without a centralized controller.
"""
from typing import Dict, List
import numpy as np


class WMSRConsensusCoordinator:
    def __init__(self, num_nodes: int, byzantine_tolerance_f: int = 1, alpha: float = 0.3):
        self.n = num_nodes
        self.f = byzantine_tolerance_f
        self.alpha = alpha  # Consensus convergence rate

    def filter_and_update(
        self,
        node_id: int,
        local_value: float,
        neighbor_values: Dict[int, float],
    ) -> float:
        """
        Execute W-MSR consensus step for a single state variable:
        1. Collect local and neighbor values.
        2. Filter out top-F values strictly greater than local_value.
        3. Filter out bottom-F values strictly smaller than local_value.
        4. Compute convex combination of the remaining subset.
        """
        larger_neighbors = [v for v in neighbor_values.values() if v > local_value]
        smaller_neighbors = [v for v in neighbor_values.values() if v < local_value]

        # Sort and trim up to F adversarial extremes
        larger_neighbors.sort(reverse=True)
        smaller_neighbors.sort()

        trimmed_larger = larger_neighbors[self.f:] if len(larger_neighbors) >= self.f else []
        trimmed_smaller = smaller_neighbors[self.f:] if len(smaller_neighbors) >= self.f else []

        # Retained set includes local node value and non-eliminated neighbors
        valid_set = [local_value] + trimmed_larger + trimmed_smaller

        # Equal weight convex consensus update
        weight = self.alpha / len(valid_set)
        update_step = sum(weight * (val - local_value) for val in valid_set)
        return float(local_value + update_step)

    def step_mesh(
        self,
        frequencies: List[float],
        adjacency_matrix: np.ndarray,
        fdi_corruptions: Dict[int, float] = None,
    ) -> List[float]:
        """
        Run one round of consensus across the graph with optional FDI attack overrides.
        """
        fdi = fdi_corruptions or {}
        new_freqs = list(frequencies)

        for i in range(self.n):
            if i in fdi:
                new_freqs[i] = fdi[i]
                continue

            neighbors = {
                j: (fdi[j] if j in fdi else frequencies[j])
                for j in range(self.n)
                if adjacency_matrix[i, j] > 0 and i != j
            }

            new_freqs[i] = self.filter_and_update(
                node_id=i,
                local_value=frequencies[i],
                neighbor_values=neighbors,
            )

        return new_freqs
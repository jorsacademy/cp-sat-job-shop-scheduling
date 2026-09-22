"""Data definitions for the parallel machine scheduling project."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class SchedulingData:
    """Container for an identical parallel machine scheduling instance."""

    jobs: List[str]
    machines: List[str]
    processing_time: Dict[str, int]

    def validate(self) -> None:
        """Validate the consistency of the scheduling input data."""

        if not self.jobs:
            raise ValueError("At least one job is required.")
        if not self.machines:
            raise ValueError("At least one machine is required.")
        if len(set(self.jobs)) != len(self.jobs):
            raise ValueError("Job identifiers must be unique.")
        if len(set(self.machines)) != len(self.machines):
            raise ValueError("Machine identifiers must be unique.")
        if set(self.processing_time) != set(self.jobs):
            raise ValueError("Processing times must be defined for every job exactly once.")
        if any(value <= 0 for value in self.processing_time.values()):
            raise ValueError("All processing times must be strictly positive.")


def build_sample_data() -> SchedulingData:
    """Return the deterministic sample instance used in this project.

    The instance contains 12 independent jobs and 3 identical machines. The
    processing times were selected so that the total workload is 132 time units,
    which creates a theoretical workload lower bound of 44 time units.
    """

    data = SchedulingData(
        jobs=[f"J{i}" for i in range(1, 13)],
        machines=["M1", "M2", "M3"],
        processing_time={
            "J1": 14,
            "J2": 9,
            "J3": 18,
            "J4": 7,
            "J5": 13,
            "J6": 6,
            "J7": 11,
            "J8": 16,
            "J9": 8,
            "J10": 10,
            "J11": 15,
            "J12": 5,
        },
    )
    data.validate()
    return data

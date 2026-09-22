"""Visualization utilities for the optimized schedule."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import matplotlib.pyplot as plt

from data import SchedulingData

Schedule = Dict[str, List[str]]


def build_start_times(data: SchedulingData, schedule: Schedule) -> Dict[str, int]:
    """Calculate deterministic start times from the reporting order."""

    start_times: Dict[str, int] = {}

    for machine in data.machines:
        current_time = 0
        for job in schedule[machine]:
            start_times[job] = current_time
            current_time += data.processing_time[job]

    return start_times


def save_gantt_chart(
    data: SchedulingData,
    schedule: Schedule,
    output_path: str = "outputs/gantt_chart.png",
) -> Path:
    """Save a Gantt chart of the optimized schedule and return its path."""

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    start_times = build_start_times(data, schedule)

    fig, ax = plt.subplots(figsize=(11, 5.5))

    for machine_index, machine in enumerate(data.machines):
        for job in schedule[machine]:
            start = start_times[job]
            duration = data.processing_time[job]
            ax.barh(machine_index, duration, left=start)
            ax.text(
                start + duration / 2,
                machine_index,
                f"{job}\n({duration})",
                ha="center",
                va="center",
                fontsize=8,
            )

    ax.set_yticks(range(len(data.machines)), labels=data.machines)
    ax.set_xlabel("Time")
    ax.set_ylabel("Machine")
    ax.set_title("Optimized Parallel Machine Schedule")
    ax.grid(axis="x", alpha=0.25)
    ax.invert_yaxis()
    fig.tight_layout()
    fig.savefig(destination, dpi=160, bbox_inches="tight")
    plt.close(fig)

    return destination

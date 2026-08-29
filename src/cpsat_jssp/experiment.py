from __future__ import annotations

from .baseline import serial_schedule_generation
from .data import demo_instance
from .solution import lower_bound_makespan, machine_utilization
from .solver import solve_job_shop


def run_demo(
    *,
    time_limit: float = 10.0,
    workers: int = 1,
    seed: int = 2026,
    makespan_weight: int = 10,
    tardiness_weight: int = 1,
) -> dict[str, object]:
    instance = demo_instance()
    baseline = serial_schedule_generation(instance)
    result = solve_job_shop(
        instance,
        makespan_weight=makespan_weight,
        tardiness_weight=tardiness_weight,
        time_limit=time_limit,
        workers=workers,
        random_seed=seed,
    )
    by_machine = result.schedule.by_machine(instance.n_machines)
    return {
        "status": result.status,
        "objective": result.objective,
        "best_bound": result.best_bound,
        "absolute_gap": result.absolute_gap,
        "makespan": result.schedule.makespan,
        "weighted_tardiness": result.schedule.weighted_tardiness,
        "makespan_lower_bound": lower_bound_makespan(instance),
        "baseline_makespan": baseline.makespan,
        "baseline_weighted_tardiness": baseline.weighted_tardiness,
        "wall_time_seconds": result.wall_time,
        "conflicts": result.conflicts,
        "branches": result.branches,
        "machine_utilization": machine_utilization(instance, result.schedule),
        "machine_schedules": {
            str(machine): [
                {
                    "job": operation.job,
                    "operation": operation.operation,
                    "start": operation.start,
                    "end": operation.end,
                }
                for operation in operations
            ]
            for machine, operations in by_machine.items()
        },
    }

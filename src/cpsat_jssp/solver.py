from __future__ import annotations

from dataclasses import dataclass

from ortools.sat.python import cp_model

from .data import JobShopInstance
from .model import build_model
from .solution import Schedule, ScheduledOperation, validate_schedule


@dataclass(frozen=True)
class SolveResult:
    status: str
    objective: float
    best_bound: float
    wall_time: float
    conflicts: int
    branches: int
    schedule: Schedule

    @property
    def absolute_gap(self) -> float:
        return max(0.0, self.objective - self.best_bound)


def solve_job_shop(
    instance: JobShopInstance,
    *,
    makespan_weight: int = 1,
    tardiness_weight: int = 0,
    time_limit: float = 30.0,
    workers: int = 1,
    random_seed: int = 2026,
    log_search: bool = False,
) -> SolveResult:
    if time_limit <= 0:
        raise ValueError("time_limit must be positive")
    if workers <= 0:
        raise ValueError("workers must be positive")

    artifacts = build_model(instance, makespan_weight, tardiness_weight)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = float(time_limit)
    solver.parameters.num_search_workers = int(workers)
    solver.parameters.random_seed = int(random_seed)
    solver.parameters.log_search_progress = bool(log_search)
    status = solver.solve(artifacts.model)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        raise RuntimeError(
            f"CP-SAT did not produce a feasible schedule: {solver.status_name(status)}"
        )

    scheduled = []
    for (job_id, operation_id), variables in artifacts.tasks.items():
        specification = instance.jobs[job_id].operations[operation_id]
        start = int(solver.value(variables.start))
        end = int(solver.value(variables.end))
        scheduled.append(
            ScheduledOperation(
                job=job_id,
                operation=operation_id,
                machine=specification.machine,
                duration=specification.duration,
                start=start,
                end=end,
            )
        )

    completion = {}
    for job_id, job in enumerate(instance.jobs):
        completion[job_id] = int(
            solver.value(artifacts.tasks[job_id, len(job.operations) - 1].end)
        )
    weighted_tardiness = sum(
        job.weight * max(0, completion[job_id] - job.due)
        for job_id, job in enumerate(instance.jobs)
        if job.due is not None
    )
    schedule = Schedule(
        operations=tuple(sorted(scheduled, key=lambda op: (op.job, op.operation))),
        makespan=int(solver.value(artifacts.makespan)),
        weighted_tardiness=int(weighted_tardiness),
    )
    validate_schedule(instance, schedule)

    return SolveResult(
        status=solver.status_name(status),
        objective=float(solver.objective_value),
        best_bound=float(solver.best_objective_bound),
        wall_time=float(solver.wall_time),
        conflicts=int(solver.num_conflicts),
        branches=int(solver.num_branches),
        schedule=schedule,
    )

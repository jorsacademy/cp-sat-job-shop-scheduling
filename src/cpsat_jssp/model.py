from __future__ import annotations

from dataclasses import dataclass

from ortools.sat.python import cp_model

from .data import JobShopInstance

TaskKey = tuple[int, int]


@dataclass(frozen=True)
class TaskVars:
    start: cp_model.IntVar
    end: cp_model.IntVar
    interval: cp_model.IntervalVar


@dataclass(frozen=True)
class ModelArtifacts:
    model: cp_model.CpModel
    tasks: dict[TaskKey, TaskVars]
    makespan: cp_model.IntVar
    tardiness: dict[int, cp_model.IntVar]
    horizon: int


def build_model(
    instance: JobShopInstance,
    makespan_weight: int = 1,
    tardiness_weight: int = 0,
) -> ModelArtifacts:
    if makespan_weight < 0 or tardiness_weight < 0:
        raise ValueError("objective weights must be nonnegative")
    if makespan_weight == 0 and tardiness_weight == 0:
        raise ValueError("at least one objective weight must be positive")

    model = cp_model.CpModel()
    horizon = instance.horizon
    tasks: dict[TaskKey, TaskVars] = {}
    machine_intervals: dict[int, list[cp_model.IntervalVar]] = {
        machine: [] for machine in range(instance.n_machines)
    }

    for job_id, job in enumerate(instance.jobs):
        for operation_id, operation in enumerate(job.operations):
            suffix = f"j{job_id}_o{operation_id}"
            start = model.new_int_var(0, horizon, f"start_{suffix}")
            end = model.new_int_var(0, horizon, f"end_{suffix}")
            interval = model.new_interval_var(start, operation.duration, end, f"interval_{suffix}")
            tasks[job_id, operation_id] = TaskVars(start, end, interval)
            machine_intervals[operation.machine].append(interval)

        model.add(tasks[job_id, 0].start >= job.release)
        for operation_id in range(len(job.operations) - 1):
            model.add(
                tasks[job_id, operation_id + 1].start
                >= tasks[job_id, operation_id].end
            )

    for intervals in machine_intervals.values():
        model.add_no_overlap(intervals)

    completion_vars = [
        tasks[job_id, len(job.operations) - 1].end
        for job_id, job in enumerate(instance.jobs)
    ]
    makespan = model.new_int_var(0, horizon, "makespan")
    model.add_max_equality(makespan, completion_vars)

    tardiness: dict[int, cp_model.IntVar] = {}
    tardiness_terms = []
    for job_id, job in enumerate(instance.jobs):
        if job.due is None:
            continue
        variable = model.new_int_var(0, horizon, f"tardiness_j{job_id}")
        model.add(variable >= completion_vars[job_id] - job.due)
        tardiness[job_id] = variable
        tardiness_terms.append(job.weight * variable)

    objective = makespan_weight * makespan
    if tardiness_weight > 0:
        if not tardiness_terms:
            raise ValueError("tardiness_weight is positive but no job has a due date")
        objective += tardiness_weight * sum(tardiness_terms)
    model.minimize(objective)

    return ModelArtifacts(
        model=model,
        tasks=tasks,
        makespan=makespan,
        tardiness=tardiness,
        horizon=horizon,
    )

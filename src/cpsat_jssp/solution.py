from __future__ import annotations

from dataclasses import dataclass

from .data import JobShopInstance


@dataclass(frozen=True)
class ScheduledOperation:
    job: int
    operation: int
    machine: int
    duration: int
    start: int
    end: int


@dataclass(frozen=True)
class Schedule:
    operations: tuple[ScheduledOperation, ...]
    makespan: int
    weighted_tardiness: int

    def by_machine(self, n_machines: int) -> dict[int, tuple[ScheduledOperation, ...]]:
        result: dict[int, list[ScheduledOperation]] = {m: [] for m in range(n_machines)}
        for operation in self.operations:
            result[operation.machine].append(operation)
        return {
            machine: tuple(sorted(items, key=lambda item: (item.start, item.end, item.job)))
            for machine, items in result.items()
        }


def validate_schedule(instance: JobShopInstance, schedule: Schedule) -> None:
    expected = {
        (job_id, operation_id)
        for job_id, job in enumerate(instance.jobs)
        for operation_id in range(len(job.operations))
    }
    actual = {(op.job, op.operation) for op in schedule.operations}
    if actual != expected or len(actual) != len(schedule.operations):
        raise ValueError("schedule does not contain every operation exactly once")

    lookup = {(op.job, op.operation): op for op in schedule.operations}
    for job_id, job in enumerate(instance.jobs):
        first = lookup[job_id, 0]
        if first.start < job.release:
            raise ValueError("job starts before its release time")
        for operation_id, specification in enumerate(job.operations):
            scheduled = lookup[job_id, operation_id]
            if scheduled.machine != specification.machine:
                raise ValueError("operation assigned to the wrong machine")
            if scheduled.duration != specification.duration:
                raise ValueError("operation duration does not match the instance")
            if scheduled.end - scheduled.start != scheduled.duration:
                raise ValueError("operation timing is inconsistent")
            if scheduled.start < 0:
                raise ValueError("operation start must be nonnegative")
            if operation_id > 0:
                predecessor = lookup[job_id, operation_id - 1]
                if scheduled.start < predecessor.end:
                    raise ValueError("job precedence is violated")

    for operations in schedule.by_machine(instance.n_machines).values():
        for previous, current in zip(operations, operations[1:]):
            if current.start < previous.end:
                raise ValueError("machine no-overlap is violated")

    computed_makespan = max(operation.end for operation in schedule.operations)
    if schedule.makespan != computed_makespan:
        raise ValueError("reported makespan is inconsistent")

    completion = {
        job_id: lookup[job_id, len(job.operations) - 1].end
        for job_id, job in enumerate(instance.jobs)
    }
    weighted_tardiness = sum(
        job.weight * max(0, completion[job_id] - job.due)
        for job_id, job in enumerate(instance.jobs)
        if job.due is not None
    )
    if schedule.weighted_tardiness != weighted_tardiness:
        raise ValueError("reported weighted tardiness is inconsistent")


def machine_utilization(instance: JobShopInstance, schedule: Schedule) -> dict[int, float]:
    if schedule.makespan <= 0:
        return {machine: 0.0 for machine in range(instance.n_machines)}
    busy = {machine: 0 for machine in range(instance.n_machines)}
    for operation in schedule.operations:
        busy[operation.machine] += operation.duration
    return {
        machine: busy[machine] / schedule.makespan
        for machine in range(instance.n_machines)
    }


def lower_bound_makespan(instance: JobShopInstance) -> int:
    job_bound = max(
        sum(op.duration for op in job.operations) + job.release
        for job in instance.jobs
    )
    machine_loads = [0] * instance.n_machines
    for job in instance.jobs:
        for operation in job.operations:
            machine_loads[operation.machine] += operation.duration
    return max(job_bound, max(machine_loads))

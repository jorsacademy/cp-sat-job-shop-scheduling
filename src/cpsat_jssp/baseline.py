from __future__ import annotations

from .data import JobShopInstance
from .solution import Schedule, ScheduledOperation, validate_schedule


def serial_schedule_generation(instance: JobShopInstance) -> Schedule:
    """Construct a deterministic feasible schedule by job order and earliest machine availability."""
    machine_available = [0] * instance.n_machines
    operations: list[ScheduledOperation] = []
    completion: dict[int, int] = {}

    for job_id, job in enumerate(instance.jobs):
        previous_end = job.release
        for operation_id, operation in enumerate(job.operations):
            start = max(previous_end, machine_available[operation.machine])
            end = start + operation.duration
            operations.append(
                ScheduledOperation(
                    job=job_id,
                    operation=operation_id,
                    machine=operation.machine,
                    duration=operation.duration,
                    start=start,
                    end=end,
                )
            )
            previous_end = end
            machine_available[operation.machine] = end
        completion[job_id] = previous_end

    makespan = max(completion.values())
    weighted_tardiness = sum(
        job.weight * max(0, completion[job_id] - job.due)
        for job_id, job in enumerate(instance.jobs)
        if job.due is not None
    )
    schedule = Schedule(tuple(operations), makespan, weighted_tardiness)
    validate_schedule(instance, schedule)
    return schedule

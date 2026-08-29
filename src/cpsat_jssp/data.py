from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Operation:
    machine: int
    duration: int

    def __post_init__(self) -> None:
        if self.machine < 0:
            raise ValueError("machine must be nonnegative")
        if self.duration <= 0:
            raise ValueError("duration must be positive")


@dataclass(frozen=True)
class Job:
    operations: tuple[Operation, ...]
    release: int = 0
    due: int | None = None
    weight: int = 1

    def __post_init__(self) -> None:
        if not self.operations:
            raise ValueError("each job must contain at least one operation")
        if self.release < 0:
            raise ValueError("release must be nonnegative")
        if self.due is not None and self.due < 0:
            raise ValueError("due must be nonnegative when provided")
        if self.weight <= 0:
            raise ValueError("weight must be positive")


@dataclass(frozen=True)
class JobShopInstance:
    jobs: tuple[Job, ...]
    n_machines: int

    def __post_init__(self) -> None:
        if not self.jobs:
            raise ValueError("instance must contain at least one job")
        if self.n_machines <= 0:
            raise ValueError("n_machines must be positive")
        for job in self.jobs:
            for operation in job.operations:
                if operation.machine >= self.n_machines:
                    raise ValueError("operation references a machine outside the instance")

    @property
    def horizon(self) -> int:
        return max(job.release for job in self.jobs) + sum(
            operation.duration for job in self.jobs for operation in job.operations
        )

    @property
    def n_operations(self) -> int:
        return sum(len(job.operations) for job in self.jobs)


def classic_three_job_instance() -> JobShopInstance:
    """Return the standard 3-job example whose optimal makespan is 11."""
    return JobShopInstance(
        jobs=(
            Job((Operation(0, 3), Operation(1, 2), Operation(2, 2))),
            Job((Operation(0, 2), Operation(2, 1), Operation(1, 4))),
            Job((Operation(1, 4), Operation(2, 3))),
        ),
        n_machines=3,
    )


def demo_instance() -> JobShopInstance:
    """Return a synthetic due-date instance for the CLI demonstration."""
    return JobShopInstance(
        jobs=(
            Job((Operation(0, 4), Operation(1, 3), Operation(3, 2)), release=0, due=15, weight=2),
            Job((Operation(1, 2), Operation(2, 5), Operation(3, 3)), release=0, due=16, weight=1),
            Job((Operation(2, 3), Operation(0, 5), Operation(1, 2)), release=2, due=18, weight=3),
            Job((Operation(3, 4), Operation(1, 3), Operation(2, 2)), release=1, due=17, weight=2),
            Job((Operation(0, 2), Operation(2, 4), Operation(3, 5)), release=3, due=21, weight=1),
            Job((Operation(1, 3), Operation(3, 2), Operation(0, 4)), release=0, due=19, weight=2),
        ),
        n_machines=4,
    )

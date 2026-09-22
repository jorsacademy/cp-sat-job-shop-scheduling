"""MILP model, solution extraction, and validation utilities."""

from __future__ import annotations

import math
from typing import Dict, List, Tuple

import pulp

from data import SchedulingData

AssignmentVariables = Dict[Tuple[str, str], pulp.LpVariable]
Schedule = Dict[str, List[str]]


def build_model(
    data: SchedulingData,
) -> Tuple[pulp.LpProblem, AssignmentVariables, pulp.LpVariable]:
    """Build the identical parallel machine scheduling MILP model."""

    model = pulp.LpProblem("Parallel_Machine_Scheduling", pulp.LpMinimize)

    assignment = pulp.LpVariable.dicts(
        "assign",
        [(job, machine) for job in data.jobs for machine in data.machines],
        cat=pulp.LpBinary,
    )
    makespan = pulp.LpVariable("makespan", lowBound=0, cat=pulp.LpContinuous)

    model += makespan, "Minimize_Makespan"

    for job in data.jobs:
        model += (
            pulp.lpSum(assignment[(job, machine)] for machine in data.machines) == 1,
            f"Assign_{job}_Exactly_Once",
        )

    for machine in data.machines:
        model += (
            pulp.lpSum(
                data.processing_time[job] * assignment[(job, machine)]
                for job in data.jobs
            )
            <= makespan,
            f"Makespan_Bound_{machine}",
        )

    return model, assignment, makespan


def solve_model(model: pulp.LpProblem, solver_messages: bool = False) -> str:
    """Solve the MILP with HiGHS and return the solver status."""

    solver = pulp.HiGHS(msg=solver_messages)
    model.solve(solver)
    status = pulp.LpStatus[model.status]

    if status != "Optimal":
        raise RuntimeError(f"Solver did not find an optimal solution. Status: {status}")

    return status


def extract_schedule(data: SchedulingData, assignment: AssignmentVariables) -> Schedule:
    """Extract the optimized job-to-machine assignment.

    The jobs are sorted by decreasing processing time for deterministic reporting.
    Since this model has no release dates, setup times, or precedence constraints,
    the within-machine order does not affect the makespan.
    """

    schedule: Schedule = {machine: [] for machine in data.machines}

    for machine in data.machines:
        assigned_jobs = [
            job
            for job in data.jobs
            if (value := pulp.value(assignment[(job, machine)])) is not None and value > 0.5
        ]
        schedule[machine] = sorted(
            assigned_jobs,
            key=lambda job: (-data.processing_time[job], job),
        )

    return schedule


def calculate_machine_loads(data: SchedulingData, schedule: Schedule) -> Dict[str, int]:
    """Calculate the total assigned processing time on each machine."""

    return {
        machine: sum(data.processing_time[job] for job in jobs)
        for machine, jobs in schedule.items()
    }


def calculate_lower_bound(data: SchedulingData) -> int:
    """Return a standard lower bound for identical parallel machine makespan.

    The bound is the maximum of the average workload bound and the longest-job
    bound. Any feasible schedule must have a makespan at least this large.
    """

    average_load_bound = math.ceil(
        sum(data.processing_time.values()) / len(data.machines)
    )
    longest_job_bound = max(data.processing_time.values())
    return max(average_load_bound, longest_job_bound)


def validate_solution(
    data: SchedulingData,
    schedule: Schedule,
    optimized_makespan: float,
) -> None:
    """Perform independent consistency checks on the optimized schedule."""

    assigned_jobs = [job for jobs in schedule.values() for job in jobs]

    if len(assigned_jobs) != len(data.jobs):
        raise AssertionError("The schedule does not contain the expected number of jobs.")
    if set(assigned_jobs) != set(data.jobs):
        raise AssertionError("The schedule contains missing or unknown jobs.")
    if len(assigned_jobs) != len(set(assigned_jobs)):
        raise AssertionError("At least one job was assigned more than once.")

    loads = calculate_machine_loads(data, schedule)
    reconstructed_makespan = max(loads.values())

    if abs(reconstructed_makespan - optimized_makespan) > 1e-6:
        raise AssertionError(
            "The solver makespan does not match the makespan reconstructed from the schedule."
        )

    lower_bound = calculate_lower_bound(data)
    if optimized_makespan + 1e-6 < lower_bound:
        raise AssertionError("The reported makespan is below a valid theoretical lower bound.")

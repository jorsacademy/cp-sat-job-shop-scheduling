"""Entry point for the parallel machine scheduling MILP project."""

from __future__ import annotations

import pulp

from data import SchedulingData, build_sample_data
from scheduler import (
    Schedule,
    build_model,
    calculate_lower_bound,
    calculate_machine_loads,
    extract_schedule,
    solve_model,
    validate_solution,
)
from visualization import save_gantt_chart


def print_input_data(data: SchedulingData) -> None:
    """Print the scheduling instance in a compact table."""

    print("Input Data")
    print("-" * 28)
    print(f"{'Job':<8}{'Processing Time':>18}")
    print("-" * 28)
    for job in data.jobs:
        print(f"{job:<8}{data.processing_time[job]:>18}")
    print()


def print_solution_table(
    data: SchedulingData,
    schedule: Schedule,
    optimized_makespan: float,
) -> None:
    """Print the optimized machine schedule as a result table."""

    loads = calculate_machine_loads(data, schedule)
    lower_bound = calculate_lower_bound(data)

    print("Optimization Results")
    print("=" * 72)
    print(f"Theoretical lower bound : {lower_bound:.0f}")
    print(f"Optimal makespan        : {optimized_makespan:.0f}")
    print(f"Optimality gap to bound : {optimized_makespan - lower_bound:.0f}\n")

    print(f"{'Machine':<10}{'Jobs':<45}{'Load':>8}")
    print("-" * 72)
    for machine in data.machines:
        jobs_text = ", ".join(schedule[machine])
        print(f"{machine:<10}{jobs_text:<45}{loads[machine]:>8}")
    print()

    print("Detailed Timeline")
    print("-" * 72)
    for machine in data.machines:
        current_time = 0
        for job in schedule[machine]:
            duration = data.processing_time[job]
            completion_time = current_time + duration
            print(
                f"{machine} | {job:<4} | start={current_time:>3} | "
                f"duration={duration:>3} | completion={completion_time:>3}"
            )
            current_time = completion_time
        print()


def main() -> None:
    """Run data loading, optimization, validation, reporting, and visualization."""

    data = build_sample_data()
    print_input_data(data)

    model, assignment, makespan = build_model(data)
    status = solve_model(model)
    schedule = extract_schedule(data, assignment)

    optimized_makespan = pulp.value(makespan)
    if optimized_makespan is None:
        raise RuntimeError("The solver returned no makespan value.")

    validate_solution(data, schedule, optimized_makespan)

    print(f"Solver status: {status}")
    print("Independent solution validation: PASSED\n")
    print_solution_table(data, schedule, optimized_makespan)

    chart_path = save_gantt_chart(data, schedule)
    print(f"Gantt chart saved to: {chart_path}")


if __name__ == "__main__":
    main()

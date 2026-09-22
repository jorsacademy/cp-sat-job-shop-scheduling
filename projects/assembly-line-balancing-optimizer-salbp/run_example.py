from pathlib import Path

from alb_optimizer import (
    largest_candidate_rule,
    ranked_positional_weight,
    solve_salbp1,
    validate_solution,
)
from alb_optimizer.io import load_precedence, load_tasks

ROOT = Path(__file__).resolve().parent
CYCLE_TIME = 15


def print_result(name, result):
    print(f"\n{name}")
    print("-" * len(name))
    print(f"Stations: {result.station_count}")
    print(f"Theoretical minimum: {result.theoretical_minimum}")
    print(f"Line efficiency: {result.line_efficiency:.2%}")
    print(f"Balance delay: {result.balance_delay:.2%}")
    for index, (tasks, load) in enumerate(
        zip(result.stations, result.station_loads), start=1
    ):
        print(
            f"Station {index}: {tasks} | load={load}/{result.cycle_time}"
        )


def main():
    task_times = load_tasks(ROOT / "data" / "tasks.csv")
    precedence = load_precedence(ROOT / "data" / "precedence.csv")

    results = {
        "Exact SALBP-1": solve_salbp1(task_times, precedence, CYCLE_TIME),
        "Largest Candidate Rule": largest_candidate_rule(
            task_times, precedence, CYCLE_TIME
        ),
        "Ranked Positional Weight": ranked_positional_weight(
            task_times, precedence, CYCLE_TIME
        ),
    }

    for name, result in results.items():
        validate_solution(result, precedence)
        print_result(name, result)


if __name__ == "__main__":
    main()

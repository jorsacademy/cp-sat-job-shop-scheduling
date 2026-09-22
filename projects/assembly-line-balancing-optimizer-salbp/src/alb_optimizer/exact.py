from __future__ import annotations

from math import ceil
from typing import List, Sequence

from .core import BalanceResult, Edge, TaskTimes, validate_instance


def solve_salbp1(
    task_times: TaskTimes,
    precedence: Sequence[Edge],
    cycle_time: int,
    time_limit: int = 30,
) -> BalanceResult:
    """Solve SALBP-1 with OR-Tools CP-SAT."""
    validate_instance(task_times, precedence, cycle_time)
    try:
        from ortools.sat.python import cp_model
    except ImportError as exc:
        raise RuntimeError(
            "OR-Tools is required for the exact solver. Install it with: pip install ortools"
        ) from exc

    tasks = list(task_times)
    total_work = sum(task_times.values())
    lower_bound = ceil(total_work / cycle_time)
    max_stations = len(tasks)

    model = cp_model.CpModel()
    x = {
        (task, station): model.NewBoolVar(f"x_{task}_{station}")
        for task in tasks
        for station in range(max_stations)
    }
    y = {
        station: model.NewBoolVar(f"y_{station}")
        for station in range(max_stations)
    }

    for task in tasks:
        model.Add(sum(x[task, station] for station in range(max_stations)) == 1)

    for station in range(max_stations):
        model.Add(
            sum(task_times[task] * x[task, station] for task in tasks)
            <= cycle_time * y[station]
        )
        for task in tasks:
            model.Add(x[task, station] <= y[station])

    for station in range(max_stations - 1):
        model.Add(y[station + 1] <= y[station])

    for predecessor, successor in precedence:
        model.Add(
            sum(station * x[predecessor, station] for station in range(max_stations))
            <= sum(station * x[successor, station] for station in range(max_stations))
        )

    model.Add(sum(y[station] for station in range(max_stations)) >= lower_bound)
    model.Minimize(sum(y[station] for station in range(max_stations)))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = float(time_limit)
    solver.parameters.num_search_workers = 8
    status = solver.Solve(model)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        raise RuntimeError("No feasible SALBP-1 solution found.")

    used_stations = [
        station for station in range(max_stations) if solver.Value(y[station]) == 1
    ]
    stations: List[List[str]] = []
    for station in used_stations:
        stations.append(
            [task for task in tasks if solver.Value(x[task, station]) == 1]
        )

    result = BalanceResult(
        stations=stations,
        cycle_time=cycle_time,
        task_times=task_times,
    )

    if status != cp_model.OPTIMAL and result.station_count != lower_bound:
        raise RuntimeError("Time limit reached before optimality was proven.")

    return result

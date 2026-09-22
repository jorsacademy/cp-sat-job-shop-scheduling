import pytest

from rcpsp_solver import RCPSPSolver


def base_instance():
    activities = ["start", "A", "B", "finish"]
    durations = {"start": 0, "A": 2, "B": 2, "finish": 0}
    predecessors = {
        "start": [],
        "A": ["start"],
        "B": ["start"],
        "finish": ["A", "B"],
    }
    requirements = {
        ("A", "worker"): 1,
        ("B", "worker"): 1,
    }
    return activities, durations, predecessors, requirements


def test_rejects_cyclic_precedence_graph():
    activities, durations, predecessors, requirements = base_instance()
    predecessors["start"] = ["finish"]

    with pytest.raises(ValueError, match="directed acyclic graph"):
        RCPSPSolver(
            activities, durations, predecessors, requirements, {"worker": 1}
        )


def test_rejects_requirement_above_capacity():
    activities, durations, predecessors, requirements = base_instance()
    requirements[("A", "worker")] = 2

    with pytest.raises(ValueError, match="capacity"):
        RCPSPSolver(
            activities, durations, predecessors, requirements, {"worker": 1}
        )


def test_time_windows_respect_precedence():
    activities, durations, predecessors, requirements = base_instance()
    solver = RCPSPSolver(
        activities, durations, predecessors, requirements, {"worker": 1}
    )

    assert solver.est["A"] == 0
    assert solver.est["finish"] == 2
    assert solver.lst["start"] <= solver.lst["A"]
    assert solver.est["finish"] <= solver.lst["finish"]


def test_solver_serializes_competing_activities():
    activities, durations, predecessors, requirements = base_instance()
    solver = RCPSPSolver(
        activities, durations, predecessors, requirements, {"worker": 1}
    )
    result = solver.solve(msg=False)

    assert result.status == "Optimal"
    assert result.makespan == 4
    a_start = result.start_times["A"]
    b_start = result.start_times["B"]
    assert abs(a_start - b_start) >= 2

    usage = solver.resource_usage()["worker"]
    assert max(usage) <= 1

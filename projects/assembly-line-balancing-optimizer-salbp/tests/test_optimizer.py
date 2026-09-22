from pathlib import Path

from alb_optimizer import (
    largest_candidate_rule,
    ranked_positional_weight,
    solve_salbp1,
    validate_solution,
)
from alb_optimizer.io import load_precedence, load_tasks

ROOT = Path(__file__).resolve().parents[1]
TASKS = load_tasks(ROOT / "data" / "tasks.csv")
PRECEDENCE = load_precedence(ROOT / "data" / "precedence.csv")
CYCLE_TIME = 15


def test_heuristics_are_feasible():
    for solver in (largest_candidate_rule, ranked_positional_weight):
        result = solver(TASKS, PRECEDENCE, CYCLE_TIME)
        validate_solution(result, PRECEDENCE)
        assert result.station_count >= result.theoretical_minimum


def test_exact_solver_reaches_proven_lower_bound():
    result = solve_salbp1(TASKS, PRECEDENCE, CYCLE_TIME)
    validate_solution(result, PRECEDENCE)
    assert result.theoretical_minimum == 7
    assert result.station_count == 7

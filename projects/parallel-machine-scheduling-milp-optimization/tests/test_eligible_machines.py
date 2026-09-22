from itertools import product
import pytest
from eligible_machines import EligibleInstance, sample_instance, greedy_schedule, solve_milp, validate_assignment


def enumerate_optimum(instance):
    choices = [[m for m in instance.machines if (j, m) in instance.durations] for j in instance.jobs]
    return min(validate_assignment(instance, dict(zip(instance.jobs, ms))) for ms in product(*choices))


@pytest.mark.parametrize('seed', range(5))
def test_milp_matches_exhaustive_search(seed):
    data = sample_instance(seed, jobs=5, machines=3)
    _, optimum = solve_milp(data)
    assignment, greedy = greedy_schedule(data)
    assert optimum == pytest.approx(enumerate_optimum(data))
    assert greedy >= optimum - 1e-6
    assert validate_assignment(data, assignment) == greedy


def test_eligibility_trap_shows_greedy_gap():
    data = EligibleInstance(('A', 'B'), ('X', 'Y'), {('A','X'):1, ('A','Y'):2, ('B','X'):3})
    assert greedy_schedule(data)[1] == 4
    assert solve_milp(data)[1] == 3


@pytest.mark.parametrize('data', [
    EligibleInstance((), ('X',), {}),
    EligibleInstance(('A','A'), ('X',), {('A','X'):1}),
    EligibleInstance(('A',), ('X',), {('B','X'):1}),
    EligibleInstance(('A',), ('X',), {('A','X'):float('nan')}),
    EligibleInstance(('A',), ('X',), {}),
])
def test_invalid_input(data):
    with pytest.raises(ValueError):
        solve_milp(data)


def test_missing_or_ineligible_assignments_rejected():
    data = EligibleInstance(('A',), ('X','Y'), {('A','X'):1})
    for assignment in ({}, {'A':'Y'}, {'A':'X','B':'X'}):
        with pytest.raises(ValueError):
            validate_assignment(data, assignment)


def test_original_identical_machine_example():
    from data import build_sample_data
    from scheduler import build_model, solve_model, extract_schedule, validate_solution
    data = build_sample_data()
    model, variables, makespan = build_model(data)
    solve_model(model)
    validate_solution(data, extract_schedule(data, variables), makespan.value())
    assert makespan.value() == 44

import pytest

from cpsat_jssp.data import Job, JobShopInstance, Operation, classic_three_job_instance, demo_instance
from cpsat_jssp.model import build_model
from cpsat_jssp.solution import validate_schedule
from cpsat_jssp.solver import solve_job_shop


def test_objective_validation() -> None:
    instance = classic_three_job_instance()
    with pytest.raises(ValueError):
        build_model(instance, 0, 0)
    with pytest.raises(ValueError):
        build_model(instance, -1, 0)


def test_classic_instance_optimum_is_11() -> None:
    result = solve_job_shop(classic_three_job_instance(), time_limit=10.0, workers=1)
    assert result.status == "OPTIMAL"
    assert result.schedule.makespan == 11
    assert result.objective == pytest.approx(11.0)
    assert result.best_bound == pytest.approx(11.0)
    validate_schedule(classic_three_job_instance(), result.schedule)


def test_release_dates_and_due_dates_are_respected() -> None:
    instance = demo_instance()
    result = solve_job_shop(
        instance,
        makespan_weight=10,
        tardiness_weight=1,
        time_limit=10.0,
        workers=1,
    )
    validate_schedule(instance, result.schedule)
    first_starts = {
        op.job: op.start for op in result.schedule.operations if op.operation == 0
    }
    for job_id, job in enumerate(instance.jobs):
        assert first_starts[job_id] >= job.release


def test_positive_tardiness_weight_requires_due_dates() -> None:
    instance = JobShopInstance(
        jobs=(Job((Operation(0, 2),)), Job((Operation(0, 1),))),
        n_machines=1,
    )
    with pytest.raises(ValueError):
        build_model(instance, makespan_weight=1, tardiness_weight=1)

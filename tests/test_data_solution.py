import pytest

from cpsat_jssp.baseline import serial_schedule_generation
from cpsat_jssp.data import Job, JobShopInstance, Operation, classic_three_job_instance
from cpsat_jssp.solution import lower_bound_makespan, validate_schedule


def test_data_validation() -> None:
    with pytest.raises(ValueError):
        Operation(machine=-1, duration=1)
    with pytest.raises(ValueError):
        Operation(machine=0, duration=0)
    with pytest.raises(ValueError):
        Job(operations=())
    with pytest.raises(ValueError):
        JobShopInstance(jobs=(Job((Operation(2, 1),)),), n_machines=2)


def test_serial_baseline_is_feasible() -> None:
    instance = classic_three_job_instance()
    schedule = serial_schedule_generation(instance)
    validate_schedule(instance, schedule)
    assert schedule.makespan >= lower_bound_makespan(instance)


def test_classic_lower_bound_is_not_above_optimum() -> None:
    assert lower_bound_makespan(classic_three_job_instance()) <= 11

import json
import subprocess
import sys

from cpsat_jssp.baseline import serial_schedule_generation
from cpsat_jssp.data import demo_instance
from cpsat_jssp.solution import machine_utilization
from cpsat_jssp.solver import solve_job_shop


def test_cp_sat_improves_weighted_demo_objective_over_serial_baseline() -> None:
    instance = demo_instance()
    baseline = serial_schedule_generation(instance)
    result = solve_job_shop(
        instance,
        makespan_weight=10,
        tardiness_weight=1,
        time_limit=10.0,
        workers=1,
    )
    baseline_objective = 10 * baseline.makespan + baseline.weighted_tardiness
    assert result.objective <= baseline_objective


def test_machine_utilization_is_bounded() -> None:
    instance = demo_instance()
    result = solve_job_shop(instance, time_limit=10.0, workers=1)
    utilization = machine_utilization(instance, result.schedule)
    assert utilization
    assert all(0.0 <= value <= 1.0 for value in utilization.values())


def test_cli_outputs_valid_json() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "cpsat_jssp",
            "--time-limit",
            "5",
            "--workers",
            "1",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)
    assert payload["status"] in {"OPTIMAL", "FEASIBLE"}
    assert payload["makespan"] > 0
    assert payload["objective"] >= payload["best_bound"] - 1e-6

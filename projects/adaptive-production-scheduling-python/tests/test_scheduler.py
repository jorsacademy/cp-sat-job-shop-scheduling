import pytest

from adaptive_scheduler import AdaptiveProductionScheduler, Machine, Product


def scheduler(seed=1):
    products = [
        Product("A", margin=100, priority=1),
        Product("B", margin=50, priority=2),
    ]
    machines = [
        Machine("M1", 10, "A", maintenance_probability=0),
        Machine("M2", 8, "B", maintenance_probability=0),
    ]
    return AdaptiveProductionScheduler(products, machines, ["S1", "S2"], seed=seed)


def test_exponential_smoothing_forecast():
    s = scheduler()
    assert s.exponential_smoothing_forecast([10, 20, 30], alpha=0.5) == pytest.approx(22.5)
    assert s.exponential_smoothing_forecast([]) == 0


def test_machine_current_capacity_is_preserved():
    m = Machine("M", 10, "A", current_capacity=4)
    assert m.current_capacity == 4


def test_priority_prefers_high_margin_high_priority_product():
    scores = scheduler().calculate_priority_scores({"A": 50, "B": 50})
    assert scores["A"] > scores["B"]


def test_allocation_is_integer_and_non_negative():
    plan, unmet, utilization = scheduler().optimize_production_allocation({"A": 13.4, "B": 7})
    assert all(isinstance(qty, int) for shift in plan.values() for qty in shift.values())
    assert all(value >= 0 for value in unmet.values())
    assert all(0 <= value <= 100 for shift in utilization.values() for value in shift.values())


def test_available_machines_argument_is_honored():
    s = scheduler()
    custom = {
        "M1": Machine("M1", 1, "A", maintenance_probability=0),
        "M2": Machine("M2", 1, "B", maintenance_probability=0),
    }
    plan, _, _ = s.optimize_production_allocation({"A": 100, "B": 100}, custom)
    assert sum(shift["A"] for shift in plan.values()) <= 3
    assert sum(shift["B"] for shift in plan.values()) <= 3


def test_generate_schedule_kpis_are_consistent():
    result = scheduler(seed=4).generate_schedule({"A": 5, "B": 4})
    assert result["kpis"]["total_demand"] == 9
    assert result["kpis"]["total_production"] <= 9
    assert 0 <= result["kpis"]["service_level_pct"] <= 100


def test_unknown_product_is_rejected():
    with pytest.raises(ValueError, match="unknown products"):
        scheduler().generate_schedule({"UNKNOWN": 10})

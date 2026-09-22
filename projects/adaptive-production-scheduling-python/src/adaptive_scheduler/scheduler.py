from __future__ import annotations

import logging
import random
from datetime import datetime, timezone
from statistics import fmean
from typing import Iterable, Mapping

from .models import Machine, Product

logger = logging.getLogger(__name__)


class AdaptiveProductionScheduler:
    """Priority-based adaptive production scheduling heuristic.

    The scheduler combines exponential smoothing, stochastic machine availability,
    weighted product priorities, capacity-aware allocation, and KPI calculation.
    It is a heuristic simulator rather than a mathematical-programming solver.
    """

    def __init__(
        self,
        products: Iterable[Product],
        machines: Iterable[Machine],
        shifts: Iterable[str],
        *,
        seed: int | None = None,
        demand_smoothing_alpha: float = 0.3,
        efficiency_threshold: float = 0.85,
    ) -> None:
        self.products = {p.name: p for p in products}
        self.machines = {m.name: m for m in machines}
        self.shifts = list(shifts)
        if not self.products:
            raise ValueError("at least one product is required")
        if not self.machines:
            raise ValueError("at least one machine is required")
        if not self.shifts:
            raise ValueError("at least one shift is required")
        if not 0 < demand_smoothing_alpha <= 1:
            raise ValueError("demand_smoothing_alpha must be in (0, 1]")

        self.demand_smoothing_alpha = demand_smoothing_alpha
        self.efficiency_threshold = efficiency_threshold
        self.rng = random.Random(seed)
        self.production_history: list[dict] = []
        self.kpi_metrics: dict[str, float] = {}

    def exponential_smoothing_forecast(
        self, historical_demand: Iterable[float], alpha: float | None = None
    ) -> float:
        values = list(historical_demand)
        if not values:
            return 0.0
        smoothing = self.demand_smoothing_alpha if alpha is None else alpha
        if not 0 < smoothing <= 1:
            raise ValueError("alpha must be in (0, 1]")

        forecast = float(values[0])
        for demand in values[1:]:
            forecast = smoothing * float(demand) + (1 - smoothing) * forecast
        return forecast

    def simulate_machine_disruptions(
        self, machines: Mapping[str, Machine] | None = None
    ) -> dict[str, Machine]:
        source = machines or self.machines
        disrupted: dict[str, Machine] = {}
        for name, machine in source.items():
            state = machine.clone()
            if self.rng.random() < machine.maintenance_probability:
                state.current_capacity = 0
                state.efficiency = 0.0
                logger.warning("Machine %s is down for maintenance", name)
            else:
                factor = self.rng.uniform(0.8, 1.2)
                state.current_capacity = max(0, int(round(machine.base_capacity * factor)))
                state.efficiency = factor
                if factor < self.efficiency_threshold:
                    logger.warning(
                        "Machine %s below efficiency threshold: %.2f", name, factor
                    )
            disrupted[name] = state
        return disrupted

    def calculate_priority_scores(
        self, demand_forecast: Mapping[str, float]
    ) -> dict[str, float]:
        max_margin = max(p.margin for p in self.products.values()) or 1.0
        max_priority = max(p.priority for p in self.products.values()) or 1
        scores: dict[str, float] = {}

        for product_name, raw_demand in demand_forecast.items():
            if product_name not in self.products:
                continue
            demand = max(0.0, float(raw_demand))
            product = self.products[product_name]
            margin_score = product.margin / max_margin
            demand_urgency = min(demand / 100.0, 1.0)
            priority_score = 1.0 - ((product.priority - 1) / max_priority)
            scores[product_name] = (
                0.4 * margin_score + 0.3 * demand_urgency + 0.3 * priority_score
            )
        return scores

    def optimize_production_allocation(
        self,
        demand_forecast: Mapping[str, float],
        available_machines: Mapping[str, Machine] | None = None,
    ) -> tuple[dict[str, dict[str, int]], dict[str, float], dict[str, dict[str, float]]]:
        demand = {name: max(0.0, float(value)) for name, value in demand_forecast.items()}
        unknown = set(demand) - set(self.products)
        if unknown:
            raise ValueError(f"unknown products in demand forecast: {sorted(unknown)}")

        production_plan = {
            shift: {product: 0 for product in self.products} for shift in self.shifts
        }
        unmet_demand = demand.copy()
        utilization = {
            shift: {machine: 0.0 for machine in self.machines} for shift in self.shifts
        }

        scores = self.calculate_priority_scores(demand)
        sorted_products = sorted(scores, key=scores.get, reverse=True)
        machine_source = available_machines or self.machines

        for shift_index, shift in enumerate(self.shifts):
            current = self.simulate_machine_disruptions(machine_source)
            learning_factor = min(1.10, 1.0 + 0.02 * shift_index)

            for machine in current.values():
                if machine.current_capacity:
                    machine.current_capacity = int(round(machine.current_capacity * learning_factor))

            remaining_capacity = {
                name: int(machine.current_capacity or 0) for name, machine in current.items()
            }

            for product_name in sorted_products:
                remaining_demand = unmet_demand[product_name]
                if remaining_demand <= 0:
                    continue

                for machine_name, machine in current.items():
                    if machine.product_type != product_name:
                        continue
                    capacity = remaining_capacity[machine_name]
                    if capacity <= 0:
                        continue

                    qty = min(int(remaining_demand), capacity)
                    if qty <= 0 and remaining_demand > 0 and capacity > 0:
                        qty = 1
                    qty = min(qty, capacity)
                    if qty <= 0:
                        continue

                    production_plan[shift][product_name] += qty
                    unmet_demand[product_name] = max(0.0, unmet_demand[product_name] - qty)
                    remaining_capacity[machine_name] -= qty

                    denominator = max(int(machine.current_capacity or 0), 1)
                    utilization[shift][machine_name] = round(
                        100.0 * (denominator - remaining_capacity[machine_name]) / denominator,
                        2,
                    )
                    if unmet_demand[product_name] <= 0:
                        break

        return production_plan, unmet_demand, utilization

    def calculate_kpis(
        self,
        production_plan: Mapping[str, Mapping[str, int]],
        unmet_demand: Mapping[str, float],
        machine_utilization: Mapping[str, Mapping[str, float]],
        demand_forecast: Mapping[str, float],
    ) -> dict[str, float]:
        total_production = float(
            sum(sum(shift_plan.values()) for shift_plan in production_plan.values())
        )
        total_demand = float(sum(demand_forecast.values()))
        total_unmet = float(sum(unmet_demand.values()))
        service_level = (
            (total_demand - total_unmet) / total_demand * 100.0 if total_demand else 0.0
        )

        utilization_values = [
            value
            for shift_values in machine_utilization.values()
            for value in shift_values.values()
        ]
        avg_utilization = fmean(utilization_values) if utilization_values else 0.0

        total_revenue = 0.0
        for shift_plan in production_plan.values():
            for product_name, quantity in shift_plan.items():
                total_revenue += quantity * self.products[product_name].margin

        return {
            "total_production": round(total_production, 2),
            "total_demand": round(total_demand, 2),
            "service_level_pct": round(service_level, 2),
            "avg_machine_utilization_pct": round(avg_utilization, 2),
            "total_revenue": round(total_revenue, 2),
            "unmet_demand_pct": round(
                total_unmet / total_demand * 100.0 if total_demand else 0.0, 2
            ),
        }

    def generate_schedule(self, demand_forecast: Mapping[str, float]) -> dict:
        production_plan, unmet_demand, utilization = self.optimize_production_allocation(
            demand_forecast, self.machines
        )
        kpis = self.calculate_kpis(
            production_plan, unmet_demand, utilization, demand_forecast
        )
        result = {
            "timestamp": datetime.now(timezone.utc),
            "production_plan": production_plan,
            "unmet_demand": unmet_demand,
            "machine_utilization": utilization,
            "kpis": kpis,
        }
        self.production_history.append(result)
        self.kpi_metrics = kpis
        return result

    def generate_recommendations(self, schedule_result: Mapping) -> list[str]:
        recommendations: list[str] = []
        kpis = schedule_result["kpis"]
        if kpis["service_level_pct"] < 80:
            recommendations.append(
                "Low service level: consider increasing capacity or adding flexible routing."
            )
        if kpis["avg_machine_utilization_pct"] < 70:
            recommendations.append(
                "Average utilization is below 70%: review workload balancing and capacity sizing."
            )
        high_unmet = {
            product: value
            for product, value in schedule_result["unmet_demand"].items()
            if value > 20
        }
        for product, value in high_unmet.items():
            recommendations.append(
                f"High unmet demand for {product}: {value:.1f} units remain unsatisfied."
            )
        return recommendations

#!/usr/bin/env python3
"""MILP solver for the Resource-Constrained Project Scheduling Problem (RCPSP)."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Hashable, Iterable, Mapping, Optional, Tuple

import matplotlib.pyplot as plt
import networkx as nx
import pulp


Activity = Hashable
Resource = Hashable


@dataclass(frozen=True)
class SolveResult:
    status: str
    start_times: Dict[Activity, int]
    makespan: Optional[int]


class RCPSPSolver:
    """Solve a single-mode RCPSP with renewable resources using a time-indexed MILP."""

    def __init__(
        self,
        activities: Iterable[Activity],
        durations: Mapping[Activity, int],
        predecessors: Mapping[Activity, Iterable[Activity]],
        resources_required: Mapping[Tuple[Activity, Resource], int],
        resource_limits: Mapping[Resource, int],
    ) -> None:
        self.activities = list(activities)
        self.durations = dict(durations)
        self.predecessors = {
            a: list(predecessors.get(a, [])) for a in self.activities
        }
        self.resources_required = dict(resources_required)
        self.resource_limits = dict(resource_limits)

        self.graph = self._validate_and_build_graph()
        self.horizon = sum(self.durations[a] for a in self.activities)
        self.est, self.lst = self._calculate_time_windows()

        self.model: Optional[pulp.LpProblem] = None
        self.start_times: Optional[Dict[Activity, int]] = None
        self.makespan: Optional[int] = None
        self.status: Optional[str] = None

    def _validate_and_build_graph(self) -> nx.DiGraph:
        if not self.activities:
            raise ValueError("activities must not be empty")
        if len(set(self.activities)) != len(self.activities):
            raise ValueError("activities must be unique")

        activity_set = set(self.activities)

        for activity in self.activities:
            if activity not in self.durations:
                raise ValueError(f"missing duration for activity {activity!r}")
            duration = self.durations[activity]
            if not isinstance(duration, int) or duration < 0:
                raise ValueError(f"duration for {activity!r} must be a non-negative integer")

        for activity, preds in self.predecessors.items():
            for pred in preds:
                if pred not in activity_set:
                    raise ValueError(
                        f"predecessor {pred!r} of activity {activity!r} is not in activities"
                    )
                if pred == activity:
                    raise ValueError(f"activity {activity!r} cannot precede itself")

        for resource, limit in self.resource_limits.items():
            if not isinstance(limit, int) or limit < 0:
                raise ValueError(f"resource limit for {resource!r} must be non-negative")

        for (activity, resource), requirement in self.resources_required.items():
            if activity not in activity_set:
                raise ValueError(f"unknown activity in resource requirement: {activity!r}")
            if resource not in self.resource_limits:
                raise ValueError(f"missing capacity for resource {resource!r}")
            if not isinstance(requirement, int) or requirement < 0:
                raise ValueError("resource requirements must be non-negative integers")
            if requirement > self.resource_limits[resource]:
                raise ValueError(
                    f"activity {activity!r} requires {requirement} units of {resource!r}, "
                    f"but capacity is {self.resource_limits[resource]}"
                )

        graph = nx.DiGraph()
        graph.add_nodes_from(self.activities)
        for activity in self.activities:
            for pred in self.predecessors[activity]:
                graph.add_edge(pred, activity)

        if not nx.is_directed_acyclic_graph(graph):
            raise ValueError("precedence graph must be a directed acyclic graph")

        return graph

    def _calculate_time_windows(self) -> Tuple[Dict[Activity, int], Dict[Activity, int]]:
        """Compute precedence-based EST/LST bounds using a valid serial-schedule horizon."""
        topo = list(nx.topological_sort(self.graph))

        est = {a: 0 for a in self.activities}
        for activity in topo:
            if self.predecessors[activity]:
                est[activity] = max(
                    est[pred] + self.durations[pred]
                    for pred in self.predecessors[activity]
                )

        lst = {
            activity: self.horizon - self.durations[activity]
            for activity in self.activities
        }

        for activity in reversed(topo):
            successors = list(self.graph.successors(activity))
            if successors:
                lst[activity] = min(
                    lst[succ] - self.durations[activity] for succ in successors
                )
            lst[activity] = max(lst[activity], est[activity])

        return est, lst

    def _start_expression(self, x, activity: Activity):
        return pulp.lpSum(
            t * x[activity, t]
            for t in range(self.est[activity], self.lst[activity] + 1)
        )

    def build_model(self) -> pulp.LpProblem:
        model = pulp.LpProblem("RCPSP", pulp.LpMinimize)

        x = {
            (activity, t): pulp.LpVariable(
                f"start_{str(activity)}_{t}", cat=pulp.LpBinary
            )
            for activity in self.activities
            for t in range(self.est[activity], self.lst[activity] + 1)
        }

        makespan = pulp.LpVariable(
            "makespan", lowBound=0, upBound=self.horizon, cat=pulp.LpInteger
        )
        model += makespan

        for activity in self.activities:
            model += (
                pulp.lpSum(
                    x[activity, t]
                    for t in range(self.est[activity], self.lst[activity] + 1)
                )
                == 1,
                f"start_once_{activity}",
            )

        for successor in self.activities:
            for predecessor in self.predecessors[successor]:
                model += (
                    self._start_expression(x, predecessor)
                    + self.durations[predecessor]
                    <= self._start_expression(x, successor),
                    f"precedence_{predecessor}_{successor}",
                )

        for resource, capacity in self.resource_limits.items():
            for tau in range(self.horizon):
                usage_terms = []
                for activity in self.activities:
                    requirement = self.resources_required.get((activity, resource), 0)
                    duration = self.durations[activity]
                    if requirement == 0 or duration == 0:
                        continue

                    earliest_start = max(self.est[activity], tau - duration + 1)
                    latest_start = min(self.lst[activity], tau)
                    if earliest_start <= latest_start:
                        usage_terms.extend(
                            requirement * x[activity, start]
                            for start in range(earliest_start, latest_start + 1)
                        )

                if usage_terms:
                    model += (
                        pulp.lpSum(usage_terms) <= capacity,
                        f"resource_{resource}_time_{tau}",
                    )

        for activity in self.activities:
            model += (
                self._start_expression(x, activity) + self.durations[activity]
                <= makespan,
                f"makespan_{activity}",
            )

        self._x = x
        self._makespan_var = makespan
        self.model = model
        return model

    def solve(
        self,
        time_limit: Optional[int] = None,
        mip_gap: Optional[float] = 0.0,
        msg: bool = False,
    ) -> SolveResult:
        if time_limit is not None and time_limit <= 0:
            raise ValueError("time_limit must be positive")
        if mip_gap is not None and not 0 <= mip_gap <= 1:
            raise ValueError("mip_gap must be between 0 and 1")

        model = self.build_model()
        solver = pulp.PULP_CBC_CMD(
            msg=msg,
            timeLimit=time_limit,
            gapRel=mip_gap,
        )
        model.solve(solver)

        status = pulp.LpStatus[model.status]
        self.status = status

        if status != "Optimal":
            self.start_times = None
            self.makespan = None
            return SolveResult(status=status, start_times={}, makespan=None)

        start_times: Dict[Activity, int] = {}
        for activity in self.activities:
            for t in range(self.est[activity], self.lst[activity] + 1):
                if pulp.value(self._x[activity, t]) > 0.5:
                    start_times[activity] = t
                    break

        makespan = int(round(pulp.value(self._makespan_var)))
        self.start_times = start_times
        self.makespan = makespan
        return SolveResult(status=status, start_times=start_times, makespan=makespan)

    def resource_usage(self) -> Dict[Resource, list[int]]:
        if self.start_times is None or self.makespan is None:
            raise RuntimeError("solve the model before requesting resource usage")

        usage = {
            resource: [0] * self.makespan
            for resource in self.resource_limits
        }

        for activity, start in self.start_times.items():
            duration = self.durations[activity]
            for tau in range(start, start + duration):
                for resource in self.resource_limits:
                    usage[resource][tau] += self.resources_required.get(
                        (activity, resource), 0
                    )

        return usage

    def plot_gantt_chart(self, figsize=(12, 6)):
        if self.start_times is None or self.makespan is None:
            raise RuntimeError("solve the model before plotting")

        fig, ax = plt.subplots(figsize=figsize)
        ordered = sorted(self.activities, key=lambda a: (self.start_times[a], str(a)))

        for y, activity in enumerate(ordered):
            start = self.start_times[activity]
            duration = self.durations[activity]
            ax.barh(y, duration, left=start, height=0.55)
            ax.text(
                start + duration / 2,
                y,
                str(activity),
                ha="center",
                va="center",
            )

        ax.set_yticks(range(len(ordered)))
        ax.set_yticklabels([str(a) for a in ordered])
        ax.set_xlabel("Time")
        ax.set_ylabel("Activity")
        ax.set_title(f"RCPSP schedule (makespan = {self.makespan})")
        ax.grid(True, axis="x", linestyle="--", alpha=0.5)
        ax.set_xlim(0, self.makespan + 1)
        fig.tight_layout()
        return fig, ax

    def plot_resource_usage(self, figsize=(12, 6)):
        if self.makespan is None:
            raise RuntimeError("solve the model before plotting")

        usage = self.resource_usage()
        fig, ax = plt.subplots(figsize=figsize)

        for resource, values in usage.items():
            ax.step(range(self.makespan), values, where="post", label=f"Resource {resource}")
            ax.axhline(
                self.resource_limits[resource],
                linestyle="--",
                alpha=0.6,
                label=f"{resource} capacity",
            )

        ax.set_xlabel("Time")
        ax.set_ylabel("Units in use")
        ax.set_title("Renewable resource usage")
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.legend()
        fig.tight_layout()
        return fig, ax


def example_problem() -> RCPSPSolver:
    activities = list(range(10))
    durations = {0: 0, 1: 3, 2: 4, 3: 2, 4: 5, 5: 1, 6: 3, 7: 4, 8: 2, 9: 0}
    predecessors = {
        0: [],
        1: [0],
        2: [0],
        3: [1],
        4: [1],
        5: [2],
        6: [3, 5],
        7: [4],
        8: [6],
        9: [7, 8],
    }
    resources_required = {
        (1, "workers"): 3, (2, "workers"): 2, (3, "workers"): 1,
        (4, "workers"): 2, (5, "workers"): 1, (6, "workers"): 3,
        (7, "workers"): 1, (8, "workers"): 2,
        (1, "machines"): 0, (2, "machines"): 1, (3, "machines"): 2,
        (4, "machines"): 2, (5, "machines"): 2, (6, "machines"): 1,
        (7, "machines"): 1, (8, "machines"): 2,
    }
    resource_limits = {"workers": 4, "machines": 3}

    solver = RCPSPSolver(
        activities,
        durations,
        predecessors,
        resources_required,
        resource_limits,
    )
    result = solver.solve()
    print("Status:", result.status)
    print("Optimal makespan:", result.makespan)
    print("Start times:", result.start_times)
    return solver


if __name__ == "__main__":
    example_problem()

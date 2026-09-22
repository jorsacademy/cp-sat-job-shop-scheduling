from __future__ import annotations

from dataclasses import dataclass
from math import ceil
from typing import Dict, List, Sequence, Tuple

TaskTimes = Dict[str, int]
Edge = Tuple[str, str]


@dataclass(frozen=True)
class BalanceResult:
    stations: List[List[str]]
    cycle_time: int
    task_times: TaskTimes

    @property
    def station_loads(self) -> List[int]:
        return [sum(self.task_times[t] for t in station) for station in self.stations]

    @property
    def station_count(self) -> int:
        return len(self.stations)

    @property
    def total_work(self) -> int:
        return sum(self.task_times.values())

    @property
    def theoretical_minimum(self) -> int:
        return ceil(self.total_work / self.cycle_time)

    @property
    def line_efficiency(self) -> float:
        return self.total_work / (self.station_count * self.cycle_time)

    @property
    def balance_delay(self) -> float:
        return 1.0 - self.line_efficiency


def validate_instance(task_times: TaskTimes, precedence: Sequence[Edge], cycle_time: int) -> None:
    if not task_times:
        raise ValueError("At least one task is required.")
    if cycle_time <= 0:
        raise ValueError("Cycle time must be positive.")
    if any(time <= 0 for time in task_times.values()):
        raise ValueError("All task times must be positive.")
    too_long = [task for task, time in task_times.items() if time > cycle_time]
    if too_long:
        raise ValueError(f"Tasks exceed cycle time: {too_long}")
    task_set = set(task_times)
    for u, v in precedence:
        if u not in task_set or v not in task_set:
            raise ValueError(f"Unknown task in precedence edge {(u, v)}")
        if u == v:
            raise ValueError(f"Self-loop precedence edge is invalid: {(u, v)}")

    indegree = {t: 0 for t in task_times}
    successors = {t: [] for t in task_times}
    for u, v in precedence:
        successors[u].append(v)
        indegree[v] += 1
    queue = [t for t, degree in indegree.items() if degree == 0]
    visited = 0
    while queue:
        u = queue.pop()
        visited += 1
        for v in successors[u]:
            indegree[v] -= 1
            if indegree[v] == 0:
                queue.append(v)
    if visited != len(task_times):
        raise ValueError("Precedence graph contains a directed cycle.")


def predecessor_map(task_times: TaskTimes, precedence: Sequence[Edge]) -> Dict[str, set[str]]:
    pred = {t: set() for t in task_times}
    for u, v in precedence:
        pred[v].add(u)
    return pred


def successor_map(task_times: TaskTimes, precedence: Sequence[Edge]) -> Dict[str, set[str]]:
    succ = {t: set() for t in task_times}
    for u, v in precedence:
        succ[u].add(v)
    return succ


def transitive_successors(task_times: TaskTimes, precedence: Sequence[Edge]) -> Dict[str, set[str]]:
    succ = successor_map(task_times, precedence)

    def dfs(task: str, seen: set[str]) -> set[str]:
        out: set[str] = set()
        for nxt in succ[task]:
            if nxt not in seen:
                out.add(nxt)
                out.update(dfs(nxt, seen | {nxt}))
        return out

    return {task: dfs(task, {task}) for task in task_times}


def validate_solution(result: BalanceResult, precedence: Sequence[Edge]) -> None:
    assigned = [task for station in result.stations for task in station]
    if len(assigned) != len(result.task_times) or set(assigned) != set(result.task_times):
        raise AssertionError("Every task must be assigned exactly once.")
    if any(load > result.cycle_time for load in result.station_loads):
        raise AssertionError("A station exceeds the cycle time.")
    station_of = {task: s for s, station in enumerate(result.stations) for task in station}
    for u, v in precedence:
        if station_of[u] > station_of[v]:
            raise AssertionError(f"Precedence violated: {u} must not follow {v}.")

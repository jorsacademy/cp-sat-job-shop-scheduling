"""Unrelated parallel machines with eligibility: greedy baseline versus MILP.

Adapted from ManufacturingScheduler in im_rl.ipynb (cell 29). Each job has
one non-preemptive operation; there are no releases, setups or precedences.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
import json
import random
from time import perf_counter

import pulp


@dataclass(frozen=True)
class EligibleInstance:
    jobs: tuple[str, ...]
    machines: tuple[str, ...]
    # An absent pair means the job is ineligible on that machine.
    durations: dict[tuple[str, str], float]

    def validate(self):
        if not self.jobs or not self.machines:
            raise ValueError('jobs and machines must be nonempty')
        if len(set(self.jobs)) != len(self.jobs) or len(set(self.machines)) != len(self.machines):
            raise ValueError('identifiers must be unique')
        if any(j not in self.jobs or m not in self.machines for j, m in self.durations):
            raise ValueError('unknown job or machine')
        if any(not isfinite(v) or v <= 0 for v in self.durations.values()):
            raise ValueError('durations must be finite and positive')
        if any(not any((j, m) in self.durations for m in self.machines) for j in self.jobs):
            raise ValueError('every job needs an eligible machine')


def validate_assignment(instance, assignment):
    instance.validate()
    if set(assignment) != set(instance.jobs):
        raise ValueError('assignment must contain every job exactly once')
    loads = dict.fromkeys(instance.machines, 0.0)
    for job, machine in assignment.items():
        if (job, machine) not in instance.durations:
            raise ValueError('ineligible assignment')
        loads[machine] += instance.durations[job, machine]
    return max(loads.values())


def greedy_schedule(instance):
    """Shortest minimum duration first, then earliest eligible completion."""
    instance.validate()
    loads = dict.fromkeys(instance.machines, 0.0)
    assignment = {}
    jobs = sorted(instance.jobs, key=lambda j: (min(p for (job, _), p in instance.durations.items() if job == j), j))
    for j in jobs:
        eligible = [m for m in instance.machines if (j, m) in instance.durations]
        m = min(eligible, key=lambda m: (loads[m] + instance.durations[j, m], m))
        assignment[j] = m
        loads[m] += instance.durations[j, m]
    return assignment, validate_assignment(instance, assignment)


def solve_milp(instance):
    """Create variables only for eligible pairs; require proven optimal status."""
    instance.validate()
    model = pulp.LpProblem('Eligible_Unrelated_Machines', pulp.LpMinimize)
    x = {pair: pulp.LpVariable(f'x_{i}', cat='Binary') for i, pair in enumerate(instance.durations)}
    makespan = pulp.LpVariable('makespan', lowBound=0)
    model += makespan
    for job in instance.jobs:
        model += pulp.lpSum(var for (j, _), var in x.items() if j == job) == 1
    for machine in instance.machines:
        model += pulp.lpSum(instance.durations[pair] * var for pair, var in x.items() if pair[1] == machine) <= makespan
    status = model.solve(pulp.HiGHS(msg=False))
    if pulp.LpStatus[status] != 'Optimal':
        raise RuntimeError(f'Optimality not established: {pulp.LpStatus[status]}')
    assignment = {j: m for (j, m), var in x.items() if var.value() > 0.5}
    checked = validate_assignment(instance, assignment)
    if abs(checked - makespan.value()) > 1e-5:
        raise RuntimeError('solver objective disagrees with reconstructed schedule')
    return assignment, checked


def sample_instance(seed=42, jobs=10, machines=3):
    if jobs < 1 or machines < 1:
        raise ValueError('positive job and machine counts required')
    rng = random.Random(seed)
    job_ids = tuple(f'J{j}' for j in range(jobs))
    machine_ids = tuple(f'M{m}' for m in range(machines))
    durations = {}
    for j in job_ids:
        for m in rng.sample(machine_ids, rng.randint(1, machines)):
            durations[j, m] = rng.randint(15, 60)
    return EligibleInstance(job_ids, machine_ids, durations)


def gantt(instance, assignment, ax, title):
    """Serial display order does not change loads or makespan in this model."""
    validate_assignment(instance, assignment)
    for row, machine in enumerate(instance.machines):
        start = 0
        for job in instance.jobs:
            if assignment[job] == machine:
                duration = instance.durations[job, machine]
                ax.barh(row, duration, left=start, color='#286491', edgecolor='white')
                ax.text(start + duration / 2, row, job, color='white', ha='center', va='center')
                start += duration
    ax.set_yticks(range(len(instance.machines)), instance.machines)
    ax.set_xlabel('Time (synthetic time units)')
    ax.set_title(title)
    ax.set_axisbelow(True)
    ax.grid(axis='x', alpha=0.2)


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plot', help='Optional output image path')
    args = parser.parse_args()
    results = []
    for seed in (42, 43, 44):
        instance = sample_instance(seed)
        start = perf_counter()
        greedy, g = greedy_schedule(instance)
        greedy_seconds = perf_counter() - start
        start = perf_counter()
        exact, opt = solve_milp(instance)
        results.append({'seed': seed, 'greedy_makespan': g, 'optimal_makespan': opt,
                        'gap_percent': 100 * (g / opt - 1), 'greedy_seconds': greedy_seconds,
                        'milp_seconds': perf_counter() - start})
        if seed == 42 and args.plot:
            import matplotlib.pyplot as plt
            fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True, layout='constrained')
            gantt(instance, greedy, axes[0], f'Greedy: makespan {g:g}')
            gantt(instance, exact, axes[1], f'MILP optimum: makespan {opt:g}')
            fig.savefig(args.plot, dpi=160)
            plt.close(fig)
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()

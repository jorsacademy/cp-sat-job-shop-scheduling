# CP-SAT Job Shop Scheduling

A reproducible Operations Research implementation of job-shop scheduling with Google OR-Tools CP-SAT. The repository focuses on interval variables, machine disjunctive constraints, job precedences, release dates, due-date penalties, solver bounds, schedule validation, and comparison with a deterministic feasible baseline.

The code uses CP-SAT directly rather than wrapping a scheduling library. Every operation is represented by integer start/end variables and an interval variable. Operations assigned to the same machine are linked by `add_no_overlap`, while technological precedence constraints enforce the operation order inside each job.

## Problem

For each job `j`, operation `k` has a fixed processing time `p_jk` and a required machine `m_jk`.

The core constraints are

```text
start[j,k+1] >= end[j,k]                         job precedence
NoOverlap(intervals assigned to machine m)      machine capacity
start[j,0] >= release[j]                        release dates
end[j,k] = start[j,k] + processing_time[j,k]
```

The model can optimize makespan alone or a weighted combination of makespan and weighted tardiness:

```text
minimize
    makespan_weight * C_max
    + tardiness_weight * sum_j weight_j * T_j

T_j >= completion_j - due_j
T_j >= 0
```

All decision variables and coefficients are integer, which matches CP-SAT's integer modeling interface.

## Why CP-SAT for scheduling?

Scheduling is one of CP-SAT's strongest modeling domains because interval variables and global constraints express temporal structure directly. In the official OR-Tools job-shop formulation, each task has start/end/interval variables, `add_no_overlap` prevents machine conflicts, precedence constraints preserve job order, and a max-equality variable defines makespan.

This project extends that standard formulation with:

- job release dates,
- optional due dates and job weights,
- weighted tardiness,
- explicit solver lower bounds and optimality gap reporting,
- independent schedule validation,
- machine-utilization diagnostics,
- a deterministic feasible serial baseline,
- a known benchmark with proven optimum.

## Repository structure

```text
.
├── .github/workflows/ci.yml
├── examples/run_demo.py
├── src/cpsat_jssp/
│   ├── __init__.py
│   ├── __main__.py
│   ├── baseline.py
│   ├── data.py
│   ├── experiment.py
│   ├── model.py
│   ├── solution.py
│   └── solver.py
├── tests/
│   ├── test_data_solution.py
│   ├── test_diagnostics_cli.py
│   └── test_model_solver.py
├── LICENSE
├── README.md
└── pyproject.toml
```

## Installation

```bash
python -m pip install -e ".[dev]"
```

Python 3.10+ is supported.

## Run

```bash
python -m cpsat_jssp \
  --time-limit 10 \
  --workers 1 \
  --seed 2026 \
  --makespan-weight 10 \
  --tardiness-weight 1
```

or

```bash
python examples/run_demo.py
```

The command returns JSON containing:

- solver status,
- objective value,
- best objective bound,
- absolute optimality gap,
- makespan,
- weighted tardiness,
- a simple analytical makespan lower bound,
- deterministic baseline results,
- conflicts and branches,
- solver wall time,
- machine utilization,
- operation schedules by machine.

## Verification benchmark

`classic_three_job_instance()` is the standard small three-job job-shop instance used in OR-Tools teaching material. Its optimal makespan is `11`.

The test suite requires CP-SAT to return

```text
status = OPTIMAL
makespan = 11
best bound = 11
```

This is more informative than merely checking that a feasible schedule exists: the model is tested against a known optimum.

## Independent schedule validation

The solver output is not trusted automatically. `validate_schedule` reconstructs the schedule and checks:

- every operation appears exactly once,
- each operation remains on its specified machine,
- processing durations are preserved,
- job release dates are respected,
- technological precedences hold,
- no two operations overlap on the same machine,
- reported makespan is consistent,
- reported weighted tardiness is consistent with completion times and due dates.

This catches errors in result extraction separately from CP-SAT model feasibility.

## Baseline and diagnostics

`serial_schedule_generation` builds a deterministic feasible schedule by processing jobs in index order and placing each operation at the earliest time allowed by its job predecessor and machine availability.

It is intentionally simple. Its role is to provide a feasible reference point, not to compete with CP-SAT as a strong heuristic.

`machine_utilization` reports total processing time on each machine divided by the final makespan. `lower_bound_makespan` reports the maximum of the longest released job chain and the heaviest machine workload. This lower bound is inexpensive and generally weaker than the CP-SAT solver's internal best bound.

## Reproducibility and parallel search

The CLI defaults to one CP-SAT worker. This makes demonstrations more reproducible and avoids presenting parallel-search variability as an algorithmic effect. The `workers` argument can be increased for performance experiments.

A finite time limit may produce `FEASIBLE` rather than `OPTIMAL`. In that case, the returned best objective bound is retained so that the remaining optimality gap is visible rather than hidden.

## Tests

```bash
python -m pytest
```

The test suite covers:

- input-data validation,
- deterministic feasible baseline construction,
- analytical lower-bound consistency,
- objective-model validation,
- exact recovery of the known makespan-11 benchmark,
- release-date enforcement,
- due-date/tardiness modeling,
- independent schedule validation,
- CP-SAT improvement over the simple baseline on the demo objective,
- bounded machine utilization,
- CLI JSON integration.

GitHub Actions installs OR-Tools, compiles the source tree, and runs the full suite on Python 3.10 and 3.12.

## Methodological notes

- CP-SAT is an exact solver when it proves `OPTIMAL`; a time-limited `FEASIBLE` result is not a proof of optimality.
- The simple workload lower bound in this repository is a diagnostic, not the solver's full lower-bounding machinery.
- Weighted-sum objectives encode a modeling preference. Changing makespan and tardiness weights can change the schedule substantially.
- Job-shop scheduling here uses fixed machine assignments. Flexible job shop would require optional intervals and machine-choice decisions.
- Sequence-dependent setup times, calendars, preventive maintenance, alternative resources, and energy constraints are natural extensions but are intentionally kept outside the core implementation.
- A CP-SAT model is not a MILP model merely because both contain integer variables; CP-SAT combines SAT-based search, constraint programming propagation, and linear reasoning.

## References

- Google OR-Tools, **The Job Shop Problem**: https://developers.google.com/optimization/scheduling/job_shop
- Google OR-Tools, **CP-SAT Solver**: https://developers.google.com/optimization/cp/cp_solver
- Google OR-Tools source and examples: https://github.com/google/or-tools

## License

MIT

# Resource-Constrained Project Scheduling with PuLP

A compact implementation of the **Resource-Constrained Project Scheduling Problem (RCPSP)** using a time-indexed mixed-integer linear programming model in PuLP/CBC.

The solver minimizes project makespan while enforcing:

- precedence constraints between activities,
- renewable-resource capacity limits,
- one start time per activity,
- precedence-derived earliest/latest start bounds.

## Why this version

This repository is a cleaned-up version of an older RCPSP prototype. The main modeling changes are:

- CPM-style time windows are preserved instead of expanding every activity to almost the full horizon.
- Activity IDs are generic; the solver does not assume dummy activities must be `0` and `max(activity_id)`.
- Input validation detects cycles, missing durations, invalid capacities, and impossible single-activity resource requirements.
- The time-indexed resource constraints only create overlap terms that can actually be active at each period.
- Solver status and outputs are represented explicitly.
- Tests cover graph validation, capacity validation, time windows, and a small optimal scheduling case.

## Mathematical model

For each activity `i` and feasible start time `t`, binary variable `x[i,t]` equals 1 if activity `i` starts at `t`.

The objective is to minimize project makespan `C_max`.

Each activity starts exactly once:

```text
sum_t x[i,t] = 1
```

For every precedence arc `i -> j`:

```text
S_i + d_i <= S_j
```

For every renewable resource `r` and time period `tau`:

```text
sum_i q[i,r] * I(i active at tau) <= Q[r]
```

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows:

```bash
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run the example

```bash
python rcpsp_solver.py
```

The bundled example contains ten activities and two renewable resources.

## Run tests

```bash
pytest -q
```

## Visualization

After solving:

```python
solver.plot_gantt_chart()
solver.plot_resource_usage()
```

Call `matplotlib.pyplot.show()` if you are running interactively.

## Notes

This implementation uses a **time-indexed MILP**, which is clear and exact for small-to-medium educational instances but can grow quickly as the planning horizon increases. Larger RCPSP instances may benefit from tighter bounds, decomposition, CP-SAT, constraint programming, or specialized heuristics/metaheuristics.

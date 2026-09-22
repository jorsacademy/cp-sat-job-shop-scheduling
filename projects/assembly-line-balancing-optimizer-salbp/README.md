# Assembly Line Balancing Optimizer (SALBP-1)

A Python project for the **Simple Assembly Line Balancing Problem Type 1 (SALBP-1)**. The objective is to minimize the number of workstations for a fixed cycle time while respecting task precedence constraints.

The repository contains:

- Exact SALBP-1 optimization with Google OR-Tools CP-SAT
- Largest Candidate Rule (LCR)
- Ranked Positional Weight (RPW)
- Validation utilities and tests
- A synthetic example dataset created specifically for this repository

## Mathematical formulation

Let `x[t,s] = 1` when task `t` is assigned to station `s`, and `y[s] = 1` when station `s` is used.

Objective:

```text
minimize sum_s y[s]
```

Subject to:

```text
sum_s x[t,s] = 1                                      for every task t
sum_t time[t] * x[t,s] <= cycle_time * y[s]          for every station s
y[s+1] <= y[s]                                        for consecutive stations
station(u) <= station(v)                              for every precedence edge u -> v
x[t,s], y[s] are binary
```

The precedence model uses an explicit directed edge list. Task identifiers do not imply precedence.

## Example instance

The bundled instance contains 18 tasks, 22 precedence relations, a 15-second cycle time, and 92 seconds of total work content.

The workload lower bound is:

```text
ceil(92 / 15) = 7 stations
```

A separate exhaustive dynamic-programming verification of this bundled dataset also found a minimum of 7 stations, so the instance has a known optimum of 7.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e .
pip install -r requirements.txt
```

## Run

```bash
python run_example.py
```

## Test

```bash
pytest -q
```

The tests check task uniqueness, cycle-time feasibility, precedence feasibility, and the known seven-station optimum for the bundled instance.

## Metrics

The result object reports:

- Station count
- Station loads
- Total work content
- Theoretical minimum station count
- Line efficiency
- Balance delay

## Validation note

The model logic and bundled instance were independently checked before publication. In the current execution environment, third-party packages could not be installed because outbound package downloads were unavailable, so the OR-Tools test suite could not be executed there. The repository includes automated tests for execution in a normal Python environment with the declared dependencies installed.

## License

This repository is **source-available for non-commercial use only**. Commercial use requires prior written permission from the copyright holder. See `LICENSE`.

This is intentionally not an OSI-approved open-source license because OSI-compliant licenses cannot prohibit commercial use.

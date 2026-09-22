# Parallel Machine Scheduling with MILP Optimization

This project demonstrates a medium-level **identical parallel machine scheduling** problem solved with a **Mixed-Integer Linear Programming (MILP)** model in Python.

The objective is to assign a set of independent jobs to identical parallel machines so that the **makespan** — the largest total workload assigned to any machine — is minimized.

The project includes a modular data layer, MILP model construction, independent solution validation, detailed schedule reporting, and automatic Gantt chart generation.

## Problem Description

The sample instance contains:

- 12 independent jobs
- 3 identical parallel machines
- Deterministic processing times
- No preemption
- No release dates
- No precedence constraints
- No sequence-dependent setup times

Each job must be assigned to exactly one machine. Since machines are identical and there are no sequence-dependent effects, the order of jobs on an individual machine does not influence the objective value. The MILP therefore optimizes the assignment decisions directly.

## Mathematical Formulation

### Sets

- `J`: set of jobs
- `M`: set of identical machines

### Parameter

- `p_j`: processing time of job `j`

### Decision Variable

- `x_jm = 1` if job `j` is assigned to machine `m`; `0` otherwise

### Makespan Variable

- `C_max`: maximum workload among all machines

### Objective Function

Minimize:

```text
C_max
```

### Constraints

Each job must be assigned exactly once:

```text
sum_m x_jm = 1    for every job j
```

The workload of each machine cannot exceed the makespan:

```text
sum_j p_j * x_jm <= C_max    for every machine m
```

Binary restriction:

```text
x_jm in {0, 1}
```

## Sample Data

| Job | Processing Time |
|---|---:|
| J1 | 14 |
| J2 | 9 |
| J3 | 18 |
| J4 | 7 |
| J5 | 13 |
| J6 | 6 |
| J7 | 11 |
| J8 | 16 |
| J9 | 8 |
| J10 | 10 |
| J11 | 15 |
| J12 | 5 |

The total processing time is 132 time units. With three machines, the average-load lower bound is:

```text
ceil(132 / 3) = 44
```

The longest job requires 18 time units. Therefore, the standard lower bound is:

```text
max(44, 18) = 44
```

If the solver finds a feasible solution with makespan 44, that solution is proven optimal because it reaches the theoretical lower bound.

## Solution Validation

The project does not rely only on the solver status. After optimization, it independently verifies that:

1. Every expected job appears in the schedule.
2. No job is assigned more than once.
3. No unknown job appears in the solution.
4. The reconstructed machine workloads match the optimized makespan.
5. The makespan is not below a valid theoretical lower bound.

A successful run prints:

```text
Independent solution validation: PASSED
```

## Result Reporting

The program prints:

- Input processing-time table
- HiGHS solver status
- Theoretical lower bound
- Optimal makespan
- Gap between the lower bound and optimized makespan
- Machine-level job assignments
- Machine workloads
- Start, duration, and completion time for every scheduled job

The within-machine order is generated deterministically for reporting and visualization. It does not change the objective value for this specific scheduling model.

## Gantt Chart

After solving the MILP, the program automatically creates a Gantt chart with Matplotlib.

The generated file is saved as:

```text
outputs/gantt_chart.png
```

Each bar represents a scheduled job. The horizontal position indicates the job's start and completion times, while each row represents one machine.

The `outputs/` directory is excluded from Git because it contains generated results.

## Project Structure

```text
.
├── data.py
├── scheduler.py
├── visualization.py
├── main.py
├── requirements.txt
├── README.md
├── LICENSE
└── .gitignore
```

### `data.py`

Contains the `SchedulingData` data class, sample problem instance, and input-data validation.

### `scheduler.py`

Contains the MILP formulation, HiGHS solve procedure, schedule extraction, lower-bound calculation, machine-load calculation, and independent solution-validation functions.

### `visualization.py`

Builds deterministic start times from the optimized assignment and creates the Gantt chart.

### `main.py`

Coordinates the complete workflow:

```text
Data -> MILP Model -> Solver -> Schedule Extraction -> Validation -> Reporting -> Gantt Chart
```

## Technologies

- Python 3.10+
- PuLP
- HiGHS MILP Solver
- Matplotlib

## Installation

Clone the repository and install the dependencies:

```bash
pip install -r requirements.txt
```

## Run

Execute:

```bash
python main.py
```

## Why This Formulation Is Correct

A common modeling error in parallel-machine scheduling is to introduce completion-time variables indexed by sequence positions without defining a valid sequencing structure. In that case, the sequence index does not represent a real schedule.

For the problem considered in this repository, completion-time or sequence-position decision variables are unnecessary. There are no release dates, precedence constraints, setup times, or other sequence-dependent effects. Therefore, minimizing the maximum total processing load assigned to any identical machine is equivalent to minimizing the makespan.

This produces a compact and mathematically valid MILP formulation.

## Possible Extensions

The current model is intentionally medium-level and can be extended to include:

- Unrelated or uniform parallel machines
- Machine-dependent processing times
- Release dates
- Job priorities or weights
- Due dates and tardiness penalties
- Machine eligibility restrictions
- Sequence-dependent setup times
- Precedence constraints
- Multiple optimization objectives

These extensions require additional decision variables and constraints because sequencing may then affect feasibility or the objective value.

## License

This repository is **not licensed for commercial use**.

The source code may be used for personal, educational, and non-commercial research purposes only. Commercial use, commercial redistribution, sublicensing, resale, or incorporation into a commercial product or service requires prior written permission from the copyright holder.

See the `LICENSE` file for the complete terms.

## Extension: unrelated machines with eligibility

`eligible_machines.py` adapts the greedy scheduling example from cell 29 of
`im_rl.ipynb` into a separately validated comparison. Unlike the introductory
identical-machine model, each eligible pair has its own duration `p[j,m]`.
Missing pairs are forbidden. Each job still has exactly one operation: this
is unrelated parallel-machine scheduling, not a job shop or RL environment.

The MILP creates binary variables only for eligible pairs, assigns each job
exactly once and bounds every machine load by makespan. The heuristic orders
jobs by shortest eligible duration and chooses the earliest eligible completion.
Both methods use identical instances and independent assignment validation.

```bash
python eligible_machines.py
python eligible_machines.py --plot eligible_schedule.png
python -m pip install pytest
python -m pytest -q
```

Three synthetic seeds (42, 43, 44) report greedy and proven-optimal makespan,
percentage optimality gap and measured wall time. Runtime includes model
construction for the MILP and is machine-dependent; these small examples are
not a scalability benchmark. The optional chart shows the first seed.
Tests compare the MILP with exhaustive enumeration on small instances, include
an eligibility trap where greedy is suboptimal, and preserve the original
identical-machine example's optimum of 44.

The solver uses the native `highspy` Python interface on macOS, Linux and Windows,
avoiding reliance on an architecture-specific bundled CBC executable.

Reference runs are saved in [`results/eligible_comparison.json`](results/eligible_comparison.json).
For seed 42, greedy makespan is 137 versus a MILP optimum of 115 (19.13% gap).
Seeds 43 and 44 have gaps of 28.24% and 18.18%. These are synthetic examples,
not operational savings estimates.

![Greedy and optimal eligible-machine schedules](results/eligible_schedule.png)

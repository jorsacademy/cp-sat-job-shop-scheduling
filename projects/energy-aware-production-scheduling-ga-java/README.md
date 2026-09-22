# Energy-Aware Production Scheduling with a Genetic Algorithm (Java)

A compact Java implementation of multi-objective production scheduling using a Genetic Algorithm (GA). The model jointly considers production completion time, energy cost, and peak power while respecting task dependencies and machine requirements.

## Features

- Multi-mode production tasks
- Precedence/dependency constraints
- Required-machine constraints
- Random topological task ordering
- Grid and renewable energy sources with time-varying availability/prices
- Multi-objective weighted fitness
- Makespan minimization
- Energy-cost minimization
- Peak-power reduction
- Tournament selection
- Elitism
- Multiple mutation operators

## What was corrected from the initial prototype

The initial prototype compiled, but several modeled concepts were not actually enforced by the optimizer. This version fixes those issues:

- Optimization weights passed through `setWeights(...)` now affect the objective function.
- Task dependencies are enforced during schedule evaluation.
- Initial and mutated task orders remain precedence-feasible through topological ordering.
- Task-mode counts are dynamic instead of assuming exactly two modes globally.
- `requiredMachine` is enforced for each selected task mode.
- Mode mutations update the corresponding required machine assignment.
- Solar and grid sources both participate in the energy-cost calculation.
- Energy demand is allocated to available sources in ascending price order.
- Unsupplied energy demand receives a large penalty instead of being treated as free.
- Makespan, energy cost, and peak power are scaled before applying objective weights.
- Pause semantics are explicit: `pauseBefore[i]` is idle time inserted before task `i`.
- Basic model validation detects missing tasks, missing machines, unknown dependencies, unknown required machines, and dependency cycles.

## Example production system

The included demonstration models five sequential operations:

1. `LoadPart`
2. `FixPart`
3. `Rotate`
4. `Process`
5. `Unload`

Each task has alternative execution modes with different duration and power characteristics. Three machines are divided across two production cells.

The energy model contains:

- **Solar** — zero marginal price with time-varying availability.
- **Grid** — always available with an illustrative time-of-use tariff.

The sample values are illustrative rather than calibrated industrial measurements.

## Objective function

The GA minimizes a normalized weighted objective:

```text
fitness = w_m * normalized_makespan
        + w_e * normalized_energy_cost
        + w_p * normalized_peak_power
```

Three example weight configurations are run by `main`:

```text
Balanced:          0.4 / 0.4 / 0.2
Makespan-focused:  0.8 / 0.1 / 0.1
Energy-focused:    0.1 / 0.8 / 0.1
```

Weights are normalized internally, so they do not have to sum exactly to 1.0.

## Requirements

- Java 8 or newer
- No external dependencies

## Compile and run

```bash
javac ProductionSchedulingGA.java
java ProductionSchedulingGA
```

The program prints GA progress and the best schedule found for each objective configuration, including:

- makespan
- energy cost
- peak power
- normalized fitness
- task order
- task modes
- machine assignments
- pause-before times

## Notes

This project is an educational/research-oriented implementation. Real production scheduling normally requires additional constraints such as setup times, calendars, buffers, transport times, resource capacities, stochastic disruptions, maintenance windows, and more detailed energy-market models.

## Possible extensions

- Pareto-front optimization (e.g. NSGA-II) instead of a weighted-sum objective
- Crossover operators for precedence-feasible schedules
- Alternative-machine eligibility rather than one required machine per mode
- Battery/storage modeling
- Demand charges and explicit peak-power limits
- Setup/changeover matrices
- Machine maintenance and downtime calendars
- Gantt-chart and power-profile visualization
- Benchmark instances and statistical GA experiments

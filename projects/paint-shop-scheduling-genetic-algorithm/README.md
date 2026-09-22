# Paint Shop Scheduling with a Genetic Algorithm

This repository contains an educational optimization project inspired by appliance manufacturing paint-shop operations. The model represents a production environment in which washing-machine body parts are painted in several shades of white and gray before they are transferred to downstream assembly.

The objective is not to reproduce a specific manufacturer's proprietary planning system. Instead, the project demonstrates how a sequence-dependent production scheduling problem can be formulated and solved with a permutation-based Genetic Algorithm (GA) without linear programming.

## Problem

A large appliance manufacturer can have hundreds of catalog models, while only a subset is active in a given planning horizon. Model frequencies are not uniform. Some models are produced frequently, some are produced rarely, some are being phased out, and others may be newly introduced. In addition, a production order may not be immediately available because upstream body production, material supply, or another component is delayed.

The paint shop is sequence dependent. Switching between nearby shades is cheaper than switching between distant shades, and moving from a darker shade to a lighter shade is assumed to require additional cleaning because of contamination risk. At the same time, a schedule that only minimizes shade changes may starve the assembly line. For that reason, the optimization objective also penalizes lateness relative to downstream demand and idle time caused by unavailable jobs.

## Optimization objective

The GA minimizes a weighted cost function:

`Total Cost = w1 * Changeover Time + w2 * Weighted Tardiness + w3 * Material Idle Time`

Changeover time represents shade-dependent setup and cleaning. Weighted tardiness represents the penalty for completing production later than its required downstream position, with higher-priority jobs receiving a larger penalty. Material idle time represents waiting when the next scheduled job is not yet available.

The weights are configurable through `GAConfig`.

## Why this is a real optimization model

This repository does not simply sort models by shade or frequency. A schedule is encoded as a permutation of individual production jobs. The Genetic Algorithm searches the combinatorial solution space by repeatedly evaluating alternative schedules, selecting better schedules, applying permutation-preserving Order Crossover (OX), and using swap or inversion mutation. Elitism retains the best solutions found so far.

Every physical production order has a unique `job_id`. This is important because multiple units can belong to the same washing-machine model. A valid chromosome must contain every job exactly once. The implementation validates this property after genetic operations.

## Genetic Algorithm structure

The implementation uses a standard permutation-based GA with several scheduling-oriented design choices. The initial population contains one deterministic heuristic schedule and multiple random schedules. Tournament selection chooses parents. Order Crossover preserves permutation feasibility. Mutation uses either a swap or an inversion. Elitism copies the best solutions into the next generation. The best-so-far solution is retained throughout the run.

The algorithm is therefore a conventional Genetic Algorithm adapted to a sequence-dependent manufacturing scheduling problem. It is not a linear-programming model and it does not call an LP/MIP solver.

## Synthetic factory data

The demo generator can create a catalog of 756 models while scheduling a smaller planning horizon of physical jobs. A configurable fraction of models is active. Production frequencies follow a long-tail distribution so that a small number of models appear more often than the rest. White shades dominate the product mix, while gray shades appear less frequently.

The generated data are synthetic. They are intended for teaching optimization logic and should not be interpreted as calibrated industrial data.

## Project structure

```text
src/paint_shop_ga.py      Core domain model, cost function and Genetic Algorithm
examples/run_demo.py      Reproducible demonstration with synthetic data
tests/test_optimizer.py   Integrity, reproducibility and optimization tests
README.md                 Project documentation
LICENSE                   Non-commercial license
```

## Running the example

From the repository root:

```bash
python -m examples.run_demo
```

The example creates a 756-model catalog, generates 500 physical production jobs, builds a deterministic heuristic baseline, runs the Genetic Algorithm, and reports the baseline cost, optimized cost, percentage improvement, and the first jobs in the optimized sequence.

## Running the tests

```bash
python -m unittest discover -s tests -v
```

The test suite checks that Order Crossover preserves every job exactly once, the optimizer always returns a valid permutation, the result is not worse than the heuristic seed schedule, and a fixed random seed produces reproducible output.

## Scope and limitations

The current model is intentionally compact. A production-grade paint-shop scheduler would normally use measured transition matrices, actual process times, conveyor and buffer capacities, batch-size restrictions, shift calendars, maintenance windows, quality constraints, rework flows, paint-booth capacity, chemical bath state, energy constraints, assembly-line takt requirements, component synchronization, and rolling-horizon rescheduling.

The present implementation should therefore be described as an educational industrial scheduling model rather than a digital replica of a real factory. Its value is in showing how a realistic scheduling objective can be represented and searched with a Genetic Algorithm.

## License

This project is available for personal, educational, academic, and non-commercial research use only. Commercial use requires separate written permission. See `LICENSE` for the complete terms.

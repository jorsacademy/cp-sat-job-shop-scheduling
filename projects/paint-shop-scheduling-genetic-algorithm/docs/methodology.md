# Methodology

## Industrial interpretation

This project models a simplified paint-shop sequencing problem in a washing-machine manufacturing environment. Body parts arrive from upstream fabrication and are painted before entering downstream assembly. The planning problem is difficult because sequence choices influence cleaning/setup time, while downstream demand and material availability create competing scheduling pressure.

The model intentionally separates catalog models from physical jobs. A factory may maintain hundreds of model definitions, but a planning horizon contains individual production orders. Several orders may belong to the same model, and each order is represented with a unique job identifier.

## Decision variable

The decision variable is the complete sequence of jobs entering the paint shop. A candidate solution is therefore a permutation of all jobs in the planning horizon.

## Cost model

For a candidate sequence, the simulator advances a simple production clock. Every job consumes one unit of processing time. If a scheduled job is unavailable, the clock waits until the job becomes available and this waiting time is recorded as material idle time. After processing, tardiness is calculated relative to the job's downstream due position and multiplied by its priority. Between consecutive jobs, a sequence-dependent setup time is added.

Shade indices are ordered from white toward dark gray. A transition between identical shades has no setup penalty in the educational model. Increasing shade distance increases setup time. A dark-to-light transition receives an additional cleaning penalty, representing greater contamination-control effort.

The objective is a weighted sum of changeover time, weighted tardiness, and material idle time. The weights are exposed in `GAConfig` so students can study trade-offs between paint-shop efficiency and downstream service.

## Search algorithm

The optimizer is a permutation-based Genetic Algorithm. The population contains one deterministic heuristic seed and random permutations. Tournament selection creates selection pressure without requiring normalized fitness values. Order Crossover (OX) is used because ordinary one-point or uniform crossover can duplicate jobs and delete others in a permutation problem. OX preserves the set of job identifiers. Mutation uses either a pairwise swap or subsequence inversion, both of which preserve permutation feasibility.

Elitism copies the best candidates into the next generation. The algorithm also retains the global best schedule found so far, so the returned solution cannot be worse than the deterministic heuristic included in the initial population.

## Validation

The implementation explicitly checks permutation integrity after genetic operations. Unit tests verify that crossover preserves every job exactly once, optimization returns the complete set of original jobs, a fixed seed gives reproducible output, and the returned schedule does not have a higher objective value than the heuristic seed.

These tests validate algorithmic consistency, not industrial optimality. A Genetic Algorithm is a metaheuristic and does not provide a mathematical proof that the global optimum has been found.

## Interpretation of results

A lower objective value means that the schedule provides a better compromise under the selected weights. It may accept a few additional shade transitions if that prevents large downstream tardiness, or it may delay a low-priority job to preserve a more efficient paint sequence. This trade-off is the central optimization concept demonstrated by the project.

## Limitations

The project uses synthetic data and simplified time units. It does not model a specific factory's chemistry, bath stages, ovens, conveyors, elevators, buffers, breakdowns, maintenance, rework, labor calendars, energy constraints, capacity by station, or exact assembly synchronization. For industrial deployment, the transition-time function and all operational constraints would need to be calibrated with plant data and the scheduler would normally operate in a rolling horizon.

The repository should therefore be presented as an educational case study in sequence-dependent manufacturing optimization rather than as a production-ready APS replacement.

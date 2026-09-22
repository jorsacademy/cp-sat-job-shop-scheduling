# Metaheuristics and Heuristic Optimization Research Series

This file maps repositories where the primary computational idea is heuristic, metaheuristic, adaptive neighborhood search, or derivative-free search. It is an index only: every repository remains independent because the neighborhood structure, encoding, constraints, and problem class differ.

## Genetic and evolutionary methods

- `paint-shop-scheduling-genetic-algorithm` — genetic algorithm for paint-shop scheduling.
- `airline-crew-workforce-optimization-ga` — genetic algorithm for workforce/crew decisions.
- `flexible-manufacturing-scheduling-genetic-algorithm` — GA for flexible manufacturing scheduling.
- `energy-aware-production-scheduling-ga-java` — energy-aware scheduling with GA in Java.
- `multimodal-distribution-network-genetic-algorithm` — GA for multimodal distribution/network decisions.
- `multi-objective-cvrp-nsga2-python` — NSGA-II for multi-objective routing.

## Neighborhood and local-search methods

- `alns-vehicle-routing` — Adaptive Large Neighborhood Search for routing.
- `time-dependent-vehicle-routing-alns-python` — ALNS adapted to time-dependent routing.
- `capacitated-facility-location-tabu-search-julia` — tabu search for capacitated facility location.
- `warehouse-order-packing-heuristics` — domain-specific packing heuristics.
- `wind-farm-layout-optimizer` — randomized greedy / heuristic layout construction.

## Learned or neural extensions

- `neural-large-neighborhood-search-cvrp` — learned guidance for LNS in routing.
- `neural-large-neighborhood-search-job-shop-scheduling-pytorch` — learned LNS for scheduling.
- `learning-augmented-online-machine-scheduling-python` — predictions augment online scheduling rather than replacing the optimization logic.

## Black-box bridge

- `nevergrad-black-box-policy-optimization` — derivative-free black-box search.
- `smac3-simulation-based-optimization` and `sambo-sequential-model-based-optimization` — model-based black-box optimization; cross-listed in the black-box optimization series rather than treated as classical metaheuristics.

## Why these stay separate

A GA for scheduling, NSGA-II for multi-objective routing, tabu search for facility location, and ALNS for routing may all be called metaheuristics, but their representations and move operators are problem-specific. Combining them would reduce clarity. They are better treated as a methodological comparison series.

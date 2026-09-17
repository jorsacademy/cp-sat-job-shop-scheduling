# Scheduling and Rescheduling Research Series

This repository belongs to a broader set of independent projects on deterministic scheduling, dynamic scheduling, workforce/crew scheduling, and learning-based scheduling. The projects are kept separate when the formulation, solver paradigm, or decision regime changes.

## Exact and mathematical-programming scheduling

| Repository | Main focus | Role in the series |
|---|---|---|
| `cp-sat-job-shop-scheduling` | Job-shop scheduling with CP-SAT interval variables and global constraints | Constraint-programming foundation |
| `parallel-machine-scheduling-milp-optimization` | Parallel-machine scheduling as MILP | Mathematical-programming alternative |
| `resource-constrained-project-scheduling-pulp` | RCPSP/resource-constrained project scheduling | Project-scheduling case study |
| `optimal-conference-meeting-scheduling-cp-sat` | Meeting scheduling with CP-SAT | Timetabling/meeting application |
| `aircraft-maintenance-scheduling-gurobi` | Aircraft maintenance scheduling | Aviation scheduling application |
| `aviation-crew-scheduling-milp` | Crew scheduling as MILP | Crew-scheduling formulation |
| `airline-crew-scheduling-column-generation` | Large-scale crew scheduling with column generation | Decomposition-based crew scheduling |

## Heuristic and metaheuristic scheduling

- `paint-shop-scheduling-genetic-algorithm`
- `flexible-manufacturing-scheduling-genetic-algorithm`
- `energy-aware-production-scheduling-ga-java`
- `airline-crew-workforce-optimization-ga`

These remain separate because the problem structures and encoding choices differ, even when the high-level solver family is evolutionary/metaheuristic.

## Learning-based and dynamic scheduling

| Repository | Main focus | Role in the series |
|---|---|---|
| `dqn-job-shop-scheduling` | Value-based RL for job-shop decisions | DQN scheduling |
| `job-shop-scheduling-ppo` | Policy-gradient scheduling | PPO scheduling |
| `reinforcement-learning-job-shop-scheduling-pytorch` | Research-oriented RL scheduling implementation | General RL scheduling laboratory |
| `job-shop-lib-rl-scheduling` | Scheduling through a dedicated RL/job-shop library stack | Framework-oriented experiment |
| `offline-rl-flexible-job-shop-scheduling` | Learning scheduling policies from logged trajectories | Offline RL scheduling |
| `neural-large-neighborhood-search-job-shop-scheduling-pytorch` | Learned improvement search around existing schedules | Neural LNS |
| `fjsp-ml-rescheduling` | ML-assisted rescheduling under changing conditions | Predictive/dynamic rescheduling |
| `adaptive-production-scheduling-python` | Adaptive production scheduling | Online/adaptive scheduling |
| `dynamic-automotive-paint-shop-scheduling-rl` | Dynamic paint-shop scheduling with RL | Domain-specific dynamic RL |
| `learning-augmented-online-machine-scheduling-python` | Online scheduling with learned predictions | Learning-augmented online algorithms |

## Why these repositories remain separate

CP-SAT, MILP, column generation, genetic algorithms, online algorithms, RL, offline RL, neural LNS, and ML-assisted rescheduling solve different algorithmic problems even when they share a scheduling application. Combining them into one repository would obscure rather than clarify those distinctions.

## Suggested reading order

1. `cp-sat-job-shop-scheduling`
2. `parallel-machine-scheduling-milp-optimization`
3. `paint-shop-scheduling-genetic-algorithm`
4. `reinforcement-learning-job-shop-scheduling-pytorch`
5. `offline-rl-flexible-job-shop-scheduling`
6. `neural-large-neighborhood-search-job-shop-scheduling-pytorch`
7. `fjsp-ml-rescheduling`
8. `learning-augmented-online-machine-scheduling-python`

The ordering is pedagogical rather than a ranking of methods.
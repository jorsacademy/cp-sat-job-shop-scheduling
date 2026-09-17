# Repository Overlap Audit — Job-Shop Scheduling

This document records overlap across the scheduling portfolio. It does not merge, archive, rename, or deprecate any repository.

## Status legend

- **Keep separate** — materially different formulation, algorithm, or research question.
- **Overlap but justified** — similar problem and some shared baselines, but a distinct implementation or evaluation goal.
- **Potential consolidation** — unusually high duplication; requires another review before any action.

## `cp-sat-job-shop-scheduling`

**Keep separate.**

Role: exact/constraint-programming benchmark using OR-Tools CP-SAT with interval variables, no-overlap constraints, release dates, tardiness options, lower bounds, and schedule validation.

This is the exact-optimization reference point for the family.

## `job-shop-scheduling-ppo`

**Overlap but justified.**

Role: compact event-driven JSSP MDP with Stable-Baselines3 PPO and classical dispatching-rule baselines.

Distinctive value: simple environment and off-the-shelf PPO make it a readable RL benchmark.

## `reinforcement-learning-job-shop-scheduling-pytorch`

**Overlap but justified.**

Role: from-scratch PyTorch PPO with masked Transformer actor-critic, exact objective-aligned reward, feasibility auditing, CP-SAT oracle, and tiny exhaustive verification.

This repository is substantially deeper than the compact Stable-Baselines3 project and should remain independent.

## `dqn-job-shop-scheduling`

**Keep separate.**

Role: DQN/TensorFlow implementation with replay buffer, target network, epsilon-greedy exploration, and action masking.

The algorithmic question is different from PPO.

## `job-shop-lib-rl-scheduling`

**Keep separate.**

Role: JobShopLib environment/baseline integration and RL-ready foundation on FT06. It intentionally stops before adding a second RL implementation.

## `offline-rl-flexible-job-shop-scheduling`

**Keep separate.**

Role: offline-RL/FJSP setting, which changes both the learning regime and problem class.

## `neural-large-neighborhood-search-job-shop-scheduling-pytorch`

**Keep separate.**

Role: learned improvement/neighborhood search rather than direct dispatch policy learning.

## `fjsp-ml-rescheduling`

**Keep separate.**

Role: ML-assisted rescheduling in a flexible/dynamic setting rather than static JSSP solution construction.

## `learning-augmented-online-machine-scheduling-python`

**Keep separate.**

Role: learning-augmented online algorithms; the research question is prediction-assisted algorithm design rather than RL scheduling.

## Audit conclusion

There is no current consolidation candidate in the Job-Shop family. The apparent duplication comes from using the same benchmark problem to study different solution paradigms:

`CP-SAT -> DQN -> PPO -> from-scratch Transformer PPO -> offline RL -> neural LNS -> ML rescheduling -> learning-augmented online algorithms`.

That methodological progression is useful portfolio structure and should be preserved.

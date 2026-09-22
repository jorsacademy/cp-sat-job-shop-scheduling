from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Dict, List, Sequence, Tuple


SHADE_NAMES = [
    "pure_white",
    "warm_white",
    "cool_white",
    "light_gray",
    "medium_gray",
    "dark_gray",
]


@dataclass(frozen=True)
class Job:
    job_id: str
    model_id: str
    shade: int
    due_position: int
    priority: int
    available_position: int


@dataclass(frozen=True)
class CostBreakdown:
    total_cost: float
    changeover_cost: float
    weighted_tardiness: float
    material_idle: float


@dataclass(frozen=True)
class GAConfig:
    population_size: int = 80
    generations: int = 150
    elite_size: int = 4
    tournament_size: int = 4
    mutation_rate: float = 0.35
    seed: int = 7
    weight_changeover: float = 4.0
    weight_tardiness: float = 2.0
    weight_material_idle: float = 1.0


def transition_time(from_job: Job, to_job: Job) -> int:
    """Return sequence-dependent paint-shop setup/cleaning time.

    Shade indices are ordered from light to dark. Moving from a darker shade to a
    lighter shade receives an additional cleaning penalty because contamination
    risk is assumed to be higher in that direction.
    """
    shade_distance = abs(from_job.shade - to_job.shade)
    if shade_distance == 0:
        return 0

    setup = 3 + 2 * shade_distance
    if from_job.shade > to_job.shade:
        setup += 4 + 2 * shade_distance
    return setup


def evaluate_schedule(schedule: Sequence[Job], config: GAConfig) -> CostBreakdown:
    """Evaluate a schedule using a compact industrial scheduling surrogate.

    The model penalizes three operational effects:
    1. shade-dependent paint changeovers and cleaning,
    2. lateness relative to downstream assembly demand,
    3. idle time caused by parts/material not being available when needed.

    One unit of processing time is assumed per job. This is an educational
    abstraction, not a calibrated model of a specific factory.
    """
    clock = 0
    changeover = 0.0
    tardiness = 0.0
    material_idle = 0.0

    for index, job in enumerate(schedule):
        if clock < job.available_position:
            material_idle += job.available_position - clock
            clock = job.available_position

        clock += 1
        tardiness += max(0, clock - job.due_position) * job.priority

        if index < len(schedule) - 1:
            setup = transition_time(job, schedule[index + 1])
            changeover += setup
            clock += setup

    total = (
        config.weight_changeover * changeover
        + config.weight_tardiness * tardiness
        + config.weight_material_idle * material_idle
    )
    return CostBreakdown(total, changeover, tardiness, material_idle)


def validate_permutation(schedule: Sequence[Job], reference_jobs: Sequence[Job]) -> None:
    expected = [job.job_id for job in reference_jobs]
    actual = [job.job_id for job in schedule]
    if len(actual) != len(expected):
        raise ValueError("Schedule length changed during optimization.")
    if set(actual) != set(expected):
        raise ValueError("Schedule is not a valid permutation of the input jobs.")
    if len(actual) != len(set(actual)):
        raise ValueError("Duplicate job IDs detected in schedule.")


def heuristic_schedule(jobs: Sequence[Job]) -> List[Job]:
    """Construct a strong deterministic seed schedule for the GA population."""
    return sorted(
        jobs,
        key=lambda job: (
            job.shade,
            job.due_position,
            -job.priority,
            job.available_position,
            job.job_id,
        ),
    )


def random_schedule(jobs: Sequence[Job], rng: random.Random) -> List[Job]:
    schedule = list(jobs)
    rng.shuffle(schedule)
    return schedule


def order_crossover(parent_a: Sequence[Job], parent_b: Sequence[Job], rng: random.Random) -> List[Job]:
    """Permutation-preserving Order Crossover (OX)."""
    if len(parent_a) != len(parent_b):
        raise ValueError("Parents must have the same length.")
    if len(parent_a) < 2:
        return list(parent_a)

    left, right = sorted(rng.sample(range(len(parent_a)), 2))
    child: List[Job | None] = [None] * len(parent_a)
    child[left:right] = parent_a[left:right]

    copied_ids = {job.job_id for job in parent_a[left:right]}
    remaining = [job for job in parent_b if job.job_id not in copied_ids]
    fill_positions = list(range(right, len(parent_a))) + list(range(0, left))

    for position, job in zip(fill_positions, remaining):
        child[position] = job

    return [job for job in child if job is not None]


def mutate(schedule: Sequence[Job], rng: random.Random, mutation_rate: float) -> List[Job]:
    """Apply either swap or inversion mutation while preserving the permutation."""
    child = list(schedule)
    if len(child) < 2 or rng.random() >= mutation_rate:
        return child

    left, right = sorted(rng.sample(range(len(child)), 2))
    if rng.random() < 0.5:
        child[left], child[right] = child[right], child[left]
    else:
        child[left : right + 1] = reversed(child[left : right + 1])
    return child


def tournament_select(
    population: Sequence[Sequence[Job]],
    scores: Sequence[float],
    rng: random.Random,
    tournament_size: int,
) -> List[Job]:
    candidates = rng.sample(range(len(population)), tournament_size)
    winner = min(candidates, key=lambda index: scores[index])
    return list(population[winner])


def optimize(jobs: Sequence[Job], config: GAConfig | None = None) -> Tuple[List[Job], CostBreakdown, List[float]]:
    """Optimize the paint-shop sequence with a permutation-based genetic algorithm."""
    if config is None:
        config = GAConfig()
    if not jobs:
        return [], CostBreakdown(0.0, 0.0, 0.0, 0.0), []
    if config.population_size < 2:
        raise ValueError("population_size must be at least 2.")
    if config.elite_size < 1 or config.elite_size >= config.population_size:
        raise ValueError("elite_size must be between 1 and population_size - 1.")
    if config.tournament_size < 2 or config.tournament_size > config.population_size:
        raise ValueError("Invalid tournament_size.")

    rng = random.Random(config.seed)

    population: List[List[Job]] = [heuristic_schedule(jobs)]
    while len(population) < config.population_size:
        population.append(random_schedule(jobs, rng))

    best_schedule = list(population[0])
    best_cost = evaluate_schedule(best_schedule, config)
    history: List[float] = []

    for _ in range(config.generations):
        costs = [evaluate_schedule(candidate, config) for candidate in population]
        scores = [cost.total_cost for cost in costs]

        generation_best_index = min(range(len(population)), key=lambda index: scores[index])
        generation_best = costs[generation_best_index]
        if generation_best.total_cost < best_cost.total_cost:
            best_cost = generation_best
            best_schedule = list(population[generation_best_index])

        history.append(best_cost.total_cost)

        elite_indices = sorted(range(len(population)), key=lambda index: scores[index])[: config.elite_size]
        next_population = [list(population[index]) for index in elite_indices]

        while len(next_population) < config.population_size:
            parent_a = tournament_select(population, scores, rng, config.tournament_size)
            parent_b = tournament_select(population, scores, rng, config.tournament_size)
            child = order_crossover(parent_a, parent_b, rng)
            child = mutate(child, rng, config.mutation_rate)
            validate_permutation(child, jobs)
            next_population.append(child)

        population = next_population

    validate_permutation(best_schedule, jobs)
    return best_schedule, best_cost, history


def generate_demo_jobs(
    catalog_models: int = 756,
    daily_jobs: int = 500,
    active_fraction: float = 0.72,
    seed: int = 42,
) -> List[Job]:
    """Create synthetic educational data resembling a large appliance model mix.

    The catalog may contain hundreds of models, while only a subset is active in
    a planning horizon. Production frequencies follow a long-tail distribution.
    Each physical production order receives a unique job ID even when multiple
    units belong to the same model.
    """
    rng = random.Random(seed)
    all_models = [f"MODEL_{index:04d}" for index in range(1, catalog_models + 1)]
    active_count = max(1, int(catalog_models * active_fraction))
    active_models = rng.sample(all_models, active_count)

    model_weights = [1.0 / ((rank + 5) ** 0.72) for rank in range(active_count)]
    weight_sum = sum(model_weights)
    model_weights = [weight / weight_sum for weight in model_weights]

    model_shades: Dict[str, int] = {}
    for model in active_models:
        model_shades[model] = rng.choices(
            range(len(SHADE_NAMES)),
            weights=[34, 24, 18, 11, 8, 5],
            k=1,
        )[0]

    jobs: List[Job] = []
    for index in range(1, daily_jobs + 1):
        model = rng.choices(active_models, weights=model_weights, k=1)[0]
        priority = rng.choices([1, 2, 3], weights=[68, 24, 8], k=1)[0]
        due_position = rng.randint(max(15, daily_jobs // 5), daily_jobs + daily_jobs // 3)
        available_position = rng.randint(0, max(5, daily_jobs // 10))
        if priority == 3:
            available_position = max(0, available_position - daily_jobs // 50)

        jobs.append(
            Job(
                job_id=f"JOB_{index:05d}",
                model_id=model,
                shade=model_shades[model],
                due_position=due_position,
                priority=priority,
                available_position=available_position,
            )
        )

    return jobs

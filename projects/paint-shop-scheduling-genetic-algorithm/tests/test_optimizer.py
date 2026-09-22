import unittest

from src.paint_shop_ga import (
    GAConfig,
    evaluate_schedule,
    generate_demo_jobs,
    heuristic_schedule,
    optimize,
    order_crossover,
)
import random


class PaintShopOptimizerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.jobs = generate_demo_jobs(catalog_models=80, daily_jobs=120, seed=101)

    def test_order_crossover_preserves_permutation(self) -> None:
        rng = random.Random(10)
        parent_a = list(self.jobs)
        parent_b = list(reversed(self.jobs))
        child = order_crossover(parent_a, parent_b, rng)
        self.assertEqual(len(child), len(self.jobs))
        self.assertEqual(
            {job.job_id for job in child},
            {job.job_id for job in self.jobs},
        )
        self.assertEqual(len(child), len({job.job_id for job in child}))

    def test_optimizer_preserves_every_job_exactly_once(self) -> None:
        config = GAConfig(population_size=30, generations=40, seed=11)
        best, _, _ = optimize(self.jobs, config)
        self.assertEqual(
            [job.job_id for job in sorted(best, key=lambda x: x.job_id)],
            [job.job_id for job in sorted(self.jobs, key=lambda x: x.job_id)],
        )

    def test_optimizer_does_not_return_worse_than_seed_heuristic(self) -> None:
        config = GAConfig(population_size=30, generations=50, seed=12)
        baseline = heuristic_schedule(self.jobs)
        baseline_cost = evaluate_schedule(baseline, config).total_cost
        _, optimized_cost, _ = optimize(self.jobs, config)
        self.assertLessEqual(optimized_cost.total_cost, baseline_cost)

    def test_reproducibility_with_fixed_seed(self) -> None:
        config = GAConfig(population_size=25, generations=30, seed=19)
        schedule_a, cost_a, _ = optimize(self.jobs, config)
        schedule_b, cost_b, _ = optimize(self.jobs, config)
        self.assertEqual(cost_a.total_cost, cost_b.total_cost)
        self.assertEqual(
            [job.job_id for job in schedule_a],
            [job.job_id for job in schedule_b],
        )


if __name__ == "__main__":
    unittest.main()

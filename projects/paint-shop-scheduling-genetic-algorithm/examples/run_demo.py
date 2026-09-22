from src.paint_shop_ga import (
    GAConfig,
    SHADE_NAMES,
    evaluate_schedule,
    generate_demo_jobs,
    heuristic_schedule,
    optimize,
)


def main() -> None:
    jobs = generate_demo_jobs(catalog_models=756, daily_jobs=500, seed=42)
    config = GAConfig(population_size=80, generations=150, seed=7)

    baseline = heuristic_schedule(jobs)
    baseline_cost = evaluate_schedule(baseline, config)

    best_schedule, best_cost, history = optimize(jobs, config)

    improvement = 100.0 * (baseline_cost.total_cost - best_cost.total_cost) / baseline_cost.total_cost

    print("Paint Shop Scheduling Optimization")
    print("=================================")
    print(f"Jobs in planning horizon : {len(jobs)}")
    print(f"Baseline total cost      : {baseline_cost.total_cost:.2f}")
    print(f"Optimized total cost     : {best_cost.total_cost:.2f}")
    print(f"Improvement              : {improvement:.2f}%")
    print(f"Changeover time          : {best_cost.changeover_cost:.2f}")
    print(f"Weighted tardiness       : {best_cost.weighted_tardiness:.2f}")
    print(f"Material idle            : {best_cost.material_idle:.2f}")
    print(f"Best-so-far iterations   : {len(history)}")
    print()
    print("First 25 optimized jobs:")

    for position, job in enumerate(best_schedule[:25], start=1):
        print(
            f"{position:03d} | {job.job_id} | {job.model_id} | "
            f"{SHADE_NAMES[job.shade]} | due={job.due_position} | "
            f"priority={job.priority} | available={job.available_position}"
        )


if __name__ == "__main__":
    main()

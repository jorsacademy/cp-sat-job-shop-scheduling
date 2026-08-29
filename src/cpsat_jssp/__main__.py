from __future__ import annotations

import argparse
import json

from .experiment import run_demo


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Solve a job-shop scheduling instance with OR-Tools CP-SAT."
    )
    parser.add_argument("--time-limit", type=float, default=10.0)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--makespan-weight", type=int, default=10)
    parser.add_argument("--tardiness-weight", type=int, default=1)
    args = parser.parse_args()
    print(
        json.dumps(
            run_demo(
                time_limit=args.time_limit,
                workers=args.workers,
                seed=args.seed,
                makespan_weight=args.makespan_weight,
                tardiness_weight=args.tardiness_weight,
            ),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()

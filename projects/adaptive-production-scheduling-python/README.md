# Adaptive Production Scheduling Python

A disruption-aware production scheduling heuristic for manufacturing experiments. The project combines exponential-smoothing demand forecasting, stochastic machine availability, weighted product priorities, capacity-aware allocation, utilization tracking, and operational KPI reporting.

> **License:** Source-available for personal, educational, academic, and non-profit research use only. **Commercial use is prohibited** unless you obtain a separate written license from the copyright holder. See [`LICENSE`](LICENSE).

## What this project does

The scheduler models products, dedicated machines, and shifts. At each shift it simulates maintenance/efficiency disruptions, applies a small bounded learning-curve adjustment, then allocates integer production quantities according to dynamic priority scores and available capacity.

This is a heuristic simulation model, not an exact MILP/CP optimizer. That distinction is intentional: it is designed for transparent experimentation with dynamic production conditions rather than proof of mathematical optimality.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -e ".[dev]"
```

## Run the example

```bash
python examples/basic_demo.py
```

## Run tests

```bash
pytest
ruff check .
```

## Core API

```python
from adaptive_scheduler import AdaptiveProductionScheduler, Machine, Product

products = [
    Product("Smartphone", margin=300, priority=1),
    Product("Tablet", margin=200, priority=2),
]

machines = [
    Machine("Machine_A", base_capacity=30, product_type="Smartphone"),
    Machine("Machine_B", base_capacity=20, product_type="Tablet"),
]

scheduler = AdaptiveProductionScheduler(
    products,
    machines,
    shifts=["Morning", "Afternoon", "Night"],
    seed=42,
)

result = scheduler.generate_schedule({"Smartphone": 100, "Tablet": 75})
print(result["kpis"])
```

## Design notes

- Randomness is isolated behind a scheduler-local seeded RNG so tests and experiments can be reproducible.
- `current_capacity` is preserved when explicitly supplied; otherwise it defaults to `base_capacity`.
- Production quantities are integer units and unmet demand is clamped at zero.
- The `available_machines` argument is honored by the allocation method instead of being silently ignored.
- Priority numbering follows the common convention that `1` means highest base priority.
- Timestamps are UTC-aware.

## CI

GitHub Actions runs Ruff and Pytest on Python 3.10, 3.11, 3.12, and 3.13 for pushes and pull requests targeting `main`.

## License

Copyright © 2026 jorsacademy. Commercial use is prohibited without a separate written license. See [`LICENSE`](LICENSE) for the controlling terms.

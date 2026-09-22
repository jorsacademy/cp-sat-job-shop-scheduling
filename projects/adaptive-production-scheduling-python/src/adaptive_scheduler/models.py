from __future__ import annotations

from dataclasses import dataclass, replace


@dataclass(slots=True)
class Machine:
    """Machine configuration and mutable shift capacity."""

    name: str
    base_capacity: int
    product_type: str
    current_capacity: int | None = None
    efficiency: float = 1.0
    maintenance_probability: float = 0.1
    downtime_duration: int = 1

    def __post_init__(self) -> None:
        if self.base_capacity < 0:
            raise ValueError("base_capacity must be non-negative")
        if self.current_capacity is None:
            self.current_capacity = self.base_capacity
        if self.current_capacity < 0:
            raise ValueError("current_capacity must be non-negative")
        if not 0 <= self.maintenance_probability <= 1:
            raise ValueError("maintenance_probability must be in [0, 1]")
        if self.downtime_duration < 1:
            raise ValueError("downtime_duration must be >= 1")

    def clone(self) -> "Machine":
        return replace(self)


@dataclass(frozen=True, slots=True)
class Product:
    """Product attributes used by the scheduling heuristic."""

    name: str
    margin: float
    priority: int
    setup_time: float = 0.0
    quality_threshold: float = 0.95

    def __post_init__(self) -> None:
        if self.margin < 0:
            raise ValueError("margin must be non-negative")
        if self.priority <= 0:
            raise ValueError("priority must be positive")
        if self.setup_time < 0:
            raise ValueError("setup_time must be non-negative")
        if not 0 <= self.quality_threshold <= 1:
            raise ValueError("quality_threshold must be in [0, 1]")

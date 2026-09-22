from __future__ import annotations

import csv
from pathlib import Path
from typing import List

from .core import Edge, TaskTimes


def load_tasks(path: str | Path) -> TaskTimes:
    with open(path, newline="", encoding="utf-8") as file:
        rows = csv.DictReader(file)
        return {
            row["task_id"].strip(): int(row["task_time_seconds"])
            for row in rows
        }


def load_precedence(path: str | Path) -> List[Edge]:
    with open(path, newline="", encoding="utf-8") as file:
        rows = csv.DictReader(file)
        return [
            (row["predecessor"].strip(), row["successor"].strip())
            for row in rows
        ]

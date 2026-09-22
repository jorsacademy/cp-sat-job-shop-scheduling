from __future__ import annotations

from typing import Mapping

import pandas as pd


def production_dataframe(schedule_result: Mapping) -> pd.DataFrame:
    """Return the production plan as a shift-by-product DataFrame."""
    return pd.DataFrame(schedule_result["production_plan"]).T


def utilization_dataframe(schedule_result: Mapping) -> pd.DataFrame:
    """Return machine utilization percentages as a shift-by-machine DataFrame."""
    return pd.DataFrame(schedule_result["machine_utilization"]).T

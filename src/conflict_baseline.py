import pandas as pd

from src.conflict_rolling_anomaly import compute_conflict_rolling_anomaly
from src.conflict_yoy_abs import compute_conflict_yoy_abs


def compute_conflict_baseline(method, monthly_conflict):

    # Normalize method (safety)
    method = method.upper()

    if method == "ROLLING_MEAN_6":
        df = compute_conflict_rolling_anomaly(monthly_conflict)

    elif method == "YOY_ABS":
        df = compute_conflict_yoy_abs(monthly_conflict)

    else:
        raise ValueError(
            f"Unknown conflict baseline method: {method}. "
            f"Allowed: ROLLING_MEAN_6, YOY_ABS"
        )

    # Ensure label consistency (in case transformation didn't set it)
    df["baseline_method"] = method

    return df
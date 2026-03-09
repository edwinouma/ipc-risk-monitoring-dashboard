# src/classification_utils.py

from src.config import INDICATOR_DIRECTION
import pandas as pd
import numpy as np


def validate_thresholds(indicator_value, alarm_threshold, alert_threshold):

    if indicator_value not in INDICATOR_DIRECTION:
        raise ValueError(
            f"{indicator_value} not found in INDICATOR_DIRECTION config."
        )

    direction = INDICATOR_DIRECTION[indicator_value]

    if direction == "lower" and alarm_threshold > alert_threshold:
        raise ValueError(
            f"{indicator_value}: For lower-tail indicators, "
            "alarm_threshold must be lower than alert_threshold."
        )

    if direction == "upper" and alarm_threshold < alert_threshold:
        raise ValueError(
            f"{indicator_value}: For upper-tail indicators, "
            "alarm_threshold must be higher than alert_threshold."
        )

    return direction


def classify_series(values, indicator_value, alarm_threshold, alert_threshold):

    direction = validate_thresholds(
        indicator_value,
        alarm_threshold,
        alert_threshold
    )

    if direction == "lower":
        return np.where(
            values <= alarm_threshold,
            "Alarm",
            np.where(
                values <= alert_threshold,
                "Alert",
                "Minimal"
            )
        )

    elif direction == "upper":
        return np.where(
            values >= alarm_threshold,
            "Alarm",
            np.where(
                values >= alert_threshold,
                "Alert",
                "Minimal"
            )
        )

    else:
        raise ValueError(
            f"Unknown direction '{direction}' for {indicator_value}"
        )
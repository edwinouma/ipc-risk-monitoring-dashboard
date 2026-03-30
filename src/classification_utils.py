# src/classification_utils.py

from src.config import (
    INDICATOR_DIRECTION,
    INDICATOR_METHOD,
    CONFLICT_USE_COMBINED,
    CONFLICT_COMBINED_RULES
)
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

    method = INDICATOR_METHOD.get(indicator_value, "percentile")
    # ---------------------------------------------------
    # 1A. COMBINED CONFLICT LOGIC (events + fatalities)
    # ---------------------------------------------------
    if method == "event_combined" and CONFLICT_USE_COMBINED:
        rules = CONFLICT_COMBINED_RULES.get(indicator_value)

        if rules is None:
            raise ValueError(f"No combined conflict rules defined for {indicator_value}")

        event_alert = rules["event_alert_threshold"]
        event_alarm = rules["event_alarm_threshold"]
        fatal_alarm = rules["fatality_alarm_threshold"]

        # values must contain both columns
        # values is expected to be a Series → treat as events
        events = values

        return np.where(
            pd.isna(events),
            "Missing",
            np.where(
                events >= event_alarm,
                "Alarm",
                np.where(
                    events >= event_alert,
                    "Alert",
                    "Minimal"
                )
            )
        )

    # ---------------------------------------------------
    # 1. EVENT-BASED LOGIC (conflict, flood occurrence)
    # ---------------------------------------------------
    if method in ["event", "event_combined"]:
        return np.where(
            pd.isna(values),
            "Missing",
            np.where(
                values >= alarm_threshold,
                "Alarm",
                np.where(
                    values >= alert_threshold,
                    "Alert",
                    "Minimal"
                )
            )
        )

    # ---------------------------------------------------
    # 2. DEFAULT DIRECTIONAL LOGIC
    # ---------------------------------------------------
    direction = validate_thresholds(
        indicator_value,
        alarm_threshold,
        alert_threshold
    )

    if direction == "lower":
        return np.where(
            pd.isna(values),
            "Minimal",  # 🔥 FIX HERE TOO
            np.where(
                values <= alarm_threshold,
                "Alarm",
                np.where(
                    values <= alert_threshold,
                    "Alert",
                    "Minimal"
                )
            )
        )

    if direction == "upper":

        return np.where(

            pd.isna(values),

            "Minimal",  # 🔥 FIX: treat missing as Minimal

            np.where(

                values >= alarm_threshold,

                "Alarm",

                np.where(

                    values >= alert_threshold,

                    "Alert",

                    "Minimal"

                )

            )

        )

    else:
        raise ValueError(
            f"Unknown direction '{direction}' for {indicator_value}"
        )
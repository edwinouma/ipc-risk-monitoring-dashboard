# src/classification_utils.py

from src.config import (
    INDICATOR_DIRECTION,
    INDICATOR_METHOD,
    CONFLICT_USE_COMBINED,
    CONFLICT_COMBINED_RULES
)
import pandas as pd
import numpy as np

from src.config import CLASSIFICATION_LABELS

alarm_label = CLASSIFICATION_LABELS["alarm"]
alert_label = CLASSIFICATION_LABELS["alert"]
minimal_label = CLASSIFICATION_LABELS["minimal"]
no_data_label = CLASSIFICATION_LABELS.get("no_data", "No data")

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
            no_data_label,
            np.where(
                events >= event_alarm,
                alarm_label,
                np.where(
                    events >= event_alert,
                    alert_label,
                    minimal_label
                )
            )
        )

    # ---------------------------------------------------
    # 1. EVENT-BASED LOGIC (conflict, flood occurrence)
    # ---------------------------------------------------
    if method in ["event", "event_combined"]:
        return np.where(
            pd.isna(values),
            no_data_label,
            np.where(
                values >= alarm_threshold,
                alarm_label,
                np.where(
                    values >= alert_threshold,
                    alert_label,
                    minimal_label
                )
            )
        )

    # ---------------------------------------------------
    # 1B. SPI LOGIC (DUAL TAIL: DROUGHT + FLOOD)
    # ---------------------------------------------------
    if method == "spi_true":
        # -----------------------------
        # Drought thresholds (from inputs)
        # -----------------------------
        drought_alarm = alarm_threshold
        drought_alert = alert_threshold

        # -----------------------------
        # Flood thresholds (standard SPI)
        # -----------------------------
        from src.config import SPI_TRUE_THRESHOLDS

        flood_cfg = SPI_TRUE_THRESHOLDS.get(
            indicator_value,
            SPI_TRUE_THRESHOLDS.get("default", {})
        )

        # Convert drought thresholds to positive side for flood
        flood_alert = abs(flood_cfg.get("alert", -1.0))
        flood_alarm = abs(flood_cfg.get("alarm", -2.0))

        return np.where(
            pd.isna(values),
            minimal_label,

            # -----------------------------
            # DROUGHT (lower tail)
            # -----------------------------
            np.where(
                values <= drought_alarm,
                alarm_label,
                np.where(
                    values <= drought_alert,
                    alert_label,

                    # -----------------------------
                    # FLOOD (upper tail)
                    # -----------------------------
                    np.where(
                        values >= flood_alarm,
                        alarm_label,
                        np.where(
                            values >= flood_alert,
                            alert_label,
                            minimal_label
                        )
                    )
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
            minimal_label,
            np.where(
                values <= alarm_threshold,
                alarm_label,
                np.where(
                    values <= alert_threshold,
                    alert_label,
                    minimal_label
                )
            )
        )

    if direction == "upper":
        return np.where(
            pd.isna(values),
            minimal_label,
            np.where(
                values >= alarm_threshold,
                alarm_label,
                np.where(
                    values >= alert_threshold,
                    alert_label,
                    minimal_label
                )
            )
        )

    else:
        raise ValueError(
            f"Unknown direction '{direction}' for {indicator_value}"
        )
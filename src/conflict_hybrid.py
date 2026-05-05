import pandas as pd
import numpy as np

from src.config import (
    EVENT_THRESHOLDS,
    CONFLICT_HYBRID_THRESHOLDS,
    CONFLICT_TREND_RULES,
    CONFLICT_ANOMALY_RULES
)


def classify_conflict_row(row, indicator, method):

    value = row.get("value")
    yoy = row.get("yoy_signal")
    yoy_ratio = row.get("yoy_ratio")
    anomaly = row.get("anomaly_signal")
    anomaly_ratio = row.get("anomaly_ratio")

    # -----------------------------------------
    # HANDLE NO DATA
    # -----------------------------------------
    if pd.isna(value):
        return "no_data"

    # -----------------------------------------
    # 1️⃣ CATEGORICAL METHOD
    # -----------------------------------------
    if method == "categorical":

        thresholds = EVENT_THRESHOLDS.get(indicator, {})
        if not thresholds:
            return "minimal"

        if value >= thresholds.get("alarm", np.inf):
            return "alarm"
        elif value >= thresholds.get("alert", np.inf):
            return "alert"
        else:
            return "minimal"

    # -----------------------------------------
    # 2️⃣ HYBRID METHOD
    # -----------------------------------------
    elif method == "hybrid":

        thresholds = CONFLICT_HYBRID_THRESHOLDS.get(indicator, {})
        trend_rules = CONFLICT_TREND_RULES.get(indicator, {})
        anomaly_rules = CONFLICT_ANOMALY_RULES.get(indicator, {})

        if not thresholds:
            return "minimal"

        # STEP 1: Base classification
        if value >= thresholds.get("alarm", np.inf):
            base = "alarm"
        elif value >= thresholds.get("alert", np.inf):
            base = "alert"
        else:
            base = "minimal"

        # STEP 2: YOY escalation
        if base == "alert" and trend_rules:

            if (
                (pd.notna(yoy) and yoy >= trend_rules["yoy_abs"]["alarm"]) or
                (pd.notna(yoy_ratio) and yoy_ratio >= trend_rules["yoy_ratio"]["alarm"])
            ):
                return "alarm"

            if (
                (pd.notna(yoy) and yoy >= trend_rules["yoy_abs"]["alert"]) or
                (pd.notna(yoy_ratio) and yoy_ratio >= trend_rules["yoy_ratio"]["alert"])
            ):
                base = "alert"

        # STEP 3: Anomaly escalation
        if base == "alert" and anomaly_rules:

            if (
                (pd.notna(anomaly) and anomaly >= anomaly_rules["anomaly_abs"]["alarm"]) or
                (pd.notna(anomaly_ratio) and anomaly_ratio >= anomaly_rules["anomaly_ratio"]["alarm"])
            ):
                return "alarm"

            if (
                (pd.notna(anomaly) and anomaly >= anomaly_rules["anomaly_abs"]["alert"]) or
                (pd.notna(anomaly_ratio) and anomaly_ratio >= anomaly_rules["anomaly_ratio"]["alert"])
            ):
                base = "alert"

        return base

    # -----------------------------------------
    # 3️⃣ PERCENTILE
    # -----------------------------------------
    elif method == "percentile":
        return None

    return "minimal"
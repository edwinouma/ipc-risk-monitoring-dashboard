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

    # -------------------------------------------------
    # HANDLE NO DATA
    # -------------------------------------------------
    if pd.isna(value):
        return "no_data"

    # -------------------------------------------------
    # 1️⃣ CATEGORICAL METHOD
    # -------------------------------------------------
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

    # -------------------------------------------------
    # 2️⃣ HYBRID METHOD
    # -------------------------------------------------
    elif method == "hybrid":

        thresholds = CONFLICT_HYBRID_THRESHOLDS.get(indicator, {})

        # 🔥 FIXED: GLOBAL RULES
        trend_rules = CONFLICT_TREND_RULES
        anomaly_rules = CONFLICT_ANOMALY_RULES

        if not thresholds:
            return "minimal"

        # -------------------------------------------------
        # STEP 1: BASE CLASSIFICATION
        # -------------------------------------------------
        if value >= thresholds.get("alarm", np.inf):
            base = "alarm"

        elif value >= thresholds.get("alert", np.inf):
            base = "alert"

        else:
            base = "minimal"

        # =================================================
        # STEP 2: YOY TREND ESCALATION
        # =================================================
        if trend_rules:

            # ---------------------------------------------
            # ALERT-LEVEL TREND
            # OR LOGIC (more sensitive)
            # ---------------------------------------------
            moderate_trend = (
                (
                    pd.notna(yoy)
                    and yoy >= trend_rules["yoy_abs"]["alert"]
                )
                or
                (
                    pd.notna(yoy_ratio)
                    and yoy_ratio >= trend_rules["yoy_ratio"]["alert"]
                )
            )

            # ---------------------------------------------
            # ALARM-LEVEL TREND
            # AND LOGIC (more conservative)
            # ---------------------------------------------
            extreme_trend = (
                (
                    pd.notna(yoy)
                    and yoy >= trend_rules["yoy_abs"]["alarm"]
                )
                and
                (
                    pd.notna(yoy_ratio)
                    and yoy_ratio >= trend_rules["yoy_ratio"]["alarm"]
                )
            )

            # ---------------------------------------------
            # ESCALATION RULES
            # ---------------------------------------------
            if base == "alert" and extreme_trend:
                return "alarm"

            elif base == "minimal" and moderate_trend:
                base = "alert"

        # =================================================
        # STEP 3: ANOMALY ESCALATION
        # =================================================
        if anomaly_rules:

            # ---------------------------------------------
            # ALERT-LEVEL ANOMALY
            # OR LOGIC
            # ---------------------------------------------
            moderate_anomaly = (
                (
                    pd.notna(anomaly)
                    and anomaly >= anomaly_rules["anomaly_abs"]["alert"]
                )
                or
                (
                    pd.notna(anomaly_ratio)
                    and anomaly_ratio >= anomaly_rules["anomaly_ratio"]["alert"]
                )
            )

            # ---------------------------------------------
            # ALARM-LEVEL ANOMALY
            # AND LOGIC
            # ---------------------------------------------
            extreme_anomaly = (
                (
                    pd.notna(anomaly)
                    and anomaly >= anomaly_rules["anomaly_abs"]["alarm"]
                )
                and
                (
                    pd.notna(anomaly_ratio)
                    and anomaly_ratio >= anomaly_rules["anomaly_ratio"]["alarm"]
                )
            )

            # ---------------------------------------------
            # ESCALATION RULES
            # ---------------------------------------------
            if base == "alert" and extreme_anomaly:
                return "alarm"

            elif base == "minimal" and moderate_anomaly:
                base = "alert"

        return base

    # -------------------------------------------------
    # 3️⃣ PERCENTILE
    # -------------------------------------------------
    elif method == "percentile":

        # Placeholder until implemented
        return "minimal"

    # -------------------------------------------------
    # DEFAULT FALLBACK
    # -------------------------------------------------
    return "minimal"
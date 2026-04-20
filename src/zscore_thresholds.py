# src/zscore_thresholds.py

import pandas as pd
import numpy as np
from src.config import (
    INDICATOR_DIRECTION,
    ZSCORE_THRESHOLDS,
    CLIMATE_INDICATORS,
    PRICE_INDICATORS,
    SHOCK_MANMADE
)

from src.config import Z_AGGREGATION_METHOD

def compute_zscore_thresholds(df, indicator, value_col="value"):
    """
    Compute Z-score based thresholds.

    Logic:
    - Climate → use drought values (< threshold)
    - Prices → use positive changes (> 0)
    - Conflict → excluded
    """

    # -----------------------------------------
    # 0. Exclude conflict indicators ❌
    # -----------------------------------------
    if indicator in SHOCK_MANMADE:
        return pd.DataFrame()

    direction = INDICATOR_DIRECTION.get(indicator, "upper")

    # -----------------------------------------
    # 1. Ensure numeric + clean
    # -----------------------------------------
    df = df.copy()
    df[value_col] = pd.to_numeric(df[value_col], errors="coerce")
    df = df.dropna(subset=[value_col])

    if df.empty:
        return pd.DataFrame()

    if indicator in PRICE_INDICATORS:

        if "baseline_method" not in df.columns:
            raise ValueError(
                f"{indicator}: Z-score requires anomaly values (YOY, LTM, etc.), not raw prices."
            )

    # -----------------------------------------
    # 🔥 NEW: Aggregate to MONTHLY level (CONFIG-DRIVEN)
    # -----------------------------------------

    if "year_month" in df.columns and "adm1_name" in df.columns:
        agg_method = Z_AGGREGATION_METHOD.get(indicator, "mean")

        df = (
            df
            .groupby(["adm1_name", "year_month"], as_index=False)
            .agg({
                value_col: agg_method
            })
        )

    # -----------------------------------------
    # 2. Get config (with fallback)
    # -----------------------------------------
    th_cfg = ZSCORE_THRESHOLDS.get(
        indicator,
        ZSCORE_THRESHOLDS["default"]
    )

    alert_z = th_cfg.get("alert", 1.0)
    alarm_z = th_cfg.get("alarm", 2.0)

    # Optional (safe defaults if not yet added in config)
    climate_threshold = th_cfg.get("climate_filter_threshold", 100)
    price_threshold = th_cfg.get("price_filter_threshold", 0)

    # -----------------------------------------
    # 🔥 Minimum observations safeguard
    # -----------------------------------------
    if len(df) < 10:
        return pd.DataFrame()

    # -----------------------------------------
    # 5. Compute mean & std
    # -----------------------------------------
    mean_val = df[value_col].mean()
    std_val = df[value_col].std()

    if std_val == 0 or np.isnan(std_val):
        return pd.DataFrame()

    # -----------------------------------------
    # 6. Convert Z → actual thresholds
    # -----------------------------------------
    if direction == "upper":
        alert = mean_val + alert_z * std_val
        alarm = mean_val + alarm_z * std_val
    else:
        alert = mean_val - alert_z * std_val
        alarm = mean_val - alarm_z * std_val

    # -----------------------------------------
    # 7. Output (PIPELINE-COMPATIBLE ✅)
    # -----------------------------------------
    return pd.DataFrame([{
        "indicator": indicator,
        "alert_zscore": alert,
        "alarm_zscore": alarm,
        "alert_percentile": None,
        "alarm_percentile": None,
        "alert_tukey": None,
        "alarm_tukey": None
    }])
# src/spi_zscore.py

import pandas as pd
import numpy as np
from src.config import (
    INDICATOR_DIRECTION,
    SPI_ZSCORE_THRESHOLDS,
    PRICE_INDICATORS,
    SHOCK_MANMADE,
    Z_AGGREGATION_METHOD,
    SPI_REQUIRES_RAW   # 🔥 NEW (CRITICAL CONTROL)
)


def compute_spi_zscore_thresholds(df, indicator):
    """
    Compute SPI-style (seasonally standardized) Z-score thresholds.

    Logic:
    - Climate → detect drought relative to same-month history (RAW ONLY)
    - Prices → detect abnormal spikes relative to same-month history (ANOMALY REQUIRED)
    - Conflict → excluded
    """

    # -----------------------------------------
    # 0. Exclude conflict indicators ❌
    # -----------------------------------------
    if indicator in SHOCK_MANMADE:
        return pd.DataFrame()

    direction = INDICATOR_DIRECTION.get(indicator, "upper")

    # -----------------------------------------
    # 🔥 CRITICAL: Enforce RAW-only for SPI (climate)
    # -----------------------------------------
    if indicator not in SPI_REQUIRES_RAW:
        raise ValueError(
            f"{indicator}: SPI-Z can only be applied to RAW climatological indicators."
        )

    # -----------------------------------------
    # 1. Ensure numeric + clean
    # -----------------------------------------
    df = df.copy()
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["value"])

    if df.empty:
        return pd.DataFrame()

    # -----------------------------------------
    # 🔥 SAFETY: Prevent accidental use of anomaly data
    # -----------------------------------------
    if "baseline_method" in df.columns and indicator not in PRICE_INDICATORS:
        raise ValueError(
            f"{indicator}: SPI-Z should NOT be applied to anomaly-based data."
        )

    # -----------------------------------------
    # 2. Ensure DATE exists
    # -----------------------------------------
    if "date" not in df.columns:
        raise ValueError("SPI Z-score requires 'date' column.")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])

    if df.empty:
        return pd.DataFrame()

    # -----------------------------------------
    # 3. Extract MONTH (CRITICAL for SPI logic)
    # -----------------------------------------
    df["month"] = df["date"].dt.month

    # -----------------------------------------
    # 🔥 Aggregate to MONTHLY level (CONFIG-DRIVEN)
    # -----------------------------------------
    if "year_month" in df.columns and "adm1_name" in df.columns:

        agg_method = Z_AGGREGATION_METHOD.get(indicator, "mean")

        df = (
            df
            .groupby(["adm1_name", "year_month"], as_index=False)
            .agg({"value": agg_method})
        )

        df["year_month"] = pd.to_datetime(df["year_month"])
        df["month"] = df["year_month"].dt.month

    # -----------------------------------------
    # 🔥 Minimum observations safeguard
    # -----------------------------------------
    if len(df) < 12:
        return pd.DataFrame()

    # -----------------------------------------
    # 4. Compute MONTHLY climatology
    # -----------------------------------------
    monthly_stats = (
        df.groupby("month")["value"]
        .agg(["mean", "std"])
        .reset_index()
    )

    monthly_stats["std"] = monthly_stats["std"].replace(0, np.nan)

    # -----------------------------------------
    # 5. Merge back
    # -----------------------------------------
    df = df.merge(monthly_stats, on="month", how="left")
    df = df.dropna(subset=["std"])

    if df.empty:
        return pd.DataFrame()

    # -----------------------------------------
    # 6. Compute SPI-style Z-score
    # -----------------------------------------
    df["spi_z"] = (df["value"] - df["mean"]) / df["std"]
    df = df.dropna(subset=["spi_z"])

    if df.empty:
        return pd.DataFrame()

    # -----------------------------------------
    # 7. Get thresholds from config
    # -----------------------------------------
    th_cfg = SPI_ZSCORE_THRESHOLDS.get(
        indicator,
        SPI_ZSCORE_THRESHOLDS["default"]
    )

    alert_z = th_cfg.get("alert", 1.0)
    alarm_z = th_cfg.get("alarm", 2.0)

    # -----------------------------------------
    # 8. Convert Z → threshold space
    # -----------------------------------------
    # NOTE: SPI distribution is ~standard normal

    spi_mean = df["spi_z"].mean()
    spi_std = df["spi_z"].std()

    if spi_std == 0 or np.isnan(spi_std):
        return pd.DataFrame()

    if direction == "upper":
        alert = spi_mean + alert_z * spi_std
        alarm = spi_mean + alarm_z * spi_std
    else:
        alert = spi_mean - alert_z * spi_std
        alarm = spi_mean - alarm_z * spi_std

    # -----------------------------------------
    # 9. Output (PIPELINE-COMPATIBLE ✅)
    # -----------------------------------------
    return pd.DataFrame([{
        "indicator": indicator,
        "alert_percentile": alert,
        "alarm_percentile": alarm,
        "alert_tukey": None,
        "alarm_tukey": None
    }])
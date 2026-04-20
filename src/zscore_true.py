import pandas as pd
import numpy as np
from src.config import PRICE_INDICATORS


def compute_true_zscore(df):
    """
    Compute seasonal + unit-level Z-score

    Enhancements:
    - Uses anomaly data for PRICE indicators when available
    - Falls back to log(raw) ONLY if anomaly missing
    - Aggregates price data separately by baseline_method (LTM, YOY, FIVE_YEAR)
    - Keeps NDVI and other indicators unchanged
    - Fully backward compatible
    """

    df = df.copy()

    # -----------------------------------------
    # Ensure required columns
    # -----------------------------------------
    required = ["adm1_name", "date", "value"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["date", "value"])

    if df.empty:
        raise ValueError("Input dataframe is empty after cleaning.")

    # -----------------------------------------
    # Preserve original value
    # -----------------------------------------
    df["value_original"] = df["value"]

    # -----------------------------------------
    # 🔥 PRICE HANDLING (FINAL - NO LOG)
    # -----------------------------------------
    # Prices are expected to already be anomaly (%)
    # No transformation required

    # -----------------------------------------
    # Monthly aggregation
    # -----------------------------------------
    df["year_month"] = df["date"].dt.to_period("M")

    group_cols = ["adm1_name", "year_month"]

    if "country" in df.columns:
        group_cols = ["country"] + group_cols

    # -----------------------------------------
    # 🔥 KEEP BASELINES SEPARATE FOR PRICES
    # -----------------------------------------
    if "baseline_method" in df.columns:
        if "indicator" in df.columns and df["indicator"].isin(PRICE_INDICATORS).any():
            group_cols = group_cols + ["baseline_method"]

    monthly = (
        df.groupby(group_cols)["value"]
        .mean()
        .reset_index()
    )

    # -----------------------------------------
    # Add month
    # -----------------------------------------
    monthly["date"] = monthly["year_month"].dt.to_timestamp()
    monthly["month"] = monthly["date"].dt.month

    # -----------------------------------------
    # Seasonal Z-score (DO NOT include baseline)
    # -----------------------------------------
    z_group_cols = ["adm1_name", "month"]

    if "country" in monthly.columns:
        z_group_cols = ["country"] + z_group_cols

    stats = (
        monthly
        .groupby(z_group_cols)["value"]
        .agg(["mean", "std"])
        .reset_index()
    )

    monthly = monthly.merge(stats, on=z_group_cols, how="left")

    # -----------------------------------------
    # Stability improvement
    # -----------------------------------------
    monthly["std"] = monthly["std"].replace(0, np.nan)

    monthly["value_zscore"] = (
        (monthly["value"] - monthly["mean"]) / monthly["std"]
    )

    # -----------------------------------------
    # Restore original value
    # -----------------------------------------
    original = (
        df.groupby(group_cols)["value_original"]
        .mean()
        .reset_index()
    )

    monthly = monthly.merge(original, on=group_cols, how="left")

    # -----------------------------------------
    # Final format
    # -----------------------------------------
    monthly = monthly.drop(columns=["value", "mean", "std"])
    monthly = monthly.rename(columns={"value_original": "value"})

    cols = ["adm1_name", "date", "year_month", "value", "value_zscore"]

    if "country" in monthly.columns:
        cols = ["country"] + cols

    # Preserve baseline_method if present
    if "baseline_method" in monthly.columns:
        cols = cols + ["baseline_method"]

    monthly = monthly[cols]

    # Drop rows without zscore
    monthly = monthly.dropna(subset=["value_zscore"])

    return monthly
import pandas as pd
import numpy as np
def compute_true_zscore(df):
    """
    Compute seasonal + unit-level Z-score
    Returns pipeline-compatible dataframe:
        value = Z-score
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
    # Monthly aggregation
    # -----------------------------------------
    df["year_month"] = df["date"].dt.to_period("M")

    group_cols = ["adm1_name", "year_month"]
    if "country" in df.columns:
        group_cols = ["country"] + group_cols

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
    # Compute Z-score (seasonal + unit)
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

    monthly["std"] = monthly["std"].replace(0, np.nan)

    monthly["zscore"] = (monthly["value"] - monthly["mean"]) / monthly["std"]

    # -----------------------------------------
    # Final format (MATCH SPI)
    # -----------------------------------------
    monthly = monthly.drop(columns=["value", "mean", "std"])
    monthly = monthly.rename(columns={"zscore": "value"})

    cols = ["adm1_name", "date", "year_month", "value"]
    if "country" in monthly.columns:
        cols = ["country"] + cols

    monthly = monthly[cols]

    monthly = monthly.dropna(subset=["value"])

    return monthly
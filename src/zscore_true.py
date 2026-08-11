import pandas as pd
import numpy as np
from src.config import PRICE_INDICATORS


def compute_true_zscore(df):
    print("\n==============================")
    print("TRUE_ZSCORE VERSION LOADED")
    print(__file__)
    print("==============================")

    """
    Compute seasonal + unit-level Z-score

    Enhancements
    ------------
    - Accepts both 'date' and 'year_month'
    - Supports raw and anomaly datasets
    - Preserves baseline_method throughout
    - Computes seasonal statistics separately
      for each baseline method
    - Fully backward compatible
    """

    df = df.copy()

    # --------------------------------------------------
    # Required columns
    # --------------------------------------------------
    required = ["adm1_name", "value"]

    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")

    # --------------------------------------------------
    # Build date column if only year_month exists
    # --------------------------------------------------
    if (
        "date" not in df.columns
        or df["date"].isna().all()
    ):

        if "year_month" in df.columns:

            df["date"] = pd.to_datetime(
                df["year_month"].astype(str),
                format="%Y-%m",
                errors="coerce"
            )

        else:

            raise ValueError(
                "Input dataframe must contain either "
                "'date' or 'year_month'."
            )

    else:

        df["date"] = pd.to_datetime(
            df["date"],
            errors="coerce"
        )

    # --------------------------------------------------
    # Numeric values
    # --------------------------------------------------
    df["value"] = pd.to_numeric(
        df["value"],
        errors="coerce"
    )

    print("Rows before cleaning :", len(df))
    print("Missing date         :", df["date"].isna().sum())
    print("Missing value        :", df["value"].isna().sum())

    df = df.dropna(subset=["date", "value"])

    print("Rows after cleaning  :", len(df))

    if df.empty:
        raise ValueError("Input dataframe is empty after cleaning.")

    # --------------------------------------------------
    # Preserve original value
    # --------------------------------------------------
    df["value_original"] = df["value"]

    # --------------------------------------------------
    # Monthly aggregation
    # --------------------------------------------------
    df["year_month"] = df["date"].dt.to_period("M")

    group_cols = ["adm1_name", "year_month"]

    if "country" in df.columns:
        group_cols = ["country"] + group_cols

    if "baseline_method" in df.columns:
        group_cols.append("baseline_method")

    monthly = (
        df.groupby(group_cols)["value"]
        .mean()
        .reset_index()
    )

    # --------------------------------------------------
    # Month
    # --------------------------------------------------
    monthly["date"] = monthly["year_month"].dt.to_timestamp()

    monthly["month"] = monthly["date"].dt.month

    # --------------------------------------------------
    # Seasonal statistics
    # IMPORTANT:
    # Compute mean/std separately for each baseline
    # --------------------------------------------------
    z_group_cols = ["adm1_name", "month"]

    if "country" in monthly.columns:
        z_group_cols = ["country"] + z_group_cols

    if "baseline_method" in monthly.columns:
        z_group_cols.append("baseline_method")

    stats = (
        monthly
        .groupby(z_group_cols)["value"]
        .agg(["mean", "std"])
        .reset_index()
    )

    monthly = monthly.merge(
        stats,
        on=z_group_cols,
        how="left"
    )

    # --------------------------------------------------
    # Compute Z-score
    # --------------------------------------------------
    monthly["std"] = monthly["std"].replace(0, np.nan)

    monthly["value_zscore"] = (
        (monthly["value"] - monthly["mean"])
        / monthly["std"]
    )

    # --------------------------------------------------
    # Restore original values
    # --------------------------------------------------
    original = (
        df.groupby(group_cols)["value_original"]
        .mean()
        .reset_index()
    )

    monthly = monthly.merge(
        original,
        on=group_cols,
        how="left"
    )

    # --------------------------------------------------
    # Final formatting
    # --------------------------------------------------
    monthly = monthly.drop(
        columns=[
            "value",
            "mean",
            "std"
        ]
    )

    monthly = monthly.rename(
        columns={
            "value_original": "value"
        }
    )

    cols = [
        "adm1_name",
        "date",
        "year_month",
        "value",
        "value_zscore"
    ]

    if "country" in monthly.columns:
        cols = ["country"] + cols

    if "baseline_method" in monthly.columns:
        cols.append("baseline_method")

    monthly = monthly[cols]

    # --------------------------------------------------
    # Remove rows where Z-score cannot be computed
    # --------------------------------------------------
    monthly = monthly.dropna(
        subset=["value_zscore"]
    )

    return monthly
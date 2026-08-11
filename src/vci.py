"""
==============================================================
Vegetation Condition Index (VCI)
==============================================================

Computes the Vegetation Condition Index (VCI) from historical
NDVI observations.

Method
------
For each administrative unit (ADM1) and calendar month:

    VCI = ((NDVI - NDVI_min) /
           (NDVI_max - NDVI_min)) * 100

where

    NDVI_min = historical minimum NDVI
    NDVI_max = historical maximum NDVI

The historical climatology is computed separately for each
calendar month (January, February, ..., December) to remove
seasonality.

Pipeline
--------
Raw NDVI
    ↓
Aggregate to monthly ADM1
    ↓
Compute monthly climatology
    ↓
Compute VCI
    ↓
Clip to [0,100]

Notes
-----
• Consistent with the RAAp seasonal methods.
• Uses monthly aggregation prior to climatology.
• Handles division-by-zero safely.
• Requires a minimum number of historical years.

Author : IPC RAAp
==============================================================
"""

import numpy as np
import pandas as pd

from src.config import (
    Z_AGGREGATION_METHOD,
    VCI_MIN_OBSERVATIONS
)


def compute_vci(
    df,
    indicator,
    value_col="value"
):
    """
    Compute Vegetation Condition Index (VCI).

    Parameters
    ----------
    df : pandas.DataFrame

        Required columns

            adm1_name
            year_month
            value_col

    indicator : str

        Indicator name.

    value_col : str, default="value"

        NDVI column.

    Returns
    -------
    pandas.DataFrame

    Original dataframe plus

        month
        ndvi_min
        ndvi_max
        vci
    """

    # ----------------------------------------------------------
    # Copy dataframe
    # ----------------------------------------------------------

    df = df.copy()

    # ----------------------------------------------------------
    # Validate required columns
    # ----------------------------------------------------------

    required = {
        "adm1_name",
        "year_month",
        value_col
    }

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    # ----------------------------------------------------------
    # Create working date column
    #
    # Preserve the original year_month field exactly as it is.
    # This keeps VCI fully compatible with the rest of the
    # RAAp pipeline, where year_month is used as a merge key.
    # ----------------------------------------------------------

    if pd.api.types.is_period_dtype(df["year_month"]):

        df["date"] = (
            df["year_month"]
            .dt.to_timestamp()
        )

    else:

        df["date"] = pd.to_datetime(
            df["year_month"]
        )

    # ----------------------------------------------------------
    # Ensure numeric NDVI
    # ----------------------------------------------------------

    df[value_col] = pd.to_numeric(
        df[value_col],
        errors="coerce"
    )

    df = df.dropna(
        subset=[
            "adm1_name",
            "year_month",
            value_col
        ]
    )

    if df.empty:
        return df

    # ----------------------------------------------------------
    # Aggregate to monthly level
    #
    # Uses the same aggregation rules as the other
    # seasonal methods in RAAp.
    # ----------------------------------------------------------

    agg_method = Z_AGGREGATION_METHOD.get(
        indicator,
        "mean"
    )

    df = (
        df
        .groupby(
            [
                "adm1_name",
                "year_month"
            ],
            as_index=False
        )
        .agg({
            value_col: agg_method
        })
    )

    # ----------------------------------------------------------
    # Extract year and calendar month
    # ----------------------------------------------------------

    df["year"] = df["year_month"].dt.year
    df["month"] = df["year_month"].dt.month

    # ----------------------------------------------------------
    # Count number of historical years
    # ----------------------------------------------------------

    counts = (
        df.groupby(
            [
                "adm1_name",
                "month"
            ]
        )["year"]
        .nunique()
        .reset_index(name="n")
    )

    # ----------------------------------------------------------
    # Monthly climatology
    # ----------------------------------------------------------

    climatology = (
        df.groupby(
            [
                "adm1_name",
                "month"
            ]
        )[value_col]
        .agg(
            ndvi_min="min",
            ndvi_max="max"
        )
        .reset_index()
    )

    climatology = climatology.merge(
        counts,
        on=[
            "adm1_name",
            "month"
        ],
        how="left"
    )

    # ----------------------------------------------------------
    # Keep only climatologies with sufficient history
    # ----------------------------------------------------------

    climatology = climatology[
        climatology["n"] >= VCI_MIN_OBSERVATIONS
    ]

    # ----------------------------------------------------------
    # Merge climatology
    # ----------------------------------------------------------

    df = df.merge(
        climatology[
            [
                "adm1_name",
                "month",
                "ndvi_min",
                "ndvi_max"
            ]
        ],
        on=[
            "adm1_name",
            "month"
        ],
        how="left"
    )

    # ----------------------------------------------------------
    # Compute denominator
    # ----------------------------------------------------------

    denominator = (
        df["ndvi_max"] -
        df["ndvi_min"]
    )

    # ----------------------------------------------------------
    # Compute VCI
    # ----------------------------------------------------------

    df["vci"] = np.where(
        denominator > 0,
        (
            (
                df[value_col] -
                df["ndvi_min"]
            )
            / denominator
        ) * 100,
        np.nan
    )

    # ----------------------------------------------------------
    # Restrict to valid range
    # ----------------------------------------------------------

    df["vci"] = df["vci"].clip(
        lower=0,
        upper=100
    )

    # ----------------------------------------------------------
    # Return
    # ----------------------------------------------------------

    return df
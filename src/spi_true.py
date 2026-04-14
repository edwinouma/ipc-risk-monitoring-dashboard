import pandas as pd
import numpy as np
from scipy.stats import gamma, norm


def compute_true_spi(df):
    """
    Compute TRUE SPI (Gamma-based) and return
    pipeline-compatible dataframe where:

    value = SPI
    """

    df = df.copy()

    # -----------------------------------------
    # Ensure required columns
    # -----------------------------------------
    required = ["adm1_name", "date", "value"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")

    # -----------------------------------------
    # Ensure datetime + numeric
    # -----------------------------------------
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["date", "value"])

    if df.empty:
        raise ValueError("Input dataframe is empty after cleaning.")

    # -----------------------------------------
    # Step 1: Monthly aggregation (SUM ✅)
    # -----------------------------------------
    df["year_month"] = df["date"].dt.to_period("M")

    # 🔥 Dynamic grouping (country-aware)
    group_cols = ["adm1_name", "year_month"]
    if "country" in df.columns:
        group_cols = ["country"] + group_cols

    monthly = (
        df.groupby(group_cols)["value"]
        .sum()
        .reset_index()
    )

    # -----------------------------------------
    # Restore date + extract month
    # -----------------------------------------
    monthly["date"] = monthly["year_month"].dt.to_timestamp()
    monthly["month"] = monthly["date"].dt.month

    # -----------------------------------------
    # Step 2: TRUE SPI
    # -----------------------------------------
    def compute_spi(series):

        non_zero = series[series > 0]

        if len(non_zero) < 10:
            # Fallback: use empirical distribution (no gamma fit)
            ranks = series.rank(method="average", pct=True)

            # Avoid 0/1 issues
            ranks = np.clip(ranks, 1e-6, 1 - 1e-6)

            return norm.ppf(ranks)

        shape, loc, scale = gamma.fit(non_zero, floc=0)

        zero_prob = (series == 0).sum() / len(series)

        cdf = series.apply(
            lambda x: zero_prob if x == 0
            else zero_prob + (1 - zero_prob) * gamma.cdf(x, shape, loc=loc, scale=scale)
        )

        # 🔥 Prevent infinities
        cdf = np.clip(cdf, 1e-6, 1 - 1e-6)

        return norm.ppf(cdf)

    # 🔥 Dynamic SPI grouping (country-aware)
    spi_group_cols = ["adm1_name", "month"]
    if "country" in monthly.columns:
        spi_group_cols = ["country"] + spi_group_cols

    monthly["spi"] = (
        monthly.groupby(spi_group_cols)["value"]
        .transform(compute_spi)
    )

    # -----------------------------------------
    # Safety check
    # -----------------------------------------
    if "spi" not in monthly.columns:
        raise ValueError("SPI computation failed — 'spi' column missing.")

    # -----------------------------------------
    # 🔥 FINAL STEP: Replace value cleanly
    # -----------------------------------------
    monthly = monthly.drop(columns=["value"])
    monthly = monthly.rename(columns={"spi": "value"})

    # -----------------------------------------
    # 🔥 KEEP year_month (CRITICAL FOR PIPELINE)
    # -----------------------------------------
    cols = ["adm1_name", "date", "year_month", "value"]

    if "country" in monthly.columns:
        cols = ["country"] + cols

    monthly = monthly[cols]

    # -----------------------------------------
    # Drop NaNs safely
    # -----------------------------------------
    monthly = monthly.dropna(subset=["value"])

    if monthly.empty:
        raise ValueError("All SPI values are NaN — check input data.")

    # -----------------------------------------
    # Debug export
    # -----------------------------------------
    debug = monthly.copy()

    debug["year"] = debug["date"].dt.year
    debug["month"] = debug["date"].dt.month

    debug.to_csv("outputs/debug_spi_monthly_full.csv", index=False)

    print("✅ Debug file saved: outputs/debug_spi_monthly_full.csv")

    return monthly
import pandas as pd
from src.config import UNIT_COL, INDICATOR_COL, VALUE_COL


def compute_long_term_monthly_median(
    monthly_df_price
):
    """
    Compute long-term monthly median baseline
    per unit and commodity.

    Returns:
        DataFrame with:
            UNIT_COL
            INDICATOR_COL
            month (1–12)
            baseline_median
    """

    df_price = monthly_df_price.copy()

    # Extract month number
    df_price["month"] = df_price["year_month"].dt.month

    baseline = (
        df_price.groupby(["country", UNIT_COL, INDICATOR_COL, "month"])[VALUE_COL]
        .median()
        .reset_index()
        .rename(columns={VALUE_COL: "baseline_median"})
    )

    return baseline
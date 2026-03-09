import pandas as pd
from src.config import UNIT_COL, INDICATOR_COL, VALUE_COL


def compute_five_year_anomaly(
    monthly_df_price
):
    """
    Compute anomaly relative to the previous 5-year
    average for the same calendar month.

    Formula:
        (Price_t - 5yr_mean_month) / 5yr_mean_month * 100

    Returns:
        DataFrame with:
            UNIT_COL
            INDICATOR_COL
            year_month
            price
            five_year_anomaly
            value (alias used for downstream pipeline)
    """

    df_price = monthly_df_price.copy()

    # Ensure sorted for rolling calculations
    df_price = df_price.sort_values(
        [UNIT_COL, INDICATOR_COL, "year_month"]
    )

    # Extract year and month
    df_price["year"] = df_price["year_month"].dt.year
    df_price["month"] = df_price["year_month"].dt.month

    # Compute rolling 5-year baseline for each unit + indicator + month
    df_price["five_year_mean"] = (
        df_price.groupby([UNIT_COL, INDICATOR_COL, "month"])[VALUE_COL]
        .transform(lambda x: x.shift(1).rolling(5, min_periods=5).mean())
    )

    # Compute anomaly
    df_price["five_year_anomaly"] = (
                                            (df_price[VALUE_COL] - df_price["five_year_mean"])
                                            / df_price["five_year_mean"]
                                    ) * 100

    # ---------------------------------------------------
    # Remove months without sufficient 5-year history
    # ---------------------------------------------------
    df_price = df_price.dropna(subset=["five_year_mean"])

    # Preserve original price
    df_price["price"] = df_price[VALUE_COL]

    # Use anomaly as pipeline value
    df_price["value"] = df_price["five_year_anomaly"]

    # Mark baseline method
    df_price["baseline_method"] = "FIVE_YEAR"

    return df_price
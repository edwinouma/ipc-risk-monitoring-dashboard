import pandas as pd
from src.config import UNIT_COL, INDICATOR_COL, DATE_COL, VALUE_COL


def compute_monthly_prices(
    df_price,
    aggregation="mean"
):
    """
    Convert weekly price data to monthly price data.

    Returns:
        DataFrame with:
            UNIT_COL
            INDICATOR_COL
            year_month (Period[M])
            VALUE_COL (monthly price)
    """

    df_price = df_price.copy()

    # Ensure date is datetime
    df_price[DATE_COL] = pd.to_datetime(df_price[DATE_COL])

    # Sort for stability
    df_price = df_price.sort_values([UNIT_COL, INDICATOR_COL, DATE_COL])

    # Create monthly period
    df_price["year_month"] = df_price[DATE_COL].dt.to_period("M")

    # Aggregate weekly prices to monthly
    if aggregation == "mean":
        monthly = (
            df_price.groupby(["country", UNIT_COL, INDICATOR_COL, "year_month"])[VALUE_COL]
            .mean()
            .reset_index()
        )

    elif aggregation == "median":
        monthly = (
            df_price.groupby(["country", UNIT_COL, INDICATOR_COL, "year_month"])[VALUE_COL]
            .median()
            .reset_index()
        )

    else:
        raise ValueError("Aggregation must be 'mean' or 'median'.")

    return monthly
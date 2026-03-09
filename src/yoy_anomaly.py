import pandas as pd
from src.config import UNIT_COL, INDICATOR_COL, VALUE_COL


def compute_yoy_anomaly(
    monthly_df_price
):

    df_price = monthly_df_price.copy()

    # Sort for correct lag calculation
    df_price = df_price.sort_values(
        [UNIT_COL, INDICATOR_COL, "year_month"]
    )

    # ---------------------------------------------------
    # Compute 12-month lag
    # ---------------------------------------------------
    df_price["price_lag12"] = (
        df_price.groupby([UNIT_COL, INDICATOR_COL])[VALUE_COL]
        .shift(12)
    )

    # ---------------------------------------------------
    # Compute YoY anomaly
    # ---------------------------------------------------
    df_price["yoy_anomaly"] = (
        (df_price[VALUE_COL] - df_price["price_lag12"])
        / df_price["price_lag12"]
    ) * 100

    # ---------------------------------------------------
    # Remove months without 12-month history
    # ---------------------------------------------------
    df_price = df_price.dropna(subset=["price_lag12"])

    # Preserve original price
    df_price["price"] = df_price[VALUE_COL]

    # Use anomaly as pipeline value
    df_price["value"] = df_price["yoy_anomaly"]

    # Mark baseline method
    df_price["baseline_method"] = "YOY"

    return df_price
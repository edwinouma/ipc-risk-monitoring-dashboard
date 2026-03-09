import pandas as pd
from src.config import UNIT_COL, INDICATOR_COL, VALUE_COL


def compute_ltm_anomaly(
    monthly_df_price,
    baseline_df_price
):
    """
    Compute % deviation from long-term monthly median baseline (LTM anomaly).

    Returns:
        DataFrame with:
            UNIT_COL
            INDICATOR_COL
            year_month
            price
            ltm_anomaly
            value (alias used for downstream pipeline)
    """

    df_price = monthly_df_price.copy()

    # Extract month
    df_price["month"] = df_price["year_month"].dt.month

    # Merge baseline
    df_price = df_price.merge(
        baseline_df_price,
        on=["country", UNIT_COL, INDICATOR_COL, "month"],
        how="left"
    )

    # Compute LTM anomaly
    df_price["ltm_anomaly"] = (
        (df_price[VALUE_COL] - df_price["baseline_median"])
        / df_price["baseline_median"]
    ) * 100

    # Preserve original price
    df_price["price"] = df_price[VALUE_COL]

    # Use anomaly as pipeline value
    df_price["value"] = df_price["ltm_anomaly"]

    return df_price
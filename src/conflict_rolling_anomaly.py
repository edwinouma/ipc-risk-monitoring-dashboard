import pandas as pd
from src.config import UNIT_COL, INDICATOR_COL, VALUE_COL


def compute_conflict_rolling_anomaly(
    monthly_df_conflict
):

    df_conflict = monthly_df_conflict.copy()

    # Sort
    df_conflict = df_conflict.sort_values(
        [UNIT_COL, INDICATOR_COL, "year_month"]
    )

    # ---------------------------------------------------
    # Rolling mean
    # ---------------------------------------------------
    df_conflict["rolling_mean_6"] = (
        df_conflict.groupby([UNIT_COL, INDICATOR_COL])[VALUE_COL]
        .transform(lambda x: x.rolling(6, min_periods=3).mean())
    )

    # ---------------------------------------------------
    # Rolling std
    # ---------------------------------------------------
    df_conflict["rolling_std_6"] = (
        df_conflict.groupby([UNIT_COL, INDICATOR_COL])[VALUE_COL]
        .transform(lambda x: x.rolling(6, min_periods=3).std())
    )

    df_conflict["rolling_std_6"] = df_conflict["rolling_std_6"].replace(0, 1e-6)

    # ---------------------------------------------------
    # Anomaly
    # ---------------------------------------------------
    df_conflict["conflict_anomaly"] = (
        df_conflict[VALUE_COL] - df_conflict["rolling_mean_6"]
    )

    # ---------------------------------------------------
    # Z-score
    # ---------------------------------------------------
    df_conflict["zscore"] = (
        df_conflict["conflict_anomaly"] / df_conflict["rolling_std_6"]
    )

    # ---------------------------------------------------
    # Pipeline value
    # ---------------------------------------------------
    df_conflict["value"] = df_conflict["zscore"]

    # Preserve raw
    df_conflict["conflict_events"] = df_conflict[VALUE_COL]

    # Label
    df_conflict["baseline_method"] = "ROLLING_MEAN_6_ZSCORE"

    return df_conflict
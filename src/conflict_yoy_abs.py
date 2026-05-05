import pandas as pd
from src.config import UNIT_COL, INDICATOR_COL, VALUE_COL


def compute_conflict_yoy_abs(monthly_df_conflict):

    df = monthly_df_conflict.copy()

    # ---------------------------------------------------
    # Ensure year_month is Period[M]
    # ---------------------------------------------------
    df["year_month"] = df["year_month"].astype("period[M]")

    # ---------------------------------------------------
    # Create previous year reference
    # ---------------------------------------------------
    df_prev = df.copy()
    df_prev["year_month"] = df_prev["year_month"] + 12  # shift forward → aligns with current

    df_prev = df_prev.rename(columns={
        VALUE_COL: "lag12"
    })

    # ---------------------------------------------------
    # Merge current with previous year SAME MONTH
    # ---------------------------------------------------
    df = df.merge(
        df_prev[[UNIT_COL, INDICATOR_COL, "year_month", "lag12"]],
        on=[UNIT_COL, INDICATOR_COL, "year_month"],
        how="left"
    )

    # ---------------------------------------------------
    # YoY absolute change
    # ---------------------------------------------------
    df["conflict_yoy_abs"] = df[VALUE_COL] - df["lag12"]

    # ---------------------------------------------------
    # YoY ratio
    # ---------------------------------------------------
    df["yoy_ratio"] = df[VALUE_COL] / df["lag12"]

    df.loc[
        (df["lag12"].isna()) | (df["lag12"] == 0),
        "yoy_ratio"
    ] = None

    # ---------------------------------------------------
    # Preserve original values
    # ---------------------------------------------------
    df["conflict_events"] = df[VALUE_COL]
    df["value"] = df[VALUE_COL]

    # ---------------------------------------------------
    # Supporting signal
    # ---------------------------------------------------
    df["yoy_signal"] = df["conflict_yoy_abs"]

    # ---------------------------------------------------
    # Label method
    # ---------------------------------------------------
    df["baseline_method"] = "YOY_ABS"

    return df
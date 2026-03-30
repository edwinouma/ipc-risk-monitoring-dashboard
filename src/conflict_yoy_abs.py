import pandas as pd
from src.config import UNIT_COL, INDICATOR_COL, VALUE_COL


def compute_conflict_yoy_abs(
    monthly_df_conflict
):

    df_conflict = monthly_df_conflict.copy()

    # ---------------------------------------------------
    # Sort for correct lag calculation
    # ---------------------------------------------------
    df_conflict = df_conflict.sort_values(
        [UNIT_COL, INDICATOR_COL, "year_month"]
    )

    # ---------------------------------------------------
    # Compute 12-month lag
    # ---------------------------------------------------
    df_conflict["lag12"] = (
        df_conflict.groupby([UNIT_COL, INDICATOR_COL])[VALUE_COL]
        .shift(12)
    )

    # Fill lag first
    df_conflict["lag12"] = df_conflict["lag12"].fillna(0)

    # Ensure numeric consistency (optional but safe)
    df_conflict["lag12"] = df_conflict["lag12"].astype(float)

    # Then compute YoY
    df_conflict["conflict_yoy_abs"] = (
            df_conflict[VALUE_COL] - df_conflict["lag12"]
    )

    # ---------------------------------------------------
    # Preserve original values
    # ---------------------------------------------------
    df_conflict["conflict_events"] = df_conflict[VALUE_COL]

    # ---------------------------------------------------
    # Use YoY absolute change as pipeline value
    # ---------------------------------------------------
    df_conflict["value"] = df_conflict["conflict_yoy_abs"]

    # ---------------------------------------------------
    # Label method
    # ---------------------------------------------------
    df_conflict["baseline_method"] = "YOY_ABS"

    return df_conflict
import pandas as pd


# ---------------------------------------------------
# Aggregate classification to national level
# ---------------------------------------------------
def aggregate_national(
    classified_df,
    unit_col="adm1_name"
):
    """
    Aggregate classification results to national level.

    Input:
        classified_df (output of apply_thresholds)
        Must contain:
            - year_month
            - classification
            - unit_col

    Output:
        DataFrame with:
            - year_month
            - Alarm
            - Alert
            - Minimal
            - Alarm_pct
            - Alert_pct
            - Minimal_pct
            - date
    """

    # ---------------------------------------------------
    # 1. Determine total provinces (fixed baseline)
    # ---------------------------------------------------
    total_units = classified_df[unit_col].nunique()

    # ---------------------------------------------------
    # 2. Count classification per month
    # ---------------------------------------------------
    counts = (
        classified_df
        .groupby(["year_month", "classification"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )

    # Ensure all columns exist
    for col in ["Alarm", "Alert", "Minimal"]:
        if col not in counts.columns:
            counts[col] = 0

    # ---------------------------------------------------
    # 3. Compute percentages (fixed denominator)
    # ---------------------------------------------------
    counts["Alarm_pct"] = counts["Alarm"] / total_units * 100
    counts["Alert_pct"] = counts["Alert"] / total_units * 100
    counts["Minimal_pct"] = counts["Minimal"] / total_units * 100

    # ---------------------------------------------------
    # 4. Add timestamp column
    # ---------------------------------------------------
    counts["date"] = counts["year_month"].dt.to_timestamp()

    counts = counts.sort_values("date")

    return counts
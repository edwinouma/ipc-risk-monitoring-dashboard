import pandas as pd
from src.config import CLASSIFICATION_LABELS

alarm_label = CLASSIFICATION_LABELS["alarm"]
alert_label = CLASSIFICATION_LABELS["alert"]
minimal_label = CLASSIFICATION_LABELS["minimal"]
no_data_label = CLASSIFICATION_LABELS.get("no_data", "No data")


# ---------------------------------------------------
# Aggregate classification to national level
# ---------------------------------------------------
def aggregate_national(
    classified_df,
    unit_col="adm1_name"
):
    """
    Aggregate classification results to national level.
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
    for col in [alarm_label, alert_label, minimal_label, no_data_label]:
        if col not in counts.columns:
            counts[col] = 0

    # ---------------------------------------------------
    # 3. Compute percentages (fixed denominator)
    # ---------------------------------------------------
    counts[f"{alarm_label}_pct"] = counts[alarm_label] / total_units * 100
    counts[f"{alert_label}_pct"] = counts[alert_label] / total_units * 100
    counts[f"{minimal_label}_pct"] = counts[minimal_label] / total_units * 100
    counts[f"{no_data_label}_pct"] = counts[no_data_label] / total_units * 100

    # ---------------------------------------------------
    # 4. Add timestamp column
    # ---------------------------------------------------
    counts["date"] = counts["year_month"].dt.to_timestamp()

    counts = counts.sort_values("date")

    return counts
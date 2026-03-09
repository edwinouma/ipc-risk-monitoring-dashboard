from src.unit_month import compute_unit_month_values
import pandas as pd
from src.classification_utils import classify_series

def compute_monthly_trigger_counts(
    df,
    unit_col,
    indicator_col,
    value_col,
    indicator_value,
    thresholds_df,
    total_units_fixed=34
):
    """
    Compute Alarm, Alert, and Minimal counts and percentages
    using a fixed denominator (e.g., 34 provinces).

    Minimal = total_units_fixed - (Alarm + Alert)
    """

    # -----------------------------------------
    # 1. Compute full unit-month values (NO filtering)
    # -----------------------------------------
    df_unit_month = compute_unit_month_values(
        df=df,
        unit_col=unit_col,
        indicator_col=indicator_col,
        value_col=value_col,
        indicator_value=indicator_value,
        aggregation="mean"
    )

    # -----------------------------------------
    # 2. Get thresholds
    # -----------------------------------------
    th = thresholds_df[thresholds_df["indicator"] == indicator_value]

    if th.empty:
        raise ValueError(f"No thresholds found for indicator: {indicator_value}")

    th = th.iloc[0]

    alert_p = th["alert_percentile"]
    alarm_p = th["alarm_percentile"]

    alert_t = th["alert_tukey"]
    alarm_t = th["alarm_tukey"]

    # -----------------------------------------
    # 3. Classification using shared engine
    # -----------------------------------------

    # Percentile classification
    classification_percentile = classify_series(
        df_unit_month[value_col],
        indicator_value,
        alarm_p,
        alert_p
    )

    # Tukey classification
    classification_tukey = classify_series(
        df_unit_month[value_col],
        indicator_value,
        alarm_t,
        alert_t
    )

    df_unit_month["alarm_percentile_flag"] = (
            classification_percentile == "Alarm"
    )

    df_unit_month["alert_percentile_flag"] = (
            classification_percentile == "Alert"
    )

    df_unit_month["alarm_tukey_flag"] = (
            classification_tukey == "Alarm"
    )

    df_unit_month["alert_tukey_flag"] = (
            classification_tukey == "Alert"
    )

    # -----------------------------------------
    # 4. Aggregate Alarm & Alert
    # -----------------------------------------
    counts = (
        df_unit_month
        .groupby("year_month")
        .agg(
            alarms_percentile=("alarm_percentile_flag", "sum"),
            alerts_percentile=("alert_percentile_flag", "sum"),
            alarms_tukey=("alarm_tukey_flag", "sum"),
            alerts_tukey=("alert_tukey_flag", "sum"),
        )
        .reset_index()
    )

    # -----------------------------------------
    # 5. Fixed Minimal Calculation
    # -----------------------------------------
    counts["total_units"] = total_units_fixed

    # Percentile minimal
    counts["minimal_percentile"] = (
        total_units_fixed
        - (counts["alarms_percentile"] + counts["alerts_percentile"])
    )

    # Tukey minimal
    counts["minimal_tukey"] = (
        total_units_fixed
        - (counts["alarms_tukey"] + counts["alerts_tukey"])
    )

    # -----------------------------------------
    # 6. Percentages (Fixed Denominator)
    # -----------------------------------------
    counts["alarm_percentile_pct"] = (
        counts["alarms_percentile"] / total_units_fixed * 100
    )

    counts["alert_percentile_pct"] = (
        counts["alerts_percentile"] / total_units_fixed * 100
    )

    counts["minimal_percentile_pct"] = (
        counts["minimal_percentile"] / total_units_fixed * 100
    )

    counts["alarm_tukey_pct"] = (
        counts["alarms_tukey"] / total_units_fixed * 100
    )

    counts["alert_tukey_pct"] = (
        counts["alerts_tukey"] / total_units_fixed * 100
    )

    counts["minimal_tukey_pct"] = (
        counts["minimal_tukey"] / total_units_fixed * 100
    )

    numeric_cols = counts.select_dtypes(include="number").columns
    counts[numeric_cols] = counts[numeric_cols].round(2)

    # -----------------------------------------
    # 7. Metadata
    # -----------------------------------------
    counts["indicator"] = indicator_value
    counts["date"] = counts["year_month"].dt.to_timestamp()

    return counts
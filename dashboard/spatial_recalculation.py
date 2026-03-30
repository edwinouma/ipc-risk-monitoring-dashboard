import pandas as pd
from src.config import INDICATOR_DIRECTION


def recalculate_thresholds(
    df_unit_month,
    indicator_value,
    selected_units,
    unit_col="adm1_name",
    value_col="value",
    min_obs=5,
    alarm_pct=25,
    alert_pct=50
):
    """
    Dynamically recompute:
        - Composite percentile thresholds (USER-CONTROLLED)
        - Tukey thresholds (UNCHANGED)

    Direction-aware:
        - Lower tail (<100) for drought-style indicators
        - Upper tail (>0) for price indicators
    """

    # ---------------------------------------------------
    # 1. Filter indicator + selected provinces
    # ---------------------------------------------------
    df = df_unit_month[df_unit_month["indicator"] == indicator_value].copy()

    if selected_units:
        df = df[df[unit_col].isin(selected_units)]

    if df.empty:
        raise ValueError("No data available for selected provinces.")

    # ---------------------------------------------------
    # 2. Apply directional risk filter
    # ---------------------------------------------------
    direction = INDICATOR_DIRECTION.get(indicator_value, "lower")

    if direction == "lower":
        df = df[df[value_col] < 100]
    elif direction == "upper":
        df = df[df[value_col] > 0]

    if df.empty:
        raise ValueError("No risk-side data available after filtering.")

    # ---------------------------------------------------
    # 3. Compute spatial percentiles per month (DYNAMIC)
    # ---------------------------------------------------
    spatial = (
        df.groupby("year_month")[value_col]
        .agg(
            alarm_q=lambda x: x.quantile(alarm_pct / 100),
            alert_q=lambda x: x.quantile(alert_pct / 100),
            q25=lambda x: x.quantile(0.25),
            q75=lambda x: x.quantile(0.75),
            count="count"
        )
        .reset_index()
    )

    spatial = spatial[spatial["count"] >= min_obs]

    if spatial.empty:
        raise ValueError("Insufficient data after min_obs filter.")

    spatial["iqr"] = spatial["q75"] - spatial["q25"]

    # ---------------------------------------------------
    # 4. Composite thresholds (direction-aware)
    # ---------------------------------------------------
    direction = INDICATOR_DIRECTION.get(indicator_value, "lower")

    if direction == "lower":
        # Lower = worse (climate)
        composite_alarm = spatial["alarm_q"].median()
        composite_alert = spatial["alert_q"].median()

    else:
        # Upper = worse (prices)
        # 🔥 Reverse interpretation
        composite_alarm = spatial["alert_q"].median()
        composite_alert = spatial["alarm_q"].median()

    # ---------------------------------------------------
    # 5. Tukey thresholds (UNCHANGED)
    # ---------------------------------------------------
    q1_median = spatial["q25"].median()
    q3_median = spatial["q75"].median()
    median_iqr = spatial["iqr"].median()

    if direction == "lower":
        tukey_alert = q1_median - 1.0 * median_iqr
        tukey_alarm = q1_median - 1.5 * median_iqr
    else:
        tukey_alert = q3_median + 1.0 * median_iqr
        tukey_alarm = q3_median + 1.5 * median_iqr

    return {
        "percentile": {
            "alarm": float(composite_alarm),
            "alert": float(composite_alert)
        },
        "tukey": {
            "alarm": float(tukey_alarm),
            "alert": float(tukey_alert)
        }
    }
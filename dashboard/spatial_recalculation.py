import pandas as pd
from src.config import INDICATOR_DIRECTION


def recalculate_thresholds(
    df_unit_month,
    indicator_value,
    selected_units,
    unit_col="adm1_name",
    value_col="value",
    min_obs=5
):
    """
    Dynamically recompute:
        - Composite percentile thresholds
        - Tukey thresholds

    Direction-aware:
        - Lower tail (<100) for drought-style indicators
        - Upper tail (>0) for price inflation indicators
    """

    # ---------------------------------------------------
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
        raise ValueError("No risk-side data available after directional filtering.")

    # ---------------------------------------------------
    # 3. Compute spatial percentiles per month
    # ---------------------------------------------------
    spatial = (
        df.groupby("year_month")[value_col]
        .agg(
            q25=lambda x: x.quantile(0.25),
            q50=lambda x: x.quantile(0.50),
            q75=lambda x: x.quantile(0.75),
            count="count"
        )
        .reset_index()
    )

    spatial = spatial[spatial["count"] >= min_obs]

    if spatial.empty:
        raise ValueError("Insufficient data after applying min_obs filter.")

    spatial["iqr"] = spatial["q75"] - spatial["q25"]

    # ---------------------------------------------------
    # 4. Composite thresholds (direction aware)
    # ---------------------------------------------------
    direction = INDICATOR_DIRECTION.get(indicator_value, "lower")

    if direction == "lower":

        composite_alarm = spatial["q25"].median()
        composite_alert = spatial["q50"].median()

    else:  # upper-tail indicators (prices)

        composite_alert = spatial["q50"].median()
        composite_alarm = spatial["q75"].median()

    # ---------------------------------------------------
    # 5. Tukey thresholds (direction aware)
    # ---------------------------------------------------
    q1_median = spatial["q25"].median()
    q3_median = spatial["q75"].median()
    median_iqr = spatial["iqr"].median()

    if direction == "lower":

        tukey_alert = q1_median - 1.0 * median_iqr
        tukey_alarm = q1_median - 1.5 * median_iqr

    else:  # upper-tail indicators

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
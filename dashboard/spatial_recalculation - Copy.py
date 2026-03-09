import pandas as pd


# ---------------------------------------------------
# Recalculate spatial thresholds dynamically
# ---------------------------------------------------
def recalculate_thresholds(
    df_unit_month,
    selected_units,
    unit_col="adm1_name",
    value_col="value",
    drought_only=True,
    min_obs=5
):
    """
    Dynamically recompute:
        - Composite percentile thresholds
        - Tukey thresholds

    Thresholds are computed from spatial percentiles per month.
    Drought-only filter (<100) is applied if drought_only=True.
    """

    # ---------------------------------------------------
    # 1. Filter selected provinces
    # ---------------------------------------------------
    if selected_units:
        df = df_unit_month[df_unit_month[unit_col].isin(selected_units)].copy()
    else:
        df = df_unit_month.copy()

    if df.empty:
        raise ValueError("No data available for selected provinces.")

    # ---------------------------------------------------
    # 2. Apply drought-only filter (threshold stage ONLY)
    # ---------------------------------------------------
    if drought_only:
        df = df[df[value_col] < 100]

    if df.empty:
        raise ValueError("No drought-side data available after filtering (<100).")

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

    # Ensure minimum observations
    spatial = spatial[spatial["count"] >= min_obs]

    if spatial.empty:
        raise ValueError("Insufficient data after applying min_obs filter.")

    spatial["iqr"] = spatial["q75"] - spatial["q25"]

    # ---------------------------------------------------
    # 4. Composite thresholds (median across time)
    # ---------------------------------------------------
    composite_alarm = spatial["q25"].median()
    composite_alert = spatial["q50"].median()

    # ---------------------------------------------------
    # 5. Tukey thresholds
    # ---------------------------------------------------
    q1_median = spatial["q25"].median()
    median_iqr = spatial["iqr"].median()

    tukey_alert = q1_median - 1.0 * median_iqr
    tukey_alarm = q1_median - 1.5 * median_iqr

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
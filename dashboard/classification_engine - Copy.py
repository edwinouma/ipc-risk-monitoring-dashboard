import pandas as pd


# ---------------------------------------------------
# Apply thresholds to unit-month values
# ---------------------------------------------------
def apply_thresholds(
    df_unit_month,
    selected_units,
    alarm_threshold,
    alert_threshold,
    unit_col="adm1_name",
    value_col="value"
):
    """
    Apply thresholds and compute:
        - classification per unit per month
        - monthly counts (fixed total units)
        - monthly percentages
    """

    # ---------------------------------------------------
    # 1. Filter selected units
    # ---------------------------------------------------
    if selected_units:
        df = df_unit_month[df_unit_month[unit_col].isin(selected_units)].copy()
    else:
        df = df_unit_month.copy()

    TOTAL_UNITS = len(selected_units) if selected_units else df[unit_col].nunique()

    # ---------------------------------------------------
    # 2. Create complete unit-month grid
    # ---------------------------------------------------
    all_months = df["year_month"].unique()
    all_units = selected_units if selected_units else df[unit_col].unique()

    full_grid = pd.MultiIndex.from_product(
        [all_months, all_units],
        names=["year_month", unit_col]
    ).to_frame(index=False)

    df = full_grid.merge(
        df,
        on=["year_month", unit_col],
        how="left"
    )

    # ---------------------------------------------------
    # 3. Classification logic
    # ---------------------------------------------------
    def classify(value):
        if pd.isna(value):
            return "Minimal"
        elif value <= alarm_threshold:
            return "Alarm"
        elif value <= alert_threshold:
            return "Alert"
        else:
            return "Minimal"

    df["classification"] = df[value_col].apply(classify)

    # ---------------------------------------------------
    # 4. Monthly counts (fixed 34 logic)
    # ---------------------------------------------------
    counts = (
        df.groupby(["year_month", "classification"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )

    # Ensure columns exist
    for col in ["Alarm", "Alert"]:
        if col not in counts.columns:
            counts[col] = 0

    # FIXED TOTAL LOGIC
    counts["Minimal"] = TOTAL_UNITS - (
        counts.get("Alarm", 0) + counts.get("Alert", 0)
    )

    # ---------------------------------------------------
    # 5. Percentages (based on fixed total)
    # ---------------------------------------------------
    counts["Alarm_pct"] = counts["Alarm"] / TOTAL_UNITS * 100
    counts["Alert_pct"] = counts["Alert"] / TOTAL_UNITS * 100
    counts["Minimal_pct"] = counts["Minimal"] / TOTAL_UNITS * 100

    # Convert for plotting
    counts["date"] = counts["year_month"].dt.to_timestamp()

    counts = counts.sort_values("date")

    return df, counts
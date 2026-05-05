import pandas as pd
import numpy as np
from src.classification_utils import classify_series

from src.config import CLASSIFICATION_LABELS

alarm_label = CLASSIFICATION_LABELS["alarm"]
alert_label = CLASSIFICATION_LABELS["alert"]
minimal_label = CLASSIFICATION_LABELS["minimal"]
no_data_label = CLASSIFICATION_LABELS.get("no_data", "No data")

# ---------------------------------------------------
# Apply thresholds to unit-month values
# ---------------------------------------------------
def apply_thresholds(
    df_unit_month,
    selected_units,
    alarm_threshold,
    alert_threshold,
    indicator_value,   # ← ADD THIS
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

    # -----------------------------------------
    # ✅ CORRECT TOTAL UNITS (BEFORE GRID)
    # -----------------------------------------
    TOTAL_UNITS = len(selected_units) if selected_units else df[unit_col].nunique()

    # ---------------------------------------------------
    # 2. Create complete unit-month grid
    # ---------------------------------------------------
    all_months = df["year_month"].unique()
    all_units = (
        selected_units
        if selected_units
        else df.dropna(subset=["value"])[unit_col].unique()
    )

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
    # 3. Classification using shared engine
    # ---------------------------------------------------

    from src.config import INDICATOR_METHOD, CONFLICT_USE_COMBINED, CONFLICT_COMBINED_RULES

    method = INDICATOR_METHOD.get(indicator_value, "percentile")

    # ---------------------------------------------------
    # 3A. COMBINED CONFLICT LOGIC (events + fatalities)
    # ---------------------------------------------------
    if method == "event_combined" and CONFLICT_USE_COMBINED:

        rules = CONFLICT_COMBINED_RULES[indicator_value]

        event_alert = rules["event_alert_threshold"]
        event_alarm = rules["event_alarm_threshold"]
        fatal_alarm = rules["fatality_alarm_threshold"]

        # 🔥 USE FILTERED df (IMPORTANT FIX)
        df_events = df[df["indicator"] == "conflict_events"]
        df_fatal = df[df["indicator"] == "conflict_fatalities"]

        # Merge
        df_combined = df_events.merge(
            df_fatal,
            on=["year_month", unit_col],
            suffixes=("_events", "_fatalities")
        )

        # Handle missing
        missing_mask = (
                pd.isna(df_combined["value_events"]) |
                pd.isna(df_combined["value_fatalities"])
        )

        # Classification
        df_combined["classification"] = np.where(
            missing_mask,
            no_data_label,
            np.where(
                (df_combined["value_events"] >= event_alarm) |
                (df_combined["value_fatalities"] >= fatal_alarm),
                alarm_label,
                np.where(
                    (df_combined["value_events"] >= event_alert) &
                    (df_combined["value_fatalities"] < fatal_alarm),
                    alert_label,
                    minimal_label
                )
            )
        )

        df_combined["value"] = df_combined["value_events"]

        # 🔥 REAPPLY GRID (CRITICAL FIX)
        df = full_grid.merge(
            df_combined,
            on=["year_month", unit_col],
            how="left"
        )
        df["classification"] = no_data_label

        df["indicator"] = "conflict_events"

    # ---------------------------------------------------
    # 3B. NORMAL LOGIC (existing)
    # ---------------------------------------------------
    else:

        # -----------------------------------------
        # Apply classification ONLY on valid values
        # -----------------------------------------
        valid_mask = df[value_col].notna()

        df["classification"] = no_data_label  # default

        df.loc[valid_mask, "classification"] = classify_series(
            df.loc[valid_mask, value_col],
            indicator_value,
            alarm_threshold,
            alert_threshold
        )

    # ---------------------------------------------------
    # 3C. SPI SIGNAL TYPE (DROUGHT / FLOOD)
    # ---------------------------------------------------
    method = INDICATOR_METHOD.get(indicator_value, "percentile")

    if method == "spi_true":
        df["signal_type"] = np.where(
            df[value_col].isna(),
            no_data_label,
            np.where(
                df[value_col] <= 0,
                "Drought",
                "Flood"
            )
        )
    else:
        df["signal_type"] = "Not Applicable"

    # ---------------------------------------------------
    # 4. Monthly counts (fixed 34 logic)
    # ---------------------------------------------------
    df["classification"] = df["classification"].astype(str).str.strip()

    counts = (
        df.groupby(["year_month", "classification"], dropna=False)
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )

    # Ensure columns exist
    for col in [alarm_label, alert_label, minimal_label, no_data_label]:
        if col not in counts.columns:
            counts[col] = 0

    # ---------------------------------------------------
    # 5. Percentages (based on fixed total)
    # ---------------------------------------------------
    counts[f"{alarm_label}_pct"] = counts[alarm_label] / TOTAL_UNITS * 100
    counts[f"{alert_label}_pct"] = counts[alert_label] / TOTAL_UNITS * 100
    counts[f"{minimal_label}_pct"] = counts[minimal_label] / TOTAL_UNITS * 100
    counts[f"{no_data_label}_pct"] = counts[no_data_label] / TOTAL_UNITS * 100

    # Convert for plotting
    counts["date"] = counts["year_month"].dt.to_timestamp()

    counts = counts.sort_values("date")

    return df, counts
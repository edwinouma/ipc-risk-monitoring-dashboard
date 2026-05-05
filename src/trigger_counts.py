from src.unit_month import compute_unit_month_values
import pandas as pd
from src.classification_utils import classify_series
from src.config import CLASSIFICATION_LABELS


alarm_label = CLASSIFICATION_LABELS["alarm"]
alert_label = CLASSIFICATION_LABELS["alert"]
minimal_label = CLASSIFICATION_LABELS["minimal"]

def compute_monthly_trigger_counts(
    df,
    unit_col,
    indicator_col,
    value_col,
    indicator_value,
    thresholds_df,
):
    """
    Compute Alarm, Alert, and Minimal counts and percentages
    using a fixed denominator (e.g., 34 provinces).

    Minimal = total_units - (Alarm + Alert)
    """

    # -----------------------------------------
    # 1. Compute full unit-month values (NO filtering)
    # -----------------------------------------
    from src.config import INDICATOR_METHOD

    method_type = INDICATOR_METHOD.get(indicator_value, "percentile")

    th = thresholds_df[thresholds_df["indicator"] == indicator_value]

    th = th.iloc[0]

    alert_p = th["alert_percentile"]
    alarm_p = th["alarm_percentile"]

    # ---------------------------------------------------
    # 🔥 HANDLE EVENT INDICATORS DIFFERENTLY

    if method_type == "event":

        # 🔥 Aggregate FIRST (no filtering)
        df_unit_month = (
            df
            .groupby([unit_col, "year_month", indicator_col], as_index=False)
            .agg({
                value_col: "sum"
            })
        )

        # 🔥 THEN filter indicator
        df_unit_month = df_unit_month[
            df_unit_month[indicator_col] == indicator_value
            ]

        # ---------------------------------------------------

        # 🔥 ENSURE FULL UNIT-MONTH COVERAGE (ADD HERE)

        # ---------------------------------------------------

        all_units = df[unit_col].unique()

        all_months = df["year_month"].unique()   # 🔥 FULL dataset

        full_grid = pd.MultiIndex.from_product(

            [all_units, all_months],

            names=[unit_col, "year_month"]

        ).to_frame(index=False)

        df_unit_month = full_grid.merge(

            df_unit_month,

            on=[unit_col, "year_month"],

            how="left"

        )

        # Fill missing values as 0 (no conflict)

        df_unit_month[value_col] = df_unit_month[value_col].fillna(0)

        # -----------------------------------------
        # 🔥 CORRECT PLACE FOR TOTAL UNITS
        # -----------------------------------------
        total_units = df_unit_month[unit_col].nunique()

        # ---------------------------------------------------
        # 🔥 ADD THIS BLOCK RIGHT HERE
        # ---------------------------------------------------

        df_unit_month["classification"] = classify_series(
            df_unit_month[value_col],
            indicator_value,
            alarm_p,
            alert_p
        )

        counts = (
            df_unit_month
            .groupby("year_month")["classification"]
            .value_counts()
            .unstack(fill_value=0)
            .reset_index()
        )

        # Ensure all categories exist
        for col in [alarm_label, alert_label, minimal_label]:
            if col not in counts.columns:
                counts[col] = 0

        # Map to expected structure
        counts["alarms_percentile"] = counts[alarm_label]
        counts["alerts_percentile"] = counts[alert_label]

        counts["alarms_tukey"] = counts[alarm_label]
        counts["alerts_tukey"] = counts[alert_label]

        counts["alarms_zscore"] = counts[alarm_label]
        counts["alerts_zscore"] = counts[alert_label]

        counts["year_month"] = counts["year_month"]

    elif method_type == "event_combined":
        df_unit_month = None  # not used

    else:

        df_unit_month = compute_unit_month_values(
            df=df,
            unit_col=unit_col,
            indicator_col=indicator_col,
            value_col=value_col,
            indicator_value=indicator_value,
            aggregation="mean"
        )

        # -----------------------------------------
        # 🔥 ENSURE FULL UNIT-MONTH COVERAGE
        # -----------------------------------------

        all_units = df[unit_col].unique()
        all_months = df["year_month"].unique()

        full_grid = pd.MultiIndex.from_product(
            [all_units, all_months],
            names=[unit_col, "year_month"]
        ).to_frame(index=False)

        df_unit_month = full_grid.merge(
            df_unit_month,
            on=[unit_col, "year_month"],
            how="left"
        )

        # -----------------------------------------
        # 🔥 DYNAMIC TOTAL UNITS (CORRECT PLACE)
        # -----------------------------------------
        total_units = df_unit_month[unit_col].nunique()

        # 🔥 DO NOT fill with 0 for price/climate
        # Keep NaN → will be classified as Minimal

    from src.config import COMBINED_INDICATORS, CONFLICT_COMBINED_RULES

    # ---------------------------------------------------
    # 🔥 HANDLE EVENT_COMBINED (GENERIC)
    # ---------------------------------------------------
    if method_type == "event_combined":

        combined_cfg = COMBINED_INDICATORS.get(indicator_value)

        if combined_cfg is None:
            raise ValueError(f"No combined config for {indicator_value}")

        components = combined_cfg["components"]
        suffixes = combined_cfg["suffixes"]

        df_list = []

        for comp, suffix in zip(components, suffixes):
            df_comp = df[
                (df[indicator_col] == comp) &
                (df["baseline_method"] == "none")
                ].copy()

            df_comp = df_comp.rename(columns={
                value_col: f"value_{suffix}"
            })

            df_list.append(df_comp)

        df_combined = df_list[0]

        for df_next in df_list[1:]:
            df_combined = df_combined.merge(
                df_next,
                on=["year_month", "adm1_name"],
                how="outer"
            )

        # 🔥 AFTER ALL MERGES (correct place)
        df_combined["value_events"] = df_combined["value_events"].fillna(0)
        df_combined["value_fatalities"] = df_combined["value_fatalities"].fillna(0)

        rules = CONFLICT_COMBINED_RULES.get(indicator_value)

        if rules is None:
            raise ValueError(f"No rules for {indicator_value}")

        event_alert = rules["event_alert_threshold"]
        event_alarm = rules["event_alarm_threshold"]
        fatal_alarm = rules["fatality_alarm_threshold"]

        df_combined["alert_flag"] = (
                (df_combined["value_events"] >= event_alert) &
                (df_combined["value_fatalities"] < fatal_alarm)
        )

        df_combined["alarm_flag"] = (
                (df_combined["value_events"] >= event_alarm) |
                (df_combined["value_fatalities"] >= fatal_alarm)
        )

        counts = (
            df_combined
            .groupby("year_month")
            .agg(
                alarms_percentile=("alarm_flag", "sum"),
                alerts_percentile=("alert_flag", "sum"),
            )
            .reset_index()
        )

        counts["year_month"] = counts["year_month"]

        counts["alarms_tukey"] = counts["alarms_percentile"]
        counts["alerts_tukey"] = counts["alerts_percentile"]

        counts["alarms_zscore"] = counts["alarms_percentile"]
        counts["alerts_zscore"] = counts["alerts_percentile"]

    # ---------------------------------------------------
    # 🔥 NORMAL INDICATORS (UNCHANGED)
    # ---------------------------------------------------
    else:

        # 🔥 STEP 1: Create ONE classification per unit
        df_unit_month["classification"] = classify_series(
            df_unit_month[value_col],
            indicator_value,
            alarm_p,
            alert_p
        )

        # 🔥 STEP 2: Count UNIQUE units per month
        counts = (
            df_unit_month
            .groupby("year_month")["classification"]
            .value_counts()
            .unstack(fill_value=0)
            .reset_index()
        )

        # Ensure all categories exist
        for col in [alarm_label, alert_label, minimal_label]:
            if col not in counts.columns:
                counts[col] = 0

        # 🔥 STEP 3: Map to your existing structure
        counts["alarms_percentile"] = counts[alarm_label]
        counts["alerts_percentile"] = counts[alert_label]

        # 🔥 Keep compatibility for tukey/zscore (same counts)
        counts["alarms_tukey"] = counts[alarm_label]
        counts["alerts_tukey"] = counts[alert_label]

        counts["alarms_zscore"] = counts[alarm_label]
        counts["alerts_zscore"] = counts[alert_label]

        counts["year_month"] = counts["year_month"]

    # -----------------------------------------
    # 5. Fixed Minimal Calculation
    # -----------------------------------------
    if method_type == "event":
        # Minimal already computed via classification
        counts["minimal_percentile"] = counts[minimal_label]
        counts["minimal_tukey"] = counts[minimal_label]
        counts["minimal_zscore"] = counts[minimal_label]

    else:
        counts["minimal_percentile"] = (
                total_units
                - (counts["alarms_percentile"] + counts["alerts_percentile"])
        )

        counts["minimal_tukey"] = (
                total_units
                - (counts["alarms_tukey"] + counts["alerts_tukey"])
        )

        counts["minimal_zscore"] = (
                total_units
                - (counts["alarms_zscore"] + counts["alerts_zscore"])
        )

    # -----------------------------------------
    # 6. Percentages (Fixed Denominator)
    # -----------------------------------------
    counts["alarm_percentile_pct"] = (
        counts["alarms_percentile"] / total_units * 100
    )

    counts["alert_percentile_pct"] = (
        counts["alerts_percentile"] / total_units * 100
    )

    counts["minimal_percentile_pct"] = (
        counts["minimal_percentile"] / total_units * 100
    )

    counts["alarm_tukey_pct"] = (
        counts["alarms_tukey"] / total_units * 100
    )

    counts["alert_tukey_pct"] = (
        counts["alerts_tukey"] / total_units * 100
    )

    counts["minimal_tukey_pct"] = (
        counts["minimal_tukey"] / total_units * 100
    )

    counts["alarm_zscore_pct"] = (
            counts["alarms_zscore"] / total_units * 100
    )

    counts["alert_zscore_pct"] = (
            counts["alerts_zscore"] / total_units * 100
    )

    counts["minimal_zscore_pct"] = (
            counts["minimal_zscore"] / total_units * 100
    )

    numeric_cols = counts.select_dtypes(include="number").columns
    counts[numeric_cols] = counts[numeric_cols].round(2)

    # -----------------------------------------
    # 7. Metadata
    # -----------------------------------------
    counts["indicator"] = indicator_value
    counts["date"] = counts["year_month"].dt.to_timestamp()

    return counts
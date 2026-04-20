import sys
import os
# Ensure project root is accessible (so src imports work)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def get_percentile_explanation(indicator, alert_pct, alarm_pct):
    direction = INDICATOR_DIRECTION.get(indicator, "lower")

    if direction == "upper":
        return f"""
**Percentile method — Upper-tail (high values = risk)**  

Ranks all monthly values from lowest to highest.  

- **Alert**: triggered when values exceed the **{alert_pct}th percentile**  
- **Alarm**: triggered when values exceed the **{alarm_pct}th percentile**  

👉 Interpretation: unusually **high values** indicate worsening conditions.  

**Example:** If alarm = {alarm_pct}, a month is flagged only if it is higher than {alarm_pct}% of historical observations.
"""

    else:
        return f"""
**Percentile method — Lower-tail (low values = risk)**  

Ranks all monthly values from lowest to highest.  

- **Alert**: triggered when values are among the lowest **{alert_pct}%**  
- **Alarm**: triggered when values are among the lowest **{alarm_pct}%**  

👉 Interpretation: unusually **low values** indicate worsening conditions.  

**Example:** If alarm = {alarm_pct}, a month is flagged only if it is lower than {alarm_pct}% of historical observations.
"""
def get_method_description(indicator, method):

    # 1. Try indicator-specific description
    desc = METHOD_DESCRIPTIONS.get(indicator, {}).get(method)

    if desc:
        return desc

    # 2. Fallback to default method description
    return DEFAULT_METHOD_DESCRIPTIONS.get(
        method,
        "No description available."
    )

from threshold_storage import (
    load_default_thresholds,
    get_active_thresholds,
    save_override,
    reset_override
)

from classification_engine import apply_thresholds
from spatial_recalculation import recalculate_thresholds
from src.classification_matrix import compute_unit_month_classification_matrix
from src.config import (
    INDICATOR_DIRECTION,
    PRICE_INDICATORS,
    CLIMATE_INDICATORS,
    BASELINE_METHODS,
    COUNTRY_CONFIG,
    SEASONAL_DEFINITIONS,
    DEFAULT_BASELINE,
    INDICATOR_ALLOWED_BASELINES,
    INDICATOR_ALLOWED_METHODS,   # 🔥 ADD THIS
    EVENT_THRESHOLDS,
    METHOD_DESCRIPTIONS,
    DEFAULT_METHOD_DESCRIPTIONS,
    SPI_TRUE_THRESHOLDS,
    FLOOD_INDICATORS,
    SHOCK_INDICATORS
)
from src.event_loader import load_reference_events, get_reference_events

@st.cache_data
def cached_classification_matrix(df, indicator, alarm, alert, units, start, end, unit_col):

    return compute_unit_month_classification_matrix(
        df=df,
        unit_col=unit_col,
        indicator_col="indicator",
        value_col="value",
        indicator_value=indicator,
        alarm_threshold=alarm,
        alert_threshold=alert,
        selected_units=units,
        start_date=start,
        end_date=end,
        add_proportions=True
    )

# ---------------------------------------------------
# Page Config
# ---------------------------------------------------
st.set_page_config(layout="wide")
st.title("RAAP Threshold Setting dashboard")


# ---------------------------------------------------
# Load Data
# ---------------------------------------------------
@st.cache_data
def load_unit_month():
    path = "outputs/unit_month_values.parquet"

    if not os.path.exists(path):
        st.error("Run main.py first to generate unit_month_values.")
        st.stop()

    df = pd.read_parquet(path)

    # 🔹 Ensure date column exists for charts
    if "year_month" in df.columns:
        df["date"] = df["year_month"].dt.to_timestamp()

    return df

@st.cache_data
def cached_events():
    return load_reference_events()

events_df = cached_events()

@st.cache_data
def load_thresholds_file():
    path = "outputs/thresholds_results.csv"
    if not os.path.exists(path):
        return None
    return pd.read_csv(path)


df_unit_month = load_unit_month()
df_thresholds_file = load_thresholds_file()

# ---------------------------------------------------
# Sidebar Controls
# ---------------------------------------------------
st.sidebar.header("Controls")

# ---------------------------------------------------
# Country Selector
# ---------------------------------------------------

countries = sorted(df_unit_month["country"].unique())

selected_country = st.sidebar.selectbox(
    "Country",
    countries
)

unit_col = "adm1_name"

country_df = df_unit_month[
    df_unit_month["country"] == selected_country
]

# -----------------------------------------
# 🔥 NEW: GROUP FILTER (ADD HERE)
# -----------------------------------------
# -----------------------------------------
# 🔥 GROUP FILTER (SAFE VERSION)
# -----------------------------------------
if "group" in country_df.columns:

    country_groups = sorted(
        country_df["group"].dropna().unique()
    )

    selected_region = st.sidebar.selectbox(
        "Select Region (Group)",
        ["All"] + country_groups
    )

    if selected_region == "All":
        filtered_units = sorted(country_df["adm1_name"].unique())
    else:
        filtered_units = sorted(
            country_df[
                country_df["group"] == selected_region
            ]["adm1_name"].unique()
        )

else:
    # 🔥 fallback (no grouping available)
    selected_region = "All"
    filtered_units = sorted(country_df["adm1_name"].unique())


# 🔥 USE THIS INSTEAD OF all_units
all_units = filtered_units

default_thresholds_df = load_default_thresholds()

from src.config import INDICATOR_GROUPS

# ---------------------------------------------------
# Indicator Group Selector
# ---------------------------------------------------
selected_group = st.sidebar.selectbox(
    "Risk factor",
    list(INDICATOR_GROUPS.keys())
)

# ---------------------------------------------------
# Filter indicators based on group
# ---------------------------------------------------
group_indicators = INDICATOR_GROUPS[selected_group]

available_indicators = sorted([
    ind for ind in country_df["indicator"].unique()
    if ind in group_indicators
])

# Safety check
if not available_indicators:
    st.sidebar.warning("No indicators available for this category.")
    st.stop()

indicator = st.sidebar.selectbox(
    "Risk indicator",
    available_indicators
)

# ---------------------------------------------------
# Price Baseline Selector (ONLY for price indicators)
# ---------------------------------------------------

from src.config import INDICATOR_ALLOWED_BASELINES

baseline_method = None

allowed_baselines = INDICATOR_ALLOWED_BASELINES.get(
    indicator,
    [DEFAULT_BASELINE]
)

# Only show selector if more than one option
if len(allowed_baselines) > 1:

    baseline_method = st.sidebar.selectbox(
        "Measure",
        allowed_baselines
    )

else:
    baseline_method = allowed_baselines[0]

# ---------------------------------------------------
# Method Selection (Dynamic per indicator)
# ---------------------------------------------------

from src.config import SPI_TRUE_INDICATORS

if indicator in SPI_TRUE_INDICATORS:
    available_methods = ["spi_true"]
else:
    available_methods = INDICATOR_ALLOWED_METHODS.get(
        indicator,
        ["percentile"]
    )

# Label
st.sidebar.markdown("**Method**")

# Caption
st.sidebar.caption(
    "Choose how alert and alarm levels are calculated. "
    "Each method has different assumptions."
)

# Dropdown
method = st.sidebar.selectbox(
    "",
    available_methods,
    label_visibility="collapsed"
)

# -----------------------------------------
# 🔥 SHOW ACTIVE SIGNAL TYPE
# -----------------------------------------
if method == "zscore_true":
    st.sidebar.success("Using standardized signal (Z-score)")
elif method == "spi_true":
    st.sidebar.success("Using SPI standardized signal")
else:
    st.sidebar.info("Using anomaly-based signal")

# 🔹 spacing
st.sidebar.markdown("---")

# 🔹 explanation RIGHT BELOW method
with st.sidebar.expander("ℹ️ About this method", expanded=False):
    if method == "percentile":
        direction = INDICATOR_DIRECTION.get(indicator, "lower")

        default_alert = 50
        default_alarm = 25 if direction == "lower" else 75

        explanation = get_percentile_explanation(
            indicator,
            alert_pct if "alert_pct" in locals() else default_alert,
            alarm_pct if "alarm_pct" in locals() else default_alarm
        )
    else:
        explanation = get_method_description(indicator, method)

    st.markdown(explanation)

if method == "spi_true":

    if selected_group == "Flood":
        spi_mode = "Flood"

    elif selected_group == "Climate":
        spi_mode = "Drought"

    else:
        spi_mode = "Both"

# 🔹 Retention Mode Selector (ADDITIONAL ONLY)
retention_mode = st.sidebar.selectbox(
    "Threshold sensitivity mode",
    ["Sensitive (All Months)", "Robust (≥40% Retention)"],
    help="ⓘ Controls how easily the system flags warnings across areas."
)

# 🔹 NEW: Time Frame Selector (ADDITIONAL ONLY)
season_scope = "All Months"

if df_thresholds_file is not None and "season_scope" in df_thresholds_file.columns:

    available_seasons = (
        df_thresholds_file[
            df_thresholds_file["indicator"] == indicator
        ]["season_scope"]
        .dropna()
        .unique()
        .tolist()
    )

    if available_seasons:
        season_scope = st.sidebar.selectbox(
            "Time Frame",
            available_seasons
        )

# ---------------------------------------------------
# Season Month Mapping (Display Logic Only)
# ---------------------------------------------------
indicator_seasons = SEASONAL_DEFINITIONS.get(indicator, {"All Months": None})

selected_season_months = indicator_seasons.get(season_scope)

if selected_season_months is None:
    selected_season_months = list(range(1, 13))


view_mode = st.sidebar.selectbox(
    "Geographical Scope (View)",
    ["National (all units)", "Selected Units"],
    index=0,   # 🔥 THIS LINE FIXES IT
    help = "ⓘ Select which units are shown for review in the dashboard."
)

default_units = all_units if len(all_units) <= 20 else all_units[:20]

selected_units = st.sidebar.multiselect(
    "Selected Units",
    all_units,
    default=default_units
)

if len(selected_units) == 0:
    st.sidebar.warning("Select at least one province.")

baseline_mode = st.sidebar.radio(
    "Geographical Scope (threshold)",
    ["Fixed National", "Dynamic (Selected Units)"],
    help = "ⓘ Recalculate thresholds for selected units, otherwise, use the fixed national threshold."

)

display_mode = st.sidebar.radio(
    "Display Mode",
    ["Count", "Percentage"],
    help = "ⓘ Change how warnings are presented in the charts"
)

show_events = st.sidebar.checkbox(
    "Show Reference Events",
    value=True
)

# ---------------------------------------------------
# Filter Indicator Data
# ---------------------------------------------------
df_filtered = country_df[
    country_df["indicator"] == indicator
].copy()

# -----------------------------------------
# 🔥 USE Z-SCORE VALUES FOR ZSCORE_TRUE
# -----------------------------------------
if method == "zscore_true":
    if "value_zscore" not in df_filtered.columns:
        st.error("Z-score values not found.")
        st.stop()

    df_filtered.loc[:, "value"] = df_filtered["value_zscore"]


# Apply baseline filter only for price indicators
if baseline_method is not None and "baseline_method" in df_filtered.columns:

    df_filtered = df_filtered[
        df_filtered["baseline_method"] == baseline_method
    ]

# 🔥 USER OVERRIDE CONTROL
user_override_active = False

# ---------------------------------------------------
# 🔥 EARLY USER CHANGE DETECTION (FIX)
# ---------------------------------------------------
if method in ["percentile", "tukey"]:

    direction = INDICATOR_DIRECTION.get(indicator, "lower")

    if direction == "lower":
        default_alarm_pct = 25
        default_alert_pct = 50
    else:
        default_alarm_pct = 75
        default_alert_pct = 50

    # Use session state if available
    alarm_pct_temp = st.session_state.get("alarm_pct", default_alarm_pct)
    alert_pct_temp = st.session_state.get("alert_pct", default_alert_pct)

    if method == "percentile":
        user_override_active = (
                alarm_pct_temp != default_alarm_pct or
                alert_pct_temp != default_alert_pct
        )
    else:
        user_override_active = (
                alarm_pct_temp != default_alarm_pct
        )

# ---------------------------------------------------
# EVENT INDICATORS → FIXED THRESHOLDS
# ---------------------------------------------------
if method == "categorical":

    thresholds = EVENT_THRESHOLDS.get(indicator)

    if thresholds is None:
        st.error(f"No event thresholds configured for {indicator}")
        st.stop()

    alert_threshold = thresholds["alert"]
    alarm_threshold = thresholds["alarm"]

# ---------------------------------------------------
# NORMAL INDICATORS → EXISTING LOGIC
# ---------------------------------------------------
else:

    # -----------------------------------------
    # 🔥 TRUE SPI THRESHOLDS (CONFIG-DRIVEN)
    # -----------------------------------------
    if method == "spi_true":

        thresholds = SPI_TRUE_THRESHOLDS.get(
            indicator,
            SPI_TRUE_THRESHOLDS["default"]
        )

        # -----------------------------
        # Drought (default)
        # -----------------------------
        alert_threshold = thresholds["alert"]
        alarm_threshold = thresholds["alarm"]

    elif method == "zscore_true":

        from src.config import ZSCORE_TRUE_THRESHOLDS, INDICATOR_DIRECTION, PRICE_INDICATORS

        # -----------------------------------------
        # 🔥 SELECT THRESHOLDS
        # -----------------------------------------
        if indicator in PRICE_INDICATORS:
            thresholds = ZSCORE_TRUE_THRESHOLDS["price_default"]
        else:
            thresholds = ZSCORE_TRUE_THRESHOLDS.get(
                indicator,
                ZSCORE_TRUE_THRESHOLDS["default"]
            )

        direction = INDICATOR_DIRECTION.get(indicator, "upper")

        alert_z = thresholds["alert"]
        alarm_z = thresholds["alarm"]

        # -----------------------------------------
        # 🔥 APPLY DIRECTION
        # -----------------------------------------
        if direction == "lower":
            # Ensure negative thresholds
            alert_threshold = -abs(alert_z)
            alarm_threshold = -abs(alarm_z)

            # Ensure correct ordering
            alert_threshold = max(alert_threshold, alarm_threshold)  # closer to 0
            alarm_threshold = min(alert_threshold, alarm_threshold)  # more extreme

        else:
            # Ensure positive thresholds
            alert_threshold = abs(alert_z)
            alarm_threshold = abs(alarm_z)

            # Ensure correct ordering
            alert_threshold = min(alert_threshold, alarm_threshold)
            alarm_threshold = max(alert_threshold, alarm_threshold)

    # 👇 EXISTING BLOCK CONTINUES 👇
    elif df_thresholds_file is not None and "retention_filter" in df_thresholds_file.columns:

        retention_key = "none" if retention_mode == "Sensitive (All Months)" else ">=40%"

        if "season_scope" in df_thresholds_file.columns:
            threshold_row = df_thresholds_file[
                (df_thresholds_file["indicator"] == indicator) &
                (df_thresholds_file["country"] == selected_country) &  # 🔥 ADD
                (df_thresholds_file["retention_filter"] == retention_key) &
                (df_thresholds_file["season_scope"] == season_scope) &
                (df_thresholds_file["baseline_method"] == baseline_method)  # 🔥 FORCE
                ]

            # Filter by country if column exists
            if "country" in df_thresholds_file.columns:
                threshold_row = threshold_row[
                    threshold_row["country"] == selected_country
                ]

            # 🔴 IMPORTANT: Filter by baseline for price indicators
            if baseline_method is not None and "baseline_method" in df_thresholds_file.columns:
                threshold_row = threshold_row[
                    threshold_row["baseline_method"] == baseline_method
                ]
        else:
            threshold_row = df_thresholds_file[
                (df_thresholds_file["indicator"] == indicator) &
                (df_thresholds_file["retention_filter"] == retention_key)
            ]

        if not threshold_row.empty:
            row = threshold_row.iloc[0]

            if not user_override_active:

                if method == "percentile":
                    alarm_threshold = row["alarm_percentile"]
                    alert_threshold = row["alert_percentile"]

                elif method == "tukey":
                    alarm_threshold = row["alarm_tukey"]
                    alert_threshold = row["alert_tukey"]

            # 🔥 Z-score should ALWAYS load independently
            if method == "zscore":
                alarm_threshold = row["alarm_zscore"]
                alert_threshold = row["alert_zscore"]

            # 🔥 ADD THIS RIGHT HERE
            if method == "zscore":
                if pd.isna(alarm_threshold) or pd.isna(alert_threshold):
                    st.warning("Z-score thresholds not available for this configuration.")
                    st.stop()

        else:
            alarm_threshold, alert_threshold = get_active_thresholds(indicator, method)


    else:

        if not user_override_active:
            alarm_threshold, alert_threshold = get_active_thresholds(indicator, method)

# ---------------------------------------------------
# Dynamic Threshold Recalculation (Selected Units)
# ---------------------------------------------------

if baseline_mode == "Dynamic (Selected Units)" and len(selected_units) > 0:

    # Only recompute if subset of provinces selected
    if len(selected_units) < len(all_units):

        try:

            recalculated = recalculate_thresholds(
                df_filtered,
                indicator,
                selected_units
            )

            if method in recalculated:
                if not user_override_active:
                    alarm_threshold = recalculated[method]["alarm"]
                    alert_threshold = recalculated[method]["alert"]

                st.info("Dynamic thresholds recomputed using Selected Units.")

        except Exception as e:

            st.warning(f"Dynamic threshold computation failed: {e}")


# ---------------------------------------------------
# Extract BOTH Seasonal Thresholds (for display merge)
# ---------------------------------------------------

def get_season_thresholds(season_name):
    if df_thresholds_file is None:
        return alarm_threshold, alert_threshold

    retention_key = "none" if retention_mode == "Sensitive (All Months)" else ">=40%"

    row = df_thresholds_file[
        (df_thresholds_file["indicator"] == indicator) &
        (df_thresholds_file["retention_filter"] == retention_key) &
        (df_thresholds_file["season_scope"] == season_name)
    ]

    if not row.empty:
        row = row.iloc[0]
        if method == "percentile":
            return row["alarm_percentile"], row["alert_percentile"]
        else:
            return row["alarm_tukey"], row["alert_tukey"]

    return alarm_threshold, alert_threshold


# ---------------------------------------------------
# Method Description
# ---------------------------------------------------
#st.subheader("Method Description")

#description = get_method_description(indicator, method)

#if description:
#    st.info(description)
st.subheader("Interpretation Note")
st.info("Thresholds reflect how unusual current conditions are compared to historical patterns.")

st.markdown(f"### Suggested Thresholds ({method.lower()})")
row1_col1, row1_col2 = st.columns([1, 1])
row2_col1, row2_col2 = st.columns([1, 1])

# ---------------------------------------------------
# 🔥 SAFETY DEFAULT (FIX NameError)
# ---------------------------------------------------
if "alarm_threshold" not in locals():
    alarm_threshold, alert_threshold = get_active_thresholds(indicator, method)

# -----------------------------------------
# SPI DISPLAY FIX (UI ONLY)
# -----------------------------------------
display_alarm = alarm_threshold
display_alert = alert_threshold

if method == "spi_true" and spi_mode == "Flood":
    display_alarm = abs(alarm_threshold)
    display_alert = abs(alert_threshold)

# controls continue ALWAYS

# -----------------------------------------
# NEW: Percentile inputs (direction-aware defaults)
# -----------------------------------------
if method in ["percentile", "tukey"]:

    direction = INDICATOR_DIRECTION.get(indicator, "lower")

    # 🔥 Smart defaults based on direction
    if direction == "lower":
        default_alarm_pct = 25
        default_alert_pct = 50
    else:
        default_alarm_pct = 75
        default_alert_pct = 50

    with row1_col1:
        sub_col1, _ = st.columns([1, 2])  # 🔥 shrink input
        with sub_col1:
            alarm_pct = st.number_input(
                "Alarm Percentile",
                min_value=1,
                max_value=99,
                value=default_alarm_pct,
                step=1,
                key="alarm_pct"  # 🔥 ADD THIS
            )

    if method == "percentile":
        with row2_col1:
            sub_col2, _ = st.columns([1, 2])  # Adjust ratio if you want smaller/larger input
            with sub_col2:
                alert_pct = st.number_input(
                    "Alert Percentile",
                    min_value=1,
                    max_value=99,
                    value=default_alert_pct,
                    step=1,
                    key="alert_pct"  # 🔥 ADD THIS
                )
    else:
        # Tukey → no alert input
        alert_pct = default_alert_pct  # keep for backend consistency

    if method == "tukey":
        st.caption(
            "ⓘ Tukey thresholds are driven by the Alarm Percentile only "
            "(it defines both Q1 and Q3 through the distribution spread)."
        )

    if method == "percentile":
        user_changed = (
                alarm_pct != default_alarm_pct or
                alert_pct != default_alert_pct
        )
    else:
        # Tukey → only alarm matters
        user_changed = alarm_pct != default_alarm_pct

    if user_changed:
        user_override_active = True

        try:
            recalculated = recalculate_thresholds(
                df_filtered,
                indicator,
                selected_units if baseline_mode == "Dynamic (Selected Units)" else None,
                alarm_pct=alarm_pct,
                alert_pct=alert_pct
            )

            direction = INDICATOR_DIRECTION.get(indicator, "lower")

            if method == "percentile":
                alarm_threshold = recalculated["percentile"]["alarm"]
                alert_threshold = recalculated["percentile"]["alert"]

            elif method == "tukey":
                alarm_threshold = recalculated["tukey"]["alarm"]
                alert_threshold = recalculated["tukey"]["alert"]

            # 🔥 UPDATE DISPLAY VALUES AFTER RECALCULATION
            display_alarm = alarm_threshold
            display_alert = alert_threshold

            # 🔥 Fix ordering for upper-tail indicators
            if direction == "upper":
                alarm_threshold, alert_threshold = (
                    max(alarm_threshold, alert_threshold),
                    min(alarm_threshold, alert_threshold)
                )

            st.info("Thresholds dynamically recalculated.")

        except Exception as e:
            st.warning(f"Recalculation failed: {e}")
            st.stop()

    with row1_col2:
        st.metric(
            "Alarm Threshold",
            f"{round(display_alarm, 2)}"
        )

    with row2_col2:
        st.metric(
            "Alert Threshold",
            f"{round(display_alert, 2)}"
        )

# -----------------------------------------
# EXISTING: Tukey / Z-score / Override
# -----------------------------------------
else:

    # 🔥 Row 1 → Alarm (UI input)
    with row1_col1:
        user_alarm = st.number_input(
            "Alarm Threshold",
            value=float(display_alarm)
        )

    with row1_col2:
        if st.button("Reset to Default"):
            reset_override(indicator, method)
            st.rerun()

    # 🔥 Row 2 → Alert (UI input)
    with row2_col1:
        user_alert = st.number_input(
            "Alert Threshold",
            value=float(display_alert)
        )

    with row2_col2:
        if st.button("Apply & Save Threshold"):

            # 🔥 Convert back to internal SPI logic BEFORE saving
            if method == "spi_true" and spi_mode == "Flood":
                save_override(
                    indicator,
                    method,
                    -abs(user_alarm),
                    -abs(user_alert)
                )
            else:
                save_override(
                    indicator,
                    method,
                    user_alarm,
                    user_alert
                )

            st.success("Threshold saved.")

    # -----------------------------------------
    # 🔥 Convert BACK to internal thresholds (for use downstream)
    # -----------------------------------------
    if method == "spi_true" and spi_mode == "Flood":
        alarm_threshold = -abs(user_alarm)
        alert_threshold = -abs(user_alert)
    else:
        alarm_threshold = user_alarm
        alert_threshold = user_alert

# ---------------------------------------------------
# Apply Classification (Season-Aware Only When Needed)
# ---------------------------------------------------

units_for_calc = all_units if view_mode == "National (all units)" else selected_units

if season_scope == "All Months":

    classified_df, counts = apply_thresholds(
        df_filtered,
        units_for_calc,
        alarm_threshold,
        alert_threshold,
        indicator
    )

else:

    planting_alarm, planting_alert = get_season_thresholds("Planting (Mar–Jun)")
    off_alarm, off_alert = get_season_thresholds("Off-Season (Jul–Feb)")

    # Run both classifications
    classified_planting, counts_planting = apply_thresholds(
        df_filtered,
        units_for_calc,
        planting_alarm,
        planting_alert,
        indicator
    )

    classified_off, counts_off = apply_thresholds(
        df_filtered,
        units_for_calc,
        off_alarm,
        off_alert,
        indicator
    )

    counts_planting["Month"] = counts_planting["date"].dt.month
    counts_off["Month"] = counts_off["date"].dt.month

    counts = counts_planting.copy()

    for idx, row in counts.iterrows():
        month = row["Month"]

        # If month belongs to off-season, replace with off-season result
        if month not in [3, 4, 5, 6]:
            match = counts_off[counts_off["date"] == row["date"]]
            if not match.empty:
                counts.loc[idx, ["Alarm","Alert","Minimal",
                                 "Alarm_pct","Alert_pct","Minimal_pct"]] = \
                    match[["Alarm","Alert","Minimal",
                           "Alarm_pct","Alert_pct","Minimal_pct"]].values[0]

    classified_df = classified_planting

# ---------------------------------------------------
# APPLY SPI DISPLAY LOGIC (SAFE FIX)
# ---------------------------------------------------
if method == "spi_true" and spi_mode != "Both":

    classified_df = classified_df.copy()

    if spi_mode == "Drought":
        classified_df.loc[
            classified_df["signal_type"] == "Flood",
            "classification"
        ] = "Minimal"

    elif spi_mode == "Flood":
        classified_df.loc[
            classified_df["signal_type"] == "Drought",
            "classification"
        ] = "Minimal"

    # ---------------------------------------------------
    # 🔥 FULL GRID COUNTS (FIX FOR NO DATA)
    # ---------------------------------------------------

    # Create full grid of units × months
    all_months = pd.period_range(
        classified_df["year_month"].min(),
        classified_df["year_month"].max(),
        freq="M"
    )

    full_index = pd.MultiIndex.from_product(
        [units_for_calc, all_months],
        names=[unit_col, "year_month"]
    )

    full_df = (
        classified_df
        .set_index([unit_col, "year_month"])
        .reindex(full_index)
        .reset_index()
    )

    # Fill missing classifications as "No data"
    full_df["classification"] = full_df["classification"].fillna("No data")

    # Now compute counts
    counts = (
        full_df.groupby(["year_month", "classification"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )

    for col in ["Alarm", "Alert", "Minimal", "No data"]:
        if col not in counts.columns:
            counts[col] = 0

    counts["Alarm_pct"] = counts["Alarm"] / len(units_for_calc) * 100
    counts["Alert_pct"] = counts["Alert"] / len(units_for_calc) * 100
    counts["Minimal_pct"] = counts["Minimal"] / len(units_for_calc) * 100
    counts["No data_pct"] = counts["No data"] / len(units_for_calc) * 100

    counts["date"] = counts["year_month"].dt.to_timestamp()

# ---------------------------------------------------
# Time Slider
# ---------------------------------------------------
st.subheader("Time Window")

if counts.empty:
    st.warning("No data available for selected configuration.")
    st.stop()

min_date = counts["date"].min().to_pydatetime()
max_date = counts["date"].max().to_pydatetime()

start_date, end_date = st.slider(
    "Select Time Range",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
    format="YYYY-MM"
)

start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

counts = counts[
    (counts["date"] >= start_date) &
    (counts["date"] <= end_date)
]

# ---------------------------------------------------
# Structural Summary Panel (FULLY PRESERVED)
# ---------------------------------------------------
st.subheader("Warning Summary")

# 🔹 TWG Explanatory Info Box
st.info(
    f"ℹ️ **Interpretation Note:** Thresholds reflect "
    f"**{season_scope}** | Retention Mode: **{retention_mode}**. "
    "Structural summary below reflects the actual Selected Units "
    "and time window."
)

# 🔥 ADD HERE
if method == "zscore_true":
    st.caption(
        "ⓘ Z-score uses the full historical distribution (no data filtering applied)."
    )

if len(units_for_calc) == 0:
    st.warning("Please select at least one province.")
else:

    # Only apply for SPI
    # 🔥 SPI-AWARE MATRIX INPUT (FINAL CLEAN)
    matrix_input_df = df_filtered.copy()

    # 🔥 Apply SPI interpretation BEFORE matrix classification
    if method == "spi_true" and spi_mode != "Both":

        matrix_input_df = matrix_input_df.copy()

        # Create signal_type (same logic as classified_df)
        matrix_input_df["signal_type"] = matrix_input_df["value"].apply(
            lambda x: "Drought" if x <= 0 else "Flood"
        )

        if spi_mode == "Drought":
            # Opposite signal → force Minimal
            matrix_input_df.loc[
                matrix_input_df["signal_type"] == "Flood",
                "value"
            ] = 0  # will become Minimal

        elif spi_mode == "Flood":
            matrix_input_df.loc[
                matrix_input_df["signal_type"] == "Drought",
                "value"
            ] = 0

    # Use matrix_input_df instead of df_filtered
    matrix_summary = cached_classification_matrix(
        matrix_input_df,
        indicator,
        alarm_threshold,
        alert_threshold,
        units_for_calc,
        start_date,
        end_date,
        unit_col
    )

    if matrix_summary.empty or "% Alarm" not in matrix_summary.columns:
        st.warning("Insufficient data to compute proportions.")
    else:

        alarm_col = matrix_summary["% Alarm"].str.replace("%", "", regex=False).astype(float)
        alert_col = matrix_summary["% Alert"].str.replace("%", "", regex=False).astype(float)

        alarm_min, alarm_max = alarm_col.min(), alarm_col.max()
        alert_min, alert_max = alert_col.min(), alert_col.max()

        # -------- Dynamic Retention --------
        # -------- Dynamic Retention (Direction-Aware) --------
        df_retention = df_filtered[
            df_filtered[unit_col].isin(units_for_calc)
        ].copy()

        df_retention["year_month_date"] = df_retention["year_month"].dt.to_timestamp()

        df_retention = df_retention[
            (df_retention["year_month_date"] >= start_date) &
            (df_retention["year_month_date"] <= end_date)
            ]

        total_count = df_retention["value"].count()

        direction = INDICATOR_DIRECTION.get(indicator, "lower")

        # Climate indicators
        if indicator in CLIMATE_INDICATORS:
            filtered_count = df_retention[df_retention["value"] < 100]["value"].count()

        # Flood indicators → NO FILTERING BUT EXPLICIT
        elif indicator in FLOOD_INDICATORS:
            filtered_count = total_count

        # Market indicators
        elif indicator in PRICE_INDICATORS:

            if method == "zscore_true":
                # 🔥 NO FILTERING for Z-score
                filtered_count = total_count
            else:
                # Existing logic for anomaly-based methods
                if direction == "upper":
                    filtered_count = df_retention[df_retention["value"] > 0]["value"].count()
                elif direction == "lower":
                    filtered_count = df_retention[df_retention["value"] < 0]["value"].count()
                else:
                    filtered_count = total_count

        else:
            filtered_count = total_count

        if total_count > 0:
            overall_percent = round(filtered_count / total_count * 100, 1)
            overall_display = f"{filtered_count} ({overall_percent}%)"
        else:
            overall_display = "N/A"
            overall_percent = None

        # ---- Monthly retention (consistent with spatial_percentiles logic) ----

        if indicator in CLIMATE_INDICATORS:

            monthly_stats = (
                df_retention
                .groupby("year_month")["value"]
                .agg(
                    total="count",
                    filtered=lambda x: (x < 100).sum()
                )
                .reset_index()
            )

        elif indicator in FLOOD_INDICATORS:

            monthly_stats = (

                df_retention

                .groupby("year_month")["value"]

                .agg(total="count", filtered="count")

                .reset_index()

            )

        elif indicator in PRICE_INDICATORS:

            if method == "zscore_true":

                monthly_stats = (

                    df_retention

                    .groupby("year_month")["value"]

                    .agg(total="count", filtered="count")

                    .reset_index()

                )

            else:

                if direction == "upper":

                    monthly_stats = (

                        df_retention

                        .groupby("year_month")["value"]

                        .agg(

                            total="count",

                            filtered=lambda x: (x > 0).sum()

                        )

                        .reset_index()

                    )

                elif direction == "lower":

                    monthly_stats = (

                        df_retention

                        .groupby("year_month")["value"]

                        .agg(

                            total="count",

                            filtered=lambda x: (x < 0).sum()

                        )

                        .reset_index()

                    )

                else:

                    monthly_stats = (

                        df_retention

                        .groupby("year_month")["value"]

                        .agg(total="count", filtered="count")

                        .reset_index()

                    )
        else:

            monthly_stats = (
                df_retention
                .groupby("year_month")["value"]
                .agg(total="count", filtered="count")
                .reset_index()
            )

        if not monthly_stats.empty:
            monthly_stats["pct"] = (
                    monthly_stats["filtered"] /
                    monthly_stats["total"] * 100
            )
            min_pct = round(monthly_stats["pct"].min(), 1)
            max_pct = round(monthly_stats["pct"].max(), 1)
            proportion_range = f"{min_pct}% - {max_pct}%"
        else:
            proportion_range = "N/A"
            min_pct = None

        summary_df = pd.DataFrame({
            "Metric": [
                "Threshold",
                "Data Points Used (Filtered)",
                "Monthly % Retained Range",
                "Warning Frequency (range across all units)"
            ],
            "Alarm": [
                f"{round(display_alarm, 2)}",
                overall_display,
                proportion_range,
                f"{int(alarm_min)}% - {int(alarm_max)}%"
            ],
            "Alert": [
                f"{round(display_alert, 2)}",
                overall_display,
                proportion_range,
                f"{int(alert_min)}% - {int(alert_max)}%"
            ]
        })

        # -------- Coloring --------
        def retention_color(val):
            try:
                if "(" in val:
                    pct = float(val.split("(")[1].replace("%)", ""))
                else:
                    pct = float(val.split("%")[0])
            except:
                return ""

            if pct < 60:
                return "background-color:#8B0000;color:white;font-weight:bold"
            elif pct < 80:
                return "background-color:#FF8C00;color:black;font-weight:bold"
            else:
                return "background-color:#006400;color:white;font-weight:bold"

        def highlight_rows(row):
            if row["Metric"] in ["Data Points Used (Filtered)", "Monthly % Retained Range"]:
                return ["",
                        retention_color(row["Alarm"]),
                        retention_color(row["Alert"])]
            return ["", "", ""]

        styled_summary = summary_df.style.apply(highlight_rows, axis=1)
        st.dataframe(styled_summary, width="stretch")

        if min_pct is not None and min_pct < 60:
            st.warning(
                "⚠ Some months have retention below 60%. "
                "Threshold stability may be affected."
            )


# ---------------------------------------------------
# Aggregated Stacked Chart (Season-Aware Display)
# ---------------------------------------------------
st.subheader("Warnings for all selected units (over time)")

# 🔥 ADD THIS HERE
if indicator.startswith("conflict"):
    st.caption("Note: Missing unit-months are classified as 'No data' and shown in gray.")

# Existing caption
st.caption(
    "Highlighted months reflect the selected seasonal scope. "
    "Other months remain visible but are visually softened."
)

# SPI-specific explanation
if method == "spi_true":

    if spi_mode == "Both":
        st.caption(
            "All SPI signals are shown (both drought and flood conditions)."
        )

    else:
        st.caption(
            "Gray = Opposite signal is treated as Minimal "
            "(e.g. drought periods appear as Minimal in flood view, and vice versa)."
        )

if method == "spi_true" and spi_mode == "Both":

    # Split data
    drought_df = classified_df[classified_df["signal_type"] == "Drought"]
    flood_df = classified_df[classified_df["signal_type"] == "Flood"]

    # Recompute counts separately
    def compute_counts(df_sub):
        c = (
            df_sub.groupby(["year_month", "classification"])
            .size()
            .unstack(fill_value=0)
            .reset_index()
        )
        for col in ["Alarm", "Alert", "Minimal", "No data"]:
            if col not in c.columns:
                c[col] = 0
        c["date"] = c["year_month"].dt.to_timestamp()
        return c


    counts_drought = compute_counts(drought_df)
    counts_flood = compute_counts(flood_df)

    # Apply time filter (no nested condition needed)
    counts_drought = counts_drought[
        (counts_drought["date"] >= start_date) &
        (counts_drought["date"] <= end_date)
        ]

    counts_flood = counts_flood[
        (counts_flood["date"] >= start_date) &
        (counts_flood["date"] <= end_date)
        ]

fig = go.Figure()

# ---------------------------------------------------
# SPECIAL CASE: SPI BOTH → split drought vs flood
# ---------------------------------------------------
if method == "spi_true" and spi_mode == "Both":

    # Month + opacity
    counts_drought["Month"] = counts_drought["date"].dt.month
    counts_flood["Month"] = counts_flood["date"].dt.month

    opacity_drought = [
        1 if m in selected_season_months else 0.25
        for m in counts_drought["Month"]
    ]

    opacity_flood = [
        1 if m in selected_season_months else 0.25
        for m in counts_flood["Month"]
    ]

    # Display mode
    def get_y(df, col):
        return df[col] if display_mode == "Count" else df[f"{col}_pct"]

    # 🔴 Drought
    fig.add_bar(
        x=counts_drought["date"],
        y=get_y(counts_drought, "Alarm"),
        name="Drought Alarm",
        marker=dict(color="red", opacity=opacity_drought)
    )

    fig.add_bar(
        x=counts_drought["date"],
        y=get_y(counts_drought, "Alert"),
        name="Drought Alert",
        marker=dict(color="orange", opacity=opacity_drought)
    )

    # 🔵 Flood
    fig.add_bar(
        x=counts_flood["date"],
        y=get_y(counts_flood, "Alarm"),
        name="Flood Alarm",
        marker=dict(color="blue", opacity=opacity_flood)
    )

    fig.add_bar(
        x=counts_flood["date"],
        y=get_y(counts_flood, "Alert"),
        name="Flood Alert",
        marker=dict(color="lightblue", opacity=opacity_flood)
    )

# ---------------------------------------------------
# DEFAULT (existing logic)
# ---------------------------------------------------
else:

    counts["Month"] = counts["date"].dt.month

    if display_mode == "Count":
        alarm_y = counts["Alarm"]
        alert_y = counts["Alert"]
        minimal_y = counts["Minimal"]
    else:
        alarm_y = counts["Alarm_pct"]
        alert_y = counts["Alert_pct"]
        minimal_y = counts["Minimal_pct"]

    opacity_values = [
        1 if m in selected_season_months else 0.25
        for m in counts["Month"]
    ]

    if display_mode == "Count":
        no_data_y = counts["No data"]
    else:
        no_data_y = counts["No data_pct"]

    fig.add_bar(
        x=counts["date"],
        y=alarm_y,
        name="Alarm",
        marker=dict(color="red", opacity=opacity_values)
    )

    fig.add_bar(
        x=counts["date"],
        y=alert_y,
        name="Alert",
        marker=dict(color="orange", opacity=opacity_values)
    )

    fig.add_bar(
        x=counts["date"],
        y=minimal_y,
        name="Minimal",
        marker=dict(color="green", opacity=opacity_values)
    )

    fig.add_bar(
        x=counts["date"],
        y=no_data_y,
        name="No data",
        marker=dict(color="gray", opacity=opacity_values)
    )

fig.update_layout(
    barmode="stack",
    height=500,
    xaxis=dict(rangeslider=dict(visible=True), type="date")
)

# ---------------------------------------------------
# Overlay Reference Events
# ---------------------------------------------------

if show_events:

    if indicator in PRICE_INDICATORS:
        indicator_type = "price"

    elif indicator in CLIMATE_INDICATORS:
        indicator_type = "climate"

    elif indicator in FLOOD_INDICATORS:
        indicator_type = "climate"


    elif indicator in SHOCK_INDICATORS:
        indicator_type = "shock"

    else:
        indicator_type = "price"

    events = get_reference_events(
        events_df,
        selected_country,
        indicator_type
    )

    # ---------------------------------------------------
    # 🔥 SPI EVENT FILTERING (MAIN CHART)
    # ---------------------------------------------------
    if method == "spi_true":

        if "type" in events.columns:

            if spi_mode == "Drought":
                events = events[events["type"] == "drought"]

            elif spi_mode == "Flood":
                events = events[events["type"] == "flood"]

    # Convert event dates to datetime
    events["start"] = pd.to_datetime(events["start"])
    events["end"] = pd.to_datetime(events["end"])

    # Keep only events overlapping with slider window
    events = events[
        (events["start"] <= end_date) &
        (events["end"] >= start_date)
        ]

    for _, row in events.iterrows():
        fig.add_vrect(
            x0=row["start"],
            x1=row["end"],
            fillcolor="purple",
            opacity=0.15,
            line_width=0,
            annotation_text=row["event"],
            annotation_position="top left",
            annotation=dict(
                textangle=-45,
                font=dict(size=10)
            )
        )

st.plotly_chart(fig, width="stretch")


# ---------------------------------------------------
# Province Classification Matrix (Season-Aware – Chart-Matched)
# ---------------------------------------------------
show_matrix = st.checkbox(
    "Warnings for each unit over time",
    value=False   # 🔥 default checked
)

if show_matrix and len(units_for_calc) > 0:

    matrix = matrix_summary.copy()

    # ---------------------------------------------------
    # Attach reference events directly to matrix columns
    # ---------------------------------------------------

    if show_events:

        if indicator in PRICE_INDICATORS:
            indicator_type = "price"
        elif indicator in CLIMATE_INDICATORS:
            indicator_type = "climate"
        else:
            indicator_type = "price"

        events = get_reference_events(
            events_df,
            selected_country,
            indicator_type
        )

        events["start"] = pd.to_datetime(events["start"])
        events["end"] = pd.to_datetime(events["end"])

        # Keep only visible window events
        events = events[
            (events["start"] <= end_date) &
            (events["end"] >= start_date)
            ]

        # Build month → event mapping
        event_months = {}

        for _, row in events.iterrows():

            months = pd.date_range(row["start"], row["end"], freq="MS")

            for m in months:
                key = m.strftime("%Y %b")
                event_months[key] = row["event"]

        # Rename columns with event label
        new_columns = []

        for col in matrix.columns:

            col_clean = str(col)

            if col_clean in event_months:
                event_name = event_months[col_clean]
                new_columns.append(f"{col_clean} ⚠")
            else:
                new_columns.append(col_clean)

        matrix.columns = new_columns

    # ---------------------------------------------------
    # Map reference events to matrix months
    # ---------------------------------------------------

    if show_events:

        if indicator in PRICE_INDICATORS:
            indicator_type = "price"
        elif indicator in CLIMATE_INDICATORS:
            indicator_type = "climate"
        else:
            indicator_type = "price"

        events = get_reference_events(
            events_df,
            selected_country,
            indicator_type
        )

        # Convert event dates to datetime
        events["start"] = pd.to_datetime(events["start"])
        events["end"] = pd.to_datetime(events["end"])

        # Keep only events overlapping with slider window
        events = events[
            (events["start"] <= end_date) &
            (events["end"] >= start_date)
            ]

        # ---------------------------------------------------
        # Build event annotation positions
        # ---------------------------------------------------

        event_annotations = []

        for _, row in events.iterrows():
            event_start = pd.to_datetime(row["start"])
            event_end = pd.to_datetime(row["end"])

            event_mid = event_start + (event_end - event_start) / 2

            event_annotations.append({
                "text": row["event"],
                "start": event_start,
                "end": event_end,
                "mid": event_mid
            })

    month_name_to_number = {
        "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
        "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
        "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
    }

    def style_matrix(col):
        col_name = str(col.name).replace("⚠", "").strip()
        parts = col_name.split()
        month_abbrev = parts[-1] if len(parts) > 1 else None
        month_num = month_name_to_number.get(month_abbrev)

        styled_col = []

        for val in col:

            # Percent columns
            if "%" in str(val):
                styled_col.append(
                    "background-color: #2b2b2b; color: white; font-weight: bold"
                )
                continue

            # Determine if this column is in selected season
            in_season = (
                month_num in selected_season_months
                if month_num is not None
                else True
            )

            # Alarm
            if val == "Alarm":
                if in_season:
                    styled_col.append("background-color: red; color: white")
                else:
                    styled_col.append("background-color: #ff9999; color: black")

            # Alert
            elif val == "Alert":
                if in_season:
                    styled_col.append("background-color: orange; color: black")
                else:
                    styled_col.append("background-color: #ffd699; color: black")

            elif val == "No data":
                styled_col.append("background-color: gray; color: white")

            # Minimal
            elif val == "Minimal":
                if in_season:
                    styled_col.append("background-color: green; color: white")
                else:
                    styled_col.append("background-color: #a6e3a1; color: black")

            else:
                styled_col.append("")

        return styled_col

    styled_matrix = matrix.style.apply(style_matrix, axis=0)

    st.dataframe(styled_matrix, width="stretch")


# ---------------------------------------------------
# National Seasonal Charts (Season-Aware Display)
# ---------------------------------------------------
if view_mode == "National (all units)":

    st.markdown("---")
    st.subheader("National Seasonal Analysis (Last 6 Years)")

    counts["Year"] = counts["date"].dt.year
    counts["Month"] = counts["date"].dt.month

    alarm_col_name = "Alarm" if display_mode == "Count" else "Alarm_pct"
    alert_col_name = "Alert" if display_mode == "Count" else "Alert_pct"

    last_6_years = sorted(counts["Year"].unique())[-6:]

    month_numbers = list(range(1, 13))
    month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    # ---------------- Alarm ----------------
    st.subheader("National Alarm – Seasonal Pattern")

    alarm_pivot = counts[counts["Year"].isin(last_6_years)] \
        .pivot(index="Month", columns="Year", values=alarm_col_name)

    alarm_pivot = alarm_pivot.reindex(month_numbers)

    fig_alarm = go.Figure()

    for year in alarm_pivot.columns:
        fig_alarm.add_trace(
            go.Scatter(
                x=month_labels,
                y=alarm_pivot[year],
                mode="lines",
                name=str(year),
                opacity=1 if season_scope == "All Months" else 0.7
            )
        )

    # Bold selected season months on x-axis
    if season_scope != "All Months":
        fig_alarm.update_xaxes(
            tickmode="array",
            tickvals=month_labels,
            ticktext=[
                f"<b>{m}</b>" if i+1 in selected_season_months else m
                for i, m in enumerate(month_labels)
            ]
        )

    fig_alarm.update_layout(height=500)
    st.plotly_chart(fig_alarm, width="stretch")

    # ---------------- Alert ----------------
    st.subheader("National Alert – Seasonal Pattern")

    alert_pivot = counts[counts["Year"].isin(last_6_years)] \
        .pivot(index="Month", columns="Year", values=alert_col_name)

    alert_pivot = alert_pivot.reindex(month_numbers)

    fig_alert = go.Figure()

    for year in alert_pivot.columns:
        fig_alert.add_trace(
            go.Scatter(
                x=month_labels,
                y=alert_pivot[year],
                mode="lines",
                name=str(year),
                opacity=1 if season_scope == "All Months" else 0.7
            )
        )

    if season_scope != "All Months":
        fig_alert.update_xaxes(
            tickmode="array",
            tickvals=month_labels,
            ticktext=[
                f"<b>{m}</b>" if i+1 in selected_season_months else m
                for i, m in enumerate(month_labels)
            ]
        )

    fig_alert.update_layout(height=500)
    st.plotly_chart(fig_alert, width="stretch")


# ---------------------------------------------------
# Download
# ---------------------------------------------------
st.download_button(
    label="Download Classification CSV",
    data=classified_df.to_csv(index=False),
    file_name="classification_output.csv"
)

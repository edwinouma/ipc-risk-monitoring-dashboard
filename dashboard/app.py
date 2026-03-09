import sys
import os

# Ensure project root is accessible (so src imports work)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

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
    SEASONAL_DEFINITIONS
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
st.title("Climatological and Price Trigger Dashboard (TWG)")


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

all_units = sorted(country_df[unit_col].unique())

default_thresholds_df = load_default_thresholds()

indicator = st.sidebar.selectbox(
    "Indicator",
    sorted(country_df["indicator"].unique())
)


# ---------------------------------------------------
# Price Baseline Selector (ONLY for price indicators)
# ---------------------------------------------------

baseline_method = None

if indicator in PRICE_INDICATORS:

    baseline_method = st.sidebar.selectbox(
        "Price Baseline Method",
        BASELINE_METHODS
    )

method = st.sidebar.radio(
    "Method",
    ["percentile", "tukey"]
)

# 🔹 Retention Mode Selector (ADDITIONAL ONLY)
retention_mode = st.sidebar.radio(
    "Retention Threshold Mode",
    ["Baseline (All Months)", "Robust (≥40% Retention)"]
)

# 🔹 NEW: Season Scope Selector (ADDITIONAL ONLY)
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
            "Season Scope",
            available_seasons
        )

# ---------------------------------------------------
# Season Month Mapping (Display Logic Only)
# ---------------------------------------------------
indicator_seasons = SEASONAL_DEFINITIONS.get(indicator, {"All Months": None})

selected_season_months = indicator_seasons.get(season_scope)

if selected_season_months is None:
    selected_season_months = list(range(1, 13))




view_mode = st.sidebar.radio(
    "Aggregation View",
    ["Selected Provinces", "National (All Provinces)"]
)

default_units = all_units if len(all_units) <= 20 else all_units[:20]

selected_units = st.sidebar.multiselect(
    "Select Provinces",
    all_units,
    default=default_units
)

if len(selected_units) == 0:
    st.sidebar.warning("Select at least one province.")

baseline_mode = st.sidebar.radio(
    "Baseline Mode",
    ["Fixed National", "Dynamic (Selected Provinces)"]
)

display_mode = st.sidebar.radio(
    "Display Mode",
    ["Count", "Percentage"]
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

# Apply baseline filter only for price indicators
if baseline_method is not None and "baseline_method" in df_filtered.columns:

    df_filtered = df_filtered[
        df_filtered["baseline_method"] == baseline_method
    ]

# ---------------------------------------------------
# Threshold Determination
# ---------------------------------------------------
if df_thresholds_file is not None and "retention_filter" in df_thresholds_file.columns:

    retention_key = "none" if retention_mode == "Baseline (All Months)" else ">=40%"

    if "season_scope" in df_thresholds_file.columns:
        threshold_row = df_thresholds_file[
            (df_thresholds_file["indicator"] == indicator) &
            (df_thresholds_file["retention_filter"] == retention_key) &
            (df_thresholds_file["season_scope"] == season_scope)
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

        if method == "percentile":
            alarm_threshold = row["alarm_percentile"]
            alert_threshold = row["alert_percentile"]
        else:
            alarm_threshold = row["alarm_tukey"]
            alert_threshold = row["alert_tukey"]
    else:
        alarm_threshold, alert_threshold = get_active_thresholds(indicator, method)

else:
    alarm_threshold, alert_threshold = get_active_thresholds(indicator, method)

# ---------------------------------------------------
# Dynamic Threshold Recalculation (Selected Provinces)
# ---------------------------------------------------

if baseline_mode == "Dynamic (Selected Provinces)" and len(selected_units) > 0:

    # Only recompute if subset of provinces selected
    if len(selected_units) < len(all_units):

        try:

            recalculated = recalculate_thresholds(
                df_filtered,
                indicator,
                selected_units
            )

            if method in recalculated:

                alarm_threshold = recalculated[method]["alarm"]
                alert_threshold = recalculated[method]["alert"]

                st.info("Dynamic thresholds recomputed using selected provinces.")

        except Exception as e:

            st.warning(f"Dynamic threshold computation failed: {e}")

# ---------------------------------------------------
# Extract BOTH Seasonal Thresholds (for display merge)
# ---------------------------------------------------

def get_season_thresholds(season_name):
    if df_thresholds_file is None:
        return alarm_threshold, alert_threshold

    retention_key = "none" if retention_mode == "Baseline (All Months)" else ">=40%"

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
# Editable Threshold Inputs
# ---------------------------------------------------
st.subheader("Threshold Settings")

col1, col2, col3 = st.columns(3)

with col1:
    alarm_threshold = st.number_input("Alarm Threshold", value=float(alarm_threshold))

with col2:
    alert_threshold = st.number_input("Alert Threshold", value=float(alert_threshold))

with col3:
    if st.button("Reset to Default"):
        reset_override(indicator, method)
        st.rerun()

if st.button("Apply & Save Threshold"):
    save_override(indicator, method, alarm_threshold, alert_threshold)
    st.success("Threshold saved.")


# ---------------------------------------------------
# Apply Classification (Season-Aware Only When Needed)
# ---------------------------------------------------

units_for_calc = all_units if view_mode == "National (All Provinces)" else selected_units

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
st.subheader("Trigger Structural Summary")

# 🔹 TWG Explanatory Info Box
st.info(
    f"ℹ️ **Interpretation Note:** Thresholds reflect "
    f"**{season_scope}** | Retention Mode: **{retention_mode}**. "
    "Structural summary below reflects the actual selected provinces "
    "and time window."
)

if len(units_for_calc) == 0:
    st.warning("Please select at least one province.")
else:

    matrix_summary = cached_classification_matrix(
        df_filtered,
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

        if direction == "lower":
            filtered_count = df_retention[df_retention["value"] < 100]["value"].count()
        elif direction == "upper":
            filtered_count = df_retention[df_retention["value"] > 0]["value"].count()
        else:
            filtered_count = total_count

        if total_count > 0:
            overall_percent = round(filtered_count / total_count * 100, 1)
            overall_display = f"{filtered_count} ({overall_percent}%)"
        else:
            overall_display = "N/A"
            overall_percent = None

        # ---- Monthly retention ----
        if direction == "lower":
            monthly_stats = (
                df_retention
                .groupby("year_month")["value"]
                .agg(
                    total="count",
                    filtered=lambda x: (x < 100).sum()
                )
                .reset_index()
            )
        elif direction == "upper":
            monthly_stats = (
                df_retention
                .groupby("year_month")["value"]
                .agg(
                    total="count",
                    filtered=lambda x: (x > 0).sum()
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
                "Trigger Frequency (proportion)"
            ],
            "Alarm": [
                f"{round(alarm_threshold, 2)}",
                overall_display,
                proportion_range,
                f"{int(alarm_min)}% - {int(alarm_max)}%"
            ],
            "Alert": [
                f"{round(alert_threshold, 2)}",
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
st.subheader("Aggregated Trigger Chart")

st.caption(
    "Highlighted months reflect the selected seasonal scope. "
    "Other months remain visible but are visually softened."
)

fig = go.Figure()

# Add month column for season awareness
counts["Month"] = counts["date"].dt.month

if display_mode == "Count":
    alarm_y = counts["Alarm"]
    alert_y = counts["Alert"]
    minimal_y = counts["Minimal"]
else:
    alarm_y = counts["Alarm_pct"]
    alert_y = counts["Alert_pct"]
    minimal_y = counts["Minimal_pct"]

# Opacity logic
opacity_values = [
    1 if m in selected_season_months else 0.25
    for m in counts["Month"]
]

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
    else:
        indicator_type = "price"  # safe fallback

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
if st.checkbox("Show Province Classification Matrix") and len(units_for_calc) > 0:

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
if view_mode == "National (All Provinces)":

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
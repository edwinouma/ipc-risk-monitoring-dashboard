import matplotlib.pyplot as plt
import plotly.graph_objects as go
import pandas as pd
import os


# =====================================================
# STATIC STACKED BAR (PNG + PDF)
# =====================================================

def plot_monthly_trigger_counts(
    trigger_df,
    indicator_value,
    method="percentile",
    use_percent=False,
    save_path="outputs"
):
    """
    Create stacked bar chart (Alarm → Alert → Minimal)
    and return the figure.
    """

    os.makedirs(save_path, exist_ok=True)

    df = trigger_df[trigger_df["indicator"] == indicator_value].copy()
    df = df.sort_values("date")

    # ---------------------------------------------------
    # Select columns based on method
    # ---------------------------------------------------
    if method == "percentile":
        alarm_col = "alarms_percentile"
        alert_col = "alerts_percentile"
        minimal_col = "minimal_percentile"

        if use_percent:
            alarm_col = "alarm_percentile_pct"
            alert_col = "alert_percentile_pct"
            minimal_col = "minimal_percentile_pct"

    elif method == "tukey":
        alarm_col = "alarms_tukey"
        alert_col = "alerts_tukey"
        minimal_col = "minimal_tukey"

        if use_percent:
            alarm_col = "alarm_tukey_pct"
            alert_col = "alert_tukey_pct"
            minimal_col = "minimal_tukey_pct"
    else:
        raise ValueError("method must be 'percentile' or 'tukey'")

    # ---------------------------------------------------
    # Plot using Plotly instead of matplotlib
    # ---------------------------------------------------

    fig = go.Figure()

    fig.add_bar(
        x=df["date"],
        y=df[alarm_col],
        name="Alarm",
        marker_color="red"
    )

    fig.add_bar(
        x=df["date"],
        y=df[alert_col],
        name="Alert",
        marker_color="orange"
    )

    fig.add_bar(
        x=df["date"],
        y=df[minimal_col],
        name="Minimal",
        marker_color="lightgreen"
    )

    ylabel = "Percentage (%)" if use_percent else "Number of Units"

    fig.update_layout(
        barmode="stack",
        title=f"Stacked Units by Alarm/Alert Levels ({method.capitalize()})",
        xaxis_title="Month",
        yaxis_title=ylabel,
        width=1400,
        height=600
    )

    safe_name = indicator_value.replace(" ", "_").replace("%", "")
    filename_base = f"{safe_name}_{method}_stacked"

    return fig


# =====================================================
# INTERACTIVE STACKED BAR (HTML with Zoom/Scroll)
# =====================================================

def plot_monthly_trigger_counts_interactive(
    trigger_df,
    indicator_value,
    method="percentile",
    use_percent=False,
    save_path="outputs"
):
    """
    Create interactive stacked bar chart (Alarm bottom)
    and save as HTML.
    """

    os.makedirs(save_path, exist_ok=True)

    df = trigger_df[trigger_df["indicator"] == indicator_value].copy()
    df = df.sort_values("date")

    if method == "percentile":
        alarm_col = "alarms_percentile"
        alert_col = "alerts_percentile"
        minimal_col = "minimal_percentile"

        if use_percent:
            alarm_col = "alarm_percentile_pct"
            alert_col = "alert_percentile_pct"
            minimal_col = "minimal_percentile_pct"

    elif method == "tukey":
        alarm_col = "alarms_tukey"
        alert_col = "alerts_tukey"
        minimal_col = "minimal_tukey"

        if use_percent:
            alarm_col = "alarm_tukey_pct"
            alert_col = "alert_tukey_pct"
            minimal_col = "minimal_tukey_pct"
    else:
        raise ValueError("method must be 'percentile' or 'tukey'")

    fig = go.Figure()

    fig.add_bar(
        x=df["date"],
        y=df[alarm_col],
        name="Alarm",
        marker_color="red"
    )

    fig.add_bar(
        x=df["date"],
        y=df[alert_col],
        name="Alert",
        marker_color="orange"
    )

    fig.add_bar(
        x=df["date"],
        y=df[minimal_col],
        name="Minimal",
        marker_color="lightgreen"
    )

    ylabel = "Percentage (%)" if use_percent else "Number of Units"

    fig.update_layout(
        barmode="stack",
        title=f"Stacked Units by Alarm/Alert Levels ({method.capitalize()})",
        xaxis_title="Month",
        yaxis_title=ylabel,
        width=1400,
        height=600
    )

    safe_name = indicator_value.replace(" ", "_").replace("%", "")
    filename_base = f"{safe_name}_{method}_stacked"

    return fig
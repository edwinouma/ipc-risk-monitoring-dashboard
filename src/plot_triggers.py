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
    Create stacked bar chart (Alarm bottom → Alert → Minimal top)
    and save as PNG + PDF.
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
    # Reduce x-axis clutter
    # ---------------------------------------------------
    total_points = len(df)
    step = max(1, total_points // 15)

    x = range(total_points)

    fig, ax = plt.subplots(figsize=(20, 6))

    # --- STACK ORDER: Alarm → Alert → Minimal ---

    ax.bar(x, df[alarm_col],
           label="Alarm", color="red")

    ax.bar(x, df[alert_col],
           bottom=df[alarm_col],
           label="Alert", color="orange")

    ax.bar(x, df[minimal_col],
           bottom=df[alarm_col] + df[alert_col],
           label="Minimal", color="lightgreen")

    ax.set_xticks([i for i in x if i % step == 0])
    ax.set_xticklabels(
        df["date"].dt.strftime("%Y %b")[::step],
        rotation=45,
        ha="right"
    )

    ylabel = "Percentage (%)" if use_percent else "Number of Units"

    ax.set_ylabel(ylabel)
    ax.set_title(
        f"Stacked Units by Alarm/Alert Levels ({method.capitalize()})"
    )

    ax.legend()
    plt.tight_layout()

    # ---------------------------------------------------
    # Save Files
    # ---------------------------------------------------
    safe_name = indicator_value.replace(" ", "_").replace("%", "")
    filename_base = f"{safe_name}_{method}_stacked"

    plt.savefig(f"{save_path}/{filename_base}.png", dpi=300)
    plt.savefig(f"{save_path}/{filename_base}.pdf")

    plt.close()

    print(f"Saved static stacked chart: {filename_base}.png and .pdf")


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

    # STACK ORDER matters in Plotly
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
    filename = f"{save_path}/{safe_name}_{method}_stacked_interactive.html"

    fig.write_html(filename)

    print(f"Saved interactive stacked chart: {filename}")
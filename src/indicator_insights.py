import pandas as pd
from src.config import CLASSIFICATION_LABELS

alarm_label = CLASSIFICATION_LABELS["alarm"]
alert_label = CLASSIFICATION_LABELS["alert"]
minimal_label = CLASSIFICATION_LABELS["minimal"]
no_data_label = CLASSIFICATION_LABELS.get("no_data", "No data")


def generate_indicator_insights(
    counts,
    matrix_summary,
    indicator,
    selected_country,
    start_date,
    end_date,
    top_n=5,
    events=None,   # 🔥 ADD THIS
    ipc_matrix=None   # 🔥 ADD THIS
):
    """
    Generate simple per-indicator insights from chart counts and unit matrix.
    This is descriptive only. It does not change classifications.
    """

    insights = []

    if counts is None or counts.empty:
        return ["No chart data available for insight generation."]

    if matrix_summary is None or matrix_summary.empty:
        return ["No matrix data available for insight generation."]

    df_counts = counts.copy()

    # ---------------------------------------------------
    # 1. Peak warning months
    # ---------------------------------------------------
    alarm_pct_col = f"{alarm_label}_pct"
    alert_pct_col = f"{alert_label}_pct"

    if alarm_pct_col in df_counts.columns and alert_pct_col in df_counts.columns:
        df_counts["warning_pct"] = (
            df_counts[alarm_pct_col].fillna(0) +
            df_counts[alert_pct_col].fillna(0)
        )

        peak_row = df_counts.sort_values("warning_pct", ascending=False).iloc[0]

        peak_month = peak_row["date"].strftime("%Y %b")
        peak_pct = round(peak_row["warning_pct"], 1)

        insights.append(
            f"The strongest warning signal for **{indicator}** in **{selected_country}** "
            f"occurred in **{peak_month}**, when **{peak_pct}%** of selected units were in "
            f"**{alert_label}** or **{alarm_label}**."
        )

    # ---------------------------------------------------
    # 2. Persistent hotspot units
    # ---------------------------------------------------
    matrix = matrix_summary.copy()

    # Keep only month columns, exclude summary columns
    summary_cols = ["% Alarm", "% Alert", "Sum"]
    month_cols = [c for c in matrix.columns if c not in summary_cols]

    if month_cols:
        matrix["_alarm_count"] = (matrix[month_cols] == alarm_label).sum(axis=1)
        matrix["_alert_count"] = (matrix[month_cols] == alert_label).sum(axis=1)
        matrix["_warning_count"] = matrix["_alarm_count"] + matrix["_alert_count"]
        matrix["_valid_months"] = (matrix[month_cols] != no_data_label).sum(axis=1)

        matrix["_warning_pct"] = matrix.apply(
            lambda r: (r["_warning_count"] / r["_valid_months"] * 100)
            if r["_valid_months"] > 0 else 0,
            axis=1
        )

        hotspot_units = (
            matrix.sort_values("_warning_pct", ascending=False)
            .head(top_n)
        )

        hotspot_text = ", ".join([
            f"{idx} ({round(row['_warning_pct'], 0)}%)"
            for idx, row in hotspot_units.iterrows()
            if row["_warning_pct"] > 0
        ])

        if hotspot_text:
            insights.append(
                f"The units with the most persistent warning conditions are: "
                f"**{hotspot_text}**."
            )
        else:
            insights.append(
                "No unit shows persistent Alert or Alarm conditions during the selected period."
            )

    # ---------------------------------------------------
    # 3. Alarm concentration
    # ---------------------------------------------------
    if month_cols:
        alarm_units = matrix[matrix["_alarm_count"] > 0]

        if not alarm_units.empty:
            top_alarm = (
                alarm_units.sort_values("_alarm_count", ascending=False)
                .head(top_n)
            )

            alarm_text = ", ".join([
                f"{idx} ({int(row['_alarm_count'])} months)"
                for idx, row in top_alarm.iterrows()
            ])

            insights.append(
                f"Alarm conditions are most frequently observed in: **{alarm_text}**."
            )
        else:
            insights.append(
                "No Alarm classifications were observed during the selected period."
            )

    # ---------------------------------------------------
    # 4. Data completeness warning
    # ---------------------------------------------------
    if month_cols:
        total_cells = matrix[month_cols].size
        no_data_cells = (matrix[month_cols] == no_data_label).sum().sum()

        if total_cells > 0:
            no_data_pct = round(no_data_cells / total_cells * 100, 1)

            if no_data_pct >= 30:
                insights.append(
                    f"Data completeness should be reviewed: **{no_data_pct}%** of matrix cells "
                    f"are classified as **{no_data_label}**."
                )

    # ---------------------------------------------------
    # Event Alignment (Smart: includes lag)
    # ---------------------------------------------------
    lag_alignment = compute_lagged_event_alignment(
        counts,
        events,
        max_lag=2
    )

    if lag_alignment is not None:

        lag = lag_alignment["lag"]
        pct = lag_alignment["alignment_pct"]
        overlap = lag_alignment["event_overlap"]
        total = lag_alignment["total_warning_months"]

        if lag == 0:
            insights.append(
                f"**{pct}%** of warning months ({overlap} out of {total}) "
                f"coincide with reference events, indicating strong immediate alignment."
            )

        elif lag == 1:
            insights.append(
                f"The strongest alignment occurs **one month after events**, "
                f"with **{pct}%** of warning months ({overlap} out of {total}) aligned. "
                f"This suggests a short lagged impact."
            )

        else:
            insights.append(
                f"The strongest alignment occurs **{lag} months after events**, "
                f"with **{pct}%** of warning months ({overlap} out of {total}) aligned. "
                f"This suggests delayed impact dynamics."
            )

    # ---------------------------------------------------
    # IPC Alignment (Smart with Lead)
    # ---------------------------------------------------
    ipc_lag_alignment = compute_lagged_ipc_alignment(
        matrix_summary,
        ipc_matrix,
        max_lead=3
    )

    if ipc_lag_alignment is not None:

        lead = ipc_lag_alignment["lead"]
        capture = ipc_lag_alignment["ipc_capture"]
        precision = ipc_lag_alignment["warning_precision"]
        alignment = ipc_lag_alignment["alignment_pct"]

        if lead == 0:
            lead_text = "in the same month"
        elif lead == 1:
            lead_text = "one month before IPC outcomes"
        else:
            lead_text = f"{lead} months before IPC outcomes"

        insights.append(
            f"Signal alignment with IPC Phase 3+ is **{alignment}%**, "
            f"with strongest relationship observed **{lead_text}**."
        )

        if precision is not None:
            insights.append(
                f"When the signal triggers, it matches IPC Phase 3+ in "
                f"**{precision}%** of cases, indicating strong reliability."
            )

        if capture is not None:
            insights.append(
                f"However, it captures **{capture}%** of IPC Phase 3+ cases, "
                f"suggesting limited sensitivity to all crisis conditions."
            )

    return insights

def compute_event_alignment(counts, events, start_date, end_date):
    """
    Compute alignment between warning peaks and reference events
    """

    if counts is None or counts.empty or events is None or events.empty:
        return None

    df = counts.copy()

    # Ensure date
    df["date"] = pd.to_datetime(df["date"])

    # Define warning signal
    if "warning_pct" not in df.columns:
        alarm_pct_col = f"{alarm_label}_pct"
        alert_pct_col = f"{alert_label}_pct"

        if alarm_pct_col in df.columns and alert_pct_col in df.columns:
            df["warning_pct"] = (
                    df[alarm_pct_col].fillna(0) +
                    df[alert_pct_col].fillna(0)
            )
        else:
            return None

    df["warning"] = df["warning_pct"] > 0

    # Convert events to monthly flags
    events = events.copy()
    events["start"] = pd.to_datetime(events["start"])
    events["end"] = pd.to_datetime(events["end"])

    event_months = set()

    for _, row in events.iterrows():
        months = pd.date_range(row["start"], row["end"], freq="MS")
        for m in months:
            event_months.add(m.to_period("M"))

    # Map events to counts
    df["year_month"] = df["date"].dt.to_period("M")
    df["event"] = df["year_month"].isin(event_months)

    # Compute alignment
    warning_months = df[df["warning"]]
    if len(warning_months) == 0:
        return {
            "alignment_pct": 0,
            "event_overlap": 0,
            "total_warning_months": 0
        }

    overlap = warning_months["event"].sum()
    total = len(warning_months)

    alignment_pct = round(overlap / total * 100, 1)

    return {
        "alignment_pct": alignment_pct,
        "event_overlap": int(overlap),
        "total_warning_months": int(total)
    }

def compute_lagged_event_alignment(counts, events, max_lag=2):
    """
    Check whether warning months align with reference events
    in the same month, 1 month after, or 2 months after.
    """

    if counts is None or counts.empty or events is None or events.empty:
        return None

    df = counts.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["year_month"] = df["date"].dt.to_period("M")

    alarm_pct_col = f"{alarm_label}_pct"
    alert_pct_col = f"{alert_label}_pct"

    if "warning_pct" not in df.columns:
        if alarm_pct_col in df.columns and alert_pct_col in df.columns:
            df["warning_pct"] = (
                df[alarm_pct_col].fillna(0) +
                df[alert_pct_col].fillna(0)
            )
        else:
            return None

    df["warning"] = df["warning_pct"] > 0
    warning_months = df[df["warning"]].copy()

    if warning_months.empty:
        return None

    events = events.copy()
    events["start"] = pd.to_datetime(events["start"])
    events["end"] = pd.to_datetime(events["end"])

    event_months = set()

    for _, row in events.iterrows():
        months = pd.date_range(row["start"], row["end"], freq="MS")
        for m in months:
            event_months.add(m.to_period("M"))

    results = []

    for lag in range(0, max_lag + 1):
        lagged_event_months = {
            m + lag for m in event_months
        }

        overlap = warning_months["year_month"].isin(lagged_event_months).sum()
        total = len(warning_months)

        results.append({
            "lag": lag,
            "alignment_pct": round(overlap / total * 100, 1),
            "event_overlap": int(overlap),
            "total_warning_months": int(total)
        })

    best = max(results, key=lambda x: x["alignment_pct"])

    return best

def compute_ipc_alignment(matrix_summary, ipc_matrix):
    """
    Compare indicator warning classifications with IPC Phase 3+.

    Signal warning = Alert or Alarm
    IPC concern = phase 3, 4, or 5
    """

    if matrix_summary is None or matrix_summary.empty:
        return None

    if ipc_matrix is None or ipc_matrix.empty:
        return None

    signal = matrix_summary.copy()
    ipc = ipc_matrix.copy()

    # Remove summary columns from signal matrix
    summary_cols = ["% Alarm", "% Alert", "Sum"]
    signal_month_cols = [c for c in signal.columns if c not in summary_cols]

    # Keep common units and months only
    common_units = signal.index.intersection(ipc.index)
    common_months = [c for c in signal_month_cols if c in ipc.columns]

    if len(common_units) == 0 or len(common_months) == 0:
        return None

    signal = signal.loc[common_units, common_months]
    ipc = ipc.loc[common_units, common_months]

    signal_warning = signal.isin([alert_label, alarm_label])

    def ipc_is_phase3plus(cell):
        if pd.isna(cell) or cell == no_data_label:
            return False

        text = str(cell).lower()

        return (
            "phase 3" in text or
            "phase 4" in text or
            "phase 5" in text
        )

    ipc_phase3plus = ipc.map(ipc_is_phase3plus)

    valid_cells = ipc.astype(str) != no_data_label

    if valid_cells.sum().sum() == 0:
        return None

    both_warning_and_ipc = (signal_warning & ipc_phase3plus & valid_cells).sum().sum()
    signal_warning_total = (signal_warning & valid_cells).sum().sum()
    ipc_phase3plus_total = (ipc_phase3plus & valid_cells).sum().sum()

    total_valid = valid_cells.sum().sum()

    exact_match = (
        (signal_warning == ipc_phase3plus) & valid_cells
    ).sum().sum()

    alignment_pct = round(exact_match / total_valid * 100, 1)

    if signal_warning_total > 0:
        warning_precision = round(
            both_warning_and_ipc / signal_warning_total * 100, 1
        )
    else:
        warning_precision = None

    if ipc_phase3plus_total > 0:
        ipc_capture = round(
            both_warning_and_ipc / ipc_phase3plus_total * 100, 1
        )
    else:
        ipc_capture = None

    return {
        "alignment_pct": alignment_pct,
        "warning_precision": warning_precision,
        "ipc_capture": ipc_capture,
        "matched_cells": int(both_warning_and_ipc),
        "signal_warning_total": int(signal_warning_total),
        "ipc_phase3plus_total": int(ipc_phase3plus_total),
        "total_valid_cells": int(total_valid)
    }

def compute_lagged_ipc_alignment(matrix_summary, ipc_matrix, max_lead=3):
    """
    Check whether signal warnings lead IPC Phase 3+ by 0–3 months.

    lead = 0 means same month.
    lead = 1 means signal occurs 1 month before IPC.
    """

    if matrix_summary is None or matrix_summary.empty:
        return None

    if ipc_matrix is None or ipc_matrix.empty:
        return None

    signal = matrix_summary.copy()
    ipc = ipc_matrix.copy()

    summary_cols = ["% Alarm", "% Alert", "Sum"]
    signal_month_cols = [c for c in signal.columns if c not in summary_cols]

    common_units = signal.index.intersection(ipc.index)

    if len(common_units) == 0:
        return None

    signal = signal.loc[common_units, signal_month_cols]
    ipc = ipc.loc[common_units]

    signal_warning = signal.isin([alert_label, alarm_label])

    def ipc_is_phase3plus(cell):
        if pd.isna(cell) or cell == no_data_label:
            return False

        text = str(cell).lower()

        return (
            "phase 3" in text or
            "phase 4" in text or
            "phase 5" in text
        )

    ipc_phase3plus = ipc.map(ipc_is_phase3plus)
    valid_ipc = ipc.astype(str) != no_data_label

    results = []

    for lead in range(0, max_lead + 1):

        matched = 0
        signal_total = 0
        ipc_total = 0
        valid_total = 0
        exact_match = 0

        for signal_col in signal_month_cols:

            try:
                signal_period = pd.to_datetime(signal_col).to_period("M")
            except:
                continue

            ipc_period = signal_period + lead
            ipc_col = ipc_period.strftime("%Y %b")

            if ipc_col not in ipc.columns:
                continue

            s = signal_warning[signal_col]
            i = ipc_phase3plus[ipc_col]
            v = valid_ipc[ipc_col]

            matched += (s & i & v).sum()
            signal_total += (s & v).sum()
            ipc_total += (i & v).sum()
            valid_total += v.sum()
            exact_match += ((s == i) & v).sum()

        if valid_total == 0:
            continue

        alignment_pct = round(exact_match / valid_total * 100, 1)

        precision = (
            round(matched / signal_total * 100, 1)
            if signal_total > 0 else None
        )

        capture = (
            round(matched / ipc_total * 100, 1)
            if ipc_total > 0 else None
        )

        results.append({
            "lead": lead,
            "alignment_pct": alignment_pct,
            "warning_precision": precision,
            "ipc_capture": capture,
            "matched_cells": int(matched),
            "signal_warning_total": int(signal_total),
            "ipc_phase3plus_total": int(ipc_total),
            "total_valid_cells": int(valid_total)
        })

    if not results:
        return None

    # Prioritize capture because we want to know whether signal predicts IPC crisis
    valid_capture_results = [
        r for r in results if r["ipc_capture"] is not None
    ]

    if valid_capture_results:
        best = max(valid_capture_results, key=lambda x: x["ipc_capture"])
    else:
        best = max(results, key=lambda x: x["alignment_pct"])

    return best


def generate_indicator_narrative(insights, indicator=None, country=None):
    """
    Convert bullet insights into a clean analyst-style narrative.
    Deterministic (no AI yet).
    """

    if not insights:
        return "No insights available for narrative generation."

    text = " ".join([
        str(i).replace("**", "")  # remove markdown bold
        for i in insights
    ])

    # ---------------------------------------------------
    # Simple structured narrative logic
    # ---------------------------------------------------
    narrative = ""

    # Add context intro
    if indicator and country:
        narrative += f"For **{indicator}** in **{country}**, "

    # 1. Overall signal behavior
    if "strongest warning signal" in text:
        narrative += "The indicator shows clear temporal variation in risk levels. "

    # 2. Persistence
    if "persistent warning conditions" in text:
        narrative += "Certain units experience consistently elevated risk conditions over time. "

    # 3. Event alignment
    if "alignment" in text and "events" in text:
        if "strong immediate alignment" in text:
            narrative += "The signal aligns closely with recorded events, indicating strong real-time sensitivity. "
        elif "lagged" in text or "after events" in text:
            narrative += "The signal responds to events with a short delay, suggesting lagged impact dynamics. "

    # 4. IPC relationship
    if "IPC Phase 3+" in text:

        if "before IPC outcomes" in text:
            narrative += "Importantly, the indicator shows predictive capacity, with signals preceding IPC deterioration. "

        if "matches IPC Phase 3+" in text:
            narrative += "When triggered, the signal is highly reliable in identifying crisis conditions. "

        if "captures" in text:
            narrative += "However, the signal does not capture all IPC crises, indicating partial sensitivity. "

    # 5. Data quality
    if "Data completeness" in text:
        narrative += "Data availability may influence interpretation and should be considered in analysis. "

    # ---------------------------------------------------
    # Fallback (if nothing triggered)
    # ---------------------------------------------------
    if narrative == "":
        narrative = "The indicator provides useful signals of changing conditions, though interpretation should consider timing, coverage, and data limitations."

    # ---------------------------------------------------
    # Indicator classification (VERY IMPORTANT)
    # ---------------------------------------------------
    if "predictive capacity" in narrative and "highly reliable" in narrative:
        narrative += " Overall, this indicator functions as a reliable early warning signal."

    elif "highly reliable" in narrative and "captures" not in narrative:
        narrative += "Overall, this indicator provides reliable confirmation of crisis conditions but limited early warning capability."

    elif "does not capture all IPC crises" in narrative:
        narrative += " Overall, this indicator should be used alongside other indicators to fully assess crisis conditions."

    else:
        narrative += " Overall, the indicator provides useful supporting information but should be interpreted with caution."

    return narrative.strip()
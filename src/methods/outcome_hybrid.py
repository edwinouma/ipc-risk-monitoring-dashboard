# ==========================================================
# RAAp - OUTCOME INDICATOR HYBRID METHOD
# ==========================================================
"""
Hybrid threshold methodology for food security outcome indicators.

The RAAp outcome-indicator framework evaluates two complementary
dimensions:

1. Current outcome condition
   - Based on IPC-aligned outcome categories / prevalence.

2. Recent deterioration
   - Based on changes in adverse outcome prevalence relative to
     recent historical observations.

The final hybrid classification will combine these two dimensions.

IMPORTANT
---------
The current implementation supports a short-history baseline because
the available outcome dataset begins in January 2026.

Once sufficient historical observations become available, the
deterioration component can be upgraded to a seasonal historical
baseline without changing the overall hybrid architecture.

This module contains methodology only.
It should not contain file paths, file loading, saving, or dashboard
logic.
"""

import numpy as np
import pandas as pd
from src.config.thresholds import OUTCOME_DETERIORATION_THRESHOLDS


# ==========================================================
# REQUIRED HISTORY
# ==========================================================

MIN_HISTORY_MONTHS = 3


# ==========================================================
# ADVERSE PREVALENCE
# ==========================================================

def calculate_adverse_prevalence(
    df,
    indicator_col="indicator",
    category_col="category",
    value_col="value",
):
    """
    Calculate adverse outcome prevalence for each indicator.

    Current definitions
    -------------------
    FCS:
        Phase 3 + Phase 4-5

    rCSI:
        Phase 3+

    LCS:
        Phase 3 + Phase 4-5

    HHS:
        To be configured once sufficient repeated observations exist.

    HDDS:
        To be configured once sufficient repeated observations exist.

    Parameters
    ----------
    df : pandas.DataFrame
        Long-format outcome indicator dataset.

    indicator_col : str
        Column identifying the outcome indicator.

    category_col : str
        Column containing IPC-aligned category.

    value_col : str
        Column containing prevalence/proportion.

    Returns
    -------
    pandas.DataFrame
        Dataset containing adverse prevalence by unit, date,
        and indicator.
    """

    data = df.copy()

    required = [
        "country",
        "adm1_name",
        "date",
        indicator_col,
        category_col,
        value_col,
    ]

    missing = [col for col in required if col not in data.columns]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    # ------------------------------------------------------
    # Standardize
    # ------------------------------------------------------

    data["date"] = pd.to_datetime(
        data["date"],
        errors="coerce"
    )

    data[value_col] = pd.to_numeric(
        data[value_col],
        errors="coerce"
    )

    data = data.dropna(
        subset=[
            "adm1_name",
            "date",
            indicator_col,
            category_col,
            value_col,
        ]
    )

    # ------------------------------------------------------
    # Identify adverse categories
    # ------------------------------------------------------

    adverse_categories = {
        "FCS": {
            "FCS Phase 3",
            "FCS Phase 4-5",
        },

        "RCSI": {
            "RCSI Phase 3+",
        },

        "LCS": {
            "LCS Phase 3",
            "LCS Phase 4-5",
        },
    }

    def is_adverse(row):

        indicator = str(
            row[indicator_col]
        ).strip().upper()

        category = str(
            row[category_col]
        ).strip()

        categories = adverse_categories.get(
            indicator
        )

        if categories is None:
            return False

        return category.upper() in {
            x.upper() for x in categories
        }

    data["_is_adverse"] = data.apply(
        is_adverse,
        axis=1
    )

    # Keep only indicators currently configured
    configured = set(
        adverse_categories.keys()
    )

    data = data[
        data[indicator_col]
        .astype(str)
        .str.upper()
        .isin(configured)
    ]

    # ------------------------------------------------------
    # Sum adverse prevalence
    # ------------------------------------------------------

    adverse = (
        data[data["_is_adverse"]]
        .groupby(
            [
                "country",
                "adm1_name",
                "date",
                indicator_col,
            ],
            as_index=False,
        )[value_col]
        .sum()
    )

    adverse = adverse.rename(
        columns={
            value_col: "adverse_prevalence"
        }
    )

    return adverse


# ==========================================================
# RECENT BASELINE
# ==========================================================

def calculate_recent_baseline(
    df,
    value_col="adverse_prevalence",
    min_history=MIN_HISTORY_MONTHS,
):
    """
    Calculate recent historical baseline for adverse prevalence.

    For each ADM1 and indicator, the baseline for month t is the
    mean of all PREVIOUS available observations.

    The current observation is deliberately excluded from its own
    baseline.

    Example
    -------
    July baseline =
        mean(January ... June)

    This is currently a short-history baseline rather than a true
    seasonal climatology.

    Returns
    -------
    pandas.DataFrame
        Original dataframe plus:

        history_months
        baseline_value
        anomaly_pp
        previous_value
        mom_change_pp
    """

    data = df.copy()

    required = [
        "country",
        "adm1_name",
        "date",
        "indicator",
        value_col,
    ]

    missing = [
        col for col in required
        if col not in data.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    data = data.sort_values(
        [
            "country",
            "adm1_name",
            "indicator",
            "date",
        ]
    ).reset_index(drop=True)

    group_cols = [
        "country",
        "adm1_name",
        "indicator",
    ]

    # ------------------------------------------------------
    # Number of previous observations
    # ------------------------------------------------------

    data["history_months"] = (
        data
        .groupby(group_cols)
        .cumcount()
    )

    # ------------------------------------------------------
    # Previous month's value
    # ------------------------------------------------------

    data["previous_value"] = (
        data
        .groupby(group_cols)[value_col]
        .shift(1)
    )

    # ------------------------------------------------------
    # Expanding historical mean excluding current month
    # ------------------------------------------------------

    data["baseline_value"] = (
        data
        .groupby(group_cols)[value_col]
        .transform(
            lambda x:
                x.shift(1)
                .expanding()
                .mean()
        )
    )

    # ------------------------------------------------------
    # Baseline anomaly
    # ------------------------------------------------------

    data["anomaly_pp"] = (
        data[value_col]
        - data["baseline_value"]
    )

    # ------------------------------------------------------
    # Month-on-month change
    # ------------------------------------------------------

    data["mom_change_pp"] = (
        data[value_col]
        - data["previous_value"]
    )

    # ------------------------------------------------------
    # Insufficient history
    # ------------------------------------------------------

    insufficient = (
        data["history_months"]
        < min_history
    )

    data.loc[
        insufficient,
        [
            "baseline_value",
            "anomaly_pp",
        ]
    ] = np.nan

    return data

# ==========================================================
# DETERIORATION DIRECTION
# ==========================================================

def classify_deterioration_direction(
    df,
    anomaly_col="anomaly_pp",
):
    """
    Provide descriptive deterioration direction.

    This is NOT yet the final Alert/Alarm classification.

    Positive anomaly:
        adverse prevalence is above recent baseline.

    Negative anomaly:
        adverse prevalence is below recent baseline.

    Zero:
        approximately unchanged.

    Missing:
        insufficient historical observations.
    """

    data = df.copy()

    conditions = [
        data[anomaly_col].isna(),
        data[anomaly_col] > 0,
        data[anomaly_col] < 0,
    ]

    choices = [
        "Insufficient History",
        "Deteriorating",
        "Improving",
    ]

    data["deterioration_direction"] = np.select(
        conditions,
        choices,
        default="Stable",
    )

    return data


# ==========================================================
# BASELINE DETERIORATION STATUS
# ==========================================================

def classify_baseline_status(
    df,
    thresholds=OUTCOME_DETERIORATION_THRESHOLDS,
):
    """
    Classify deterioration relative to the recent baseline.

    Positive anomaly_pp represents deterioration because
    adverse outcome prevalence is higher than its recent
    historical baseline.
    """

    data = df.copy()

    def classify(row):

        if pd.isna(row["anomaly_pp"]):
            return "Insufficient History"

        indicator = str(
            row["indicator"]
        ).strip().upper()

        config = thresholds.get(indicator)

        if config is None:
            return "Not Configured"

        alert = config["baseline"]["alert"]
        alarm = config["baseline"]["alarm"]

        value = row["anomaly_pp"]

        if value >= alarm:
            return "Alarm"

        if value >= alert:
            return "Alert"

        return "No Concern"

    data["baseline_status"] = data.apply(
        classify,
        axis=1,
    )

    return data


# ==========================================================
# MONTH-ON-MONTH DETERIORATION STATUS
# ==========================================================

def classify_mom_status(
    df,
    thresholds=OUTCOME_DETERIORATION_THRESHOLDS,
):
    """
    Classify deterioration relative to the previous observation.

    Positive mom_change_pp represents deterioration because
    adverse outcome prevalence has increased.
    """

    data = df.copy()

    def classify(row):

        if pd.isna(row["mom_change_pp"]):
            return "Insufficient History"

        indicator = str(
            row["indicator"]
        ).strip().upper()

        config = thresholds.get(indicator)

        if config is None:
            return "Not Configured"

        alert = config["mom"]["alert"]
        alarm = config["mom"]["alarm"]

        value = row["mom_change_pp"]

        if value >= alarm:
            return "Alarm"

        if value >= alert:
            return "Alert"

        return "No Concern"

    data["mom_status"] = data.apply(
        classify,
        axis=1,
    )

    return data


# ==========================================================
# COMBINED DETERIORATION STATUS
# ==========================================================

def classify_deterioration_status(df):
    """
    Combine baseline and month-on-month deterioration signals.

    Rules
    -----
    Alarm:
        Either component is Alarm, or both components are Alert.

    Alert:
        One component is Alert without an Alarm.

    No Concern:
        Available components do not indicate Alert or Alarm.

    Insufficient History:
        Neither component provides a usable classification.
    """

    data = df.copy()

    def combine(row):

        baseline = row["baseline_status"]
        mom = row["mom_status"]

        # Alarm in either component
        if baseline == "Alarm" or mom == "Alarm":
            return "Alarm"

        # Two Alerts escalate to Alarm
        if baseline == "Alert" and mom == "Alert":
            return "Alarm"

        # One Alert
        if baseline == "Alert" or mom == "Alert":
            return "Alert"

        # Both available and normal
        if baseline == "No Concern" and mom == "No Concern":
            return "No Concern"

        # One usable normal signal
        if baseline == "No Concern" or mom == "No Concern":
            return "No Concern"

        return "Insufficient History"

    data["deterioration_status"] = data.apply(
        combine,
        axis=1,
    )

    return data

# ==========================================================
# MAIN METHOD
# ==========================================================

def compute_outcome_hybrid_metrics(
    df,
    min_history=MIN_HISTORY_MONTHS,
):
    """
    Run the current analytical components of the RAAp outcome
    hybrid methodology.

    NOTE
    ----
    This function does NOT yet assign final Alert/Alarm thresholds.

    Current workflow:

        IPC category prevalence
                ↓
        adverse prevalence
                ↓
        recent historical baseline
                ↓
        baseline anomaly
                ↓
        month-on-month change
                ↓
        deterioration direction

    Final absolute-status and hybrid Alert/Alarm classification
    will be added once operational thresholds have been defined.
    """

    adverse = calculate_adverse_prevalence(df)

    metrics = calculate_recent_baseline(
        adverse,
        min_history=min_history,
    )

    metrics = classify_deterioration_direction(
        metrics
    )

    metrics = classify_baseline_status(
        metrics
    )

    metrics = classify_mom_status(
        metrics
    )

    metrics = classify_deterioration_status(
        metrics
    )

    return metrics

# ==========================================================
# STANDALONE TEST
# ==========================================================

if __name__ == "__main__":

    import os

    # ------------------------------------------------------
    # Project root
    # ------------------------------------------------------
    project_root = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            ".."
        )
    )

    # ------------------------------------------------------
    # Input file
    # ------------------------------------------------------
    input_file = os.path.join(
        project_root,
        "data",
        "ipc_indicators.xlsx"
    )

    print(f"📂 Loading: {input_file}")

    # ------------------------------------------------------
    # Load data
    # ------------------------------------------------------
    df = pd.read_excel(input_file)

    # Ensure date is datetime
    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    print(f"📊 Raw records: {len(df):,}")
    print(f"📊 Columns: {df.columns.tolist()}")
    print(f"📅 Date range: {df['date'].min()} → {df['date'].max()}")

    # ------------------------------------------------------
    # Run outcome hybrid method
    # ------------------------------------------------------
    result = compute_outcome_hybrid_metrics(
        df,
        min_history=3
    )

    # ------------------------------------------------------
    # Display result
    # ------------------------------------------------------
    print("\n" + "=" * 80)
    print("OUTCOME HYBRID TEST RESULT")
    print("=" * 80)

    print("\nColumns created:")
    print(result.columns.tolist())

    print("\nFirst 30 records:")
    print(
        result.head(30).to_string(
            index=False
        )
    )

    # ------------------------------------------------------
    # Save test output
    # ------------------------------------------------------
    output_folder = os.path.join(
        project_root,
        "output"
    )

    os.makedirs(
        output_folder,
        exist_ok=True
    )

    output_file = os.path.join(
        output_folder,
        "outcome_hybrid_test.xlsx"
    )

    result.to_excel(
        output_file,
        index=False
    )

    print("\n" + "=" * 80)
    print("✅ Test completed successfully")
    print(f"📁 Output: {output_file}")
    print("=" * 80)
# ==========================================================
# RAAp - OUTCOME THRESHOLD EXPLORATION
# ==========================================================
"""
Exploratory analysis for developing deterioration thresholds
for RAAp food security outcome indicators.

PURPOSE
-------
This script does NOT assign operational Alert/Alarm thresholds.

Instead, it examines the empirical behaviour of:

    1. adverse_prevalence
    2. anomaly_pp
    3. mom_change_pp

for each outcome indicator.

The results are intended to support evidence-based selection of
deterioration thresholds before those thresholds are incorporated
into the production hybrid methodology.

Current indicators:
    - FCS
    - rCSI
    - LCS

Output:
    output/outcome_threshold_exploration.xlsx
"""

import os
import sys
import numpy as np
import pandas as pd


# ==========================================================
# PROJECT PATHS
# ==========================================================

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        ".."
    )
)

# Ensure project root is available for imports
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ==========================================================
# IMPORT OUTCOME METHOD
# ==========================================================

from src.methods.outcome_hybrid import (
    compute_outcome_hybrid_metrics
)


# ==========================================================
# CONFIGURATION
# ==========================================================

INPUT_FILE = os.path.join(
    PROJECT_ROOT,
    "data",
    "ipc_indicators.xlsx"
)

OUTPUT_FOLDER = os.path.join(
    PROJECT_ROOT,
    "output"
)

OUTPUT_FILE = os.path.join(
    OUTPUT_FOLDER,
    "outcome_threshold_exploration.xlsx"
)

MIN_HISTORY_MONTHS = 3


# ==========================================================
# SUMMARY STATISTICS
# ==========================================================

def calculate_metric_summary(
    df,
    metric,
):
    """
    Calculate descriptive statistics for a deterioration metric
    separately for each outcome indicator.

    Parameters
    ----------
    df : pandas.DataFrame

    metric : str
        Column to analyse, e.g.
        anomaly_pp or mom_change_pp.

    Returns
    -------
    pandas.DataFrame
    """

    rows = []

    for indicator, group in df.groupby("indicator"):

        values = pd.to_numeric(
            group[metric],
            errors="coerce"
        ).dropna()

        if values.empty:
            continue

        # --------------------------------------------------
        # Positive deterioration only
        # --------------------------------------------------

        positive = values[
            values > 0
        ]

        row = {
            "indicator": indicator,
            "metric": metric,

            # ----------------------------------------------
            # Overall observations
            # ----------------------------------------------

            "n_observations": len(values),

            "mean": values.mean(),
            "median": values.median(),
            "std": values.std(),

            "min": values.min(),
            "max": values.max(),

            # ----------------------------------------------
            # Overall distribution
            # ----------------------------------------------

            "p25": values.quantile(0.25),
            "p50": values.quantile(0.50),
            "p75": values.quantile(0.75),
            "p90": values.quantile(0.90),
            "p95": values.quantile(0.95),

            # ----------------------------------------------
            # Positive deterioration
            # ----------------------------------------------

            "n_positive": len(positive),

            "pct_positive": (
                len(positive)
                / len(values)
                * 100
            ),

            "positive_median": (
                positive.median()
                if not positive.empty
                else np.nan
            ),

            "positive_p75": (
                positive.quantile(0.75)
                if not positive.empty
                else np.nan
            ),

            "positive_p90": (
                positive.quantile(0.90)
                if not positive.empty
                else np.nan
            ),

            "positive_p95": (
                positive.quantile(0.95)
                if not positive.empty
                else np.nan
            ),

            "positive_max": (
                positive.max()
                if not positive.empty
                else np.nan
            ),

            # ----------------------------------------------
            # Candidate operational thresholds
            # ----------------------------------------------

            "n_gt_3pp": (values >= 3).sum(),
            "pct_gt_3pp": (
                (values >= 3).mean()
                * 100
            ),

            "n_gt_5pp": (values >= 5).sum(),
            "pct_gt_5pp": (
                (values >= 5).mean()
                * 100
            ),

            "n_gt_7_5pp": (
                values >= 7.5
            ).sum(),

            "pct_gt_7_5pp": (
                (values >= 7.5).mean()
                * 100
            ),

            "n_gt_10pp": (
                values >= 10
            ).sum(),

            "pct_gt_10pp": (
                (values >= 10).mean()
                * 100
            ),

            "n_gt_15pp": (
                values >= 15
            ).sum(),

            "pct_gt_15pp": (
                (values >= 15).mean()
                * 100
            ),

            "n_gt_20pp": (
                values >= 20
            ).sum(),

            "pct_gt_20pp": (
                (values >= 20).mean()
                * 100
            ),
        }

        rows.append(row)

    return pd.DataFrame(rows)


# ==========================================================
# POSITIVE DETERIORATION DISTRIBUTION
# ==========================================================

def calculate_positive_distribution(
    df,
    metric,
):
    """
    Calculate percentiles using only positive values.

    Positive values represent deterioration because the analytical
    variable is adverse outcome prevalence.
    """

    rows = []

    percentiles = [
        0.10,
        0.25,
        0.50,
        0.75,
        0.80,
        0.85,
        0.90,
        0.95,
        0.975,
        0.99,
    ]

    for indicator, group in df.groupby("indicator"):

        values = pd.to_numeric(
            group[metric],
            errors="coerce"
        ).dropna()

        values = values[
            values > 0
        ]

        if values.empty:
            continue

        row = {
            "indicator": indicator,
            "metric": metric,
            "n_positive": len(values),
        }

        for p in percentiles:

            column_name = (
                f"p{int(p * 1000) / 10:g}"
            )

            row[column_name] = (
                values.quantile(p)
            )

        rows.append(row)

    return pd.DataFrame(rows)


# ==========================================================
# THRESHOLD FREQUENCY TABLE
# ==========================================================

def calculate_threshold_frequency(
    df,
    metric,
):
    """
    Show how frequently different candidate thresholds would
    trigger deterioration signals.

    This allows us to understand the operational consequences
    of selecting thresholds such as 3, 5, 7.5, 10, 15 or 20
    percentage points.
    """

    candidate_thresholds = [
        2.5,
        3,
        5,
        7.5,
        10,
        12.5,
        15,
        20,
        25,
    ]

    rows = []

    for indicator, group in df.groupby("indicator"):

        values = pd.to_numeric(
            group[metric],
            errors="coerce"
        ).dropna()

        if values.empty:
            continue

        n = len(values)

        for threshold in candidate_thresholds:

            triggered = (
                values >= threshold
            ).sum()

            rows.append(
                {
                    "indicator": indicator,
                    "metric": metric,
                    "candidate_threshold_pp": threshold,
                    "n_observations": n,
                    "n_triggered": triggered,
                    "pct_triggered": (
                        triggered / n * 100
                    ),
                }
            )

    return pd.DataFrame(rows)


# ==========================================================
# COUNTY SUMMARY
# ==========================================================

def calculate_county_summary(
    df,
):
    """
    Summarise deterioration behaviour by country, ADM1,
    and indicator.
    """

    working = df.copy()

    working["positive_anomaly"] = (
        working["anomaly_pp"]
        .clip(lower=0)
    )

    working["positive_mom"] = (
        working["mom_change_pp"]
        .clip(lower=0)
    )

    summary = (
        working
        .groupby(
            [
                "country",
                "adm1_name",
                "indicator",
            ],
            as_index=False,
        )
        .agg(
            observations=(
                "adverse_prevalence",
                "count"
            ),

            mean_adverse_prevalence=(
                "adverse_prevalence",
                "mean"
            ),

            max_adverse_prevalence=(
                "adverse_prevalence",
                "max"
            ),

            mean_anomaly_pp=(
                "anomaly_pp",
                "mean"
            ),

            max_anomaly_pp=(
                "anomaly_pp",
                "max"
            ),

            max_positive_anomaly_pp=(
                "positive_anomaly",
                "max"
            ),

            mean_mom_change_pp=(
                "mom_change_pp",
                "mean"
            ),

            max_mom_change_pp=(
                "mom_change_pp",
                "max"
            ),

            max_positive_mom_pp=(
                "positive_mom",
                "max"
            ),
        )
    )

    return summary


# ==========================================================
# LATEST OBSERVATION
# ==========================================================

def get_latest_observations(
    df,
):
    """
    Extract the latest available observation for every
    country × ADM1 × indicator combination.
    """

    data = df.copy()

    data = data.sort_values(
        [
            "country",
            "adm1_name",
            "indicator",
            "date",
        ]
    )

    latest = (
        data
        .groupby(
            [
                "country",
                "adm1_name",
                "indicator",
            ],
            as_index=False,
        )
        .tail(1)
    )

    return latest.reset_index(drop=True)


# ==========================================================
# EXTREME DETERIORATION EVENTS
# ==========================================================

def get_extreme_events(
    df,
):
    """
    Extract the largest observed deterioration events.

    Events are retained where either:

        anomaly_pp >= 10

    OR

        mom_change_pp >= 10

    These records are useful for manually inspecting whether
    large statistical movements correspond to plausible
    operational deterioration.
    """

    extreme = df[
        (df["anomaly_pp"] >= 10)
        |
        (df["mom_change_pp"] >= 10)
    ].copy()

    extreme["max_deterioration_pp"] = (
        extreme[
            [
                "anomaly_pp",
                "mom_change_pp",
            ]
        ]
        .max(axis=1)
    )

    extreme = extreme.sort_values(
        "max_deterioration_pp",
        ascending=False
    )

    return extreme


# ==========================================================
# MAIN ANALYSIS
# ==========================================================

def main():

    print("=" * 80)
    print("RAAp OUTCOME THRESHOLD EXPLORATION")
    print("=" * 80)

    # ------------------------------------------------------
    # Load source data
    # ------------------------------------------------------

    print(f"\n📂 Loading:")
    print(INPUT_FILE)

    df = pd.read_excel(
        INPUT_FILE
    )

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    print(
        f"\n📊 Raw records: "
        f"{len(df):,}"
    )

    print(
        f"📅 Date range: "
        f"{df['date'].min()} "
        f"→ "
        f"{df['date'].max()}"
    )

    # ------------------------------------------------------
    # Run hybrid measurement engine
    # ------------------------------------------------------

    metrics = (
        compute_outcome_hybrid_metrics(
            df,
            min_history=MIN_HISTORY_MONTHS,
        )
    )

    print(
        f"\n📊 Hybrid metric records: "
        f"{len(metrics):,}"
    )

    # ------------------------------------------------------
    # Metric summaries
    # ------------------------------------------------------

    anomaly_summary = (
        calculate_metric_summary(
            metrics,
            "anomaly_pp",
        )
    )

    mom_summary = (
        calculate_metric_summary(
            metrics,
            "mom_change_pp",
        )
    )

    metric_summary = pd.concat(
        [
            anomaly_summary,
            mom_summary,
        ],
        ignore_index=True,
    )

    # ------------------------------------------------------
    # Positive distributions
    # ------------------------------------------------------

    anomaly_positive = (
        calculate_positive_distribution(
            metrics,
            "anomaly_pp",
        )
    )

    mom_positive = (
        calculate_positive_distribution(
            metrics,
            "mom_change_pp",
        )
    )

    positive_distribution = pd.concat(
        [
            anomaly_positive,
            mom_positive,
        ],
        ignore_index=True,
    )

    # ------------------------------------------------------
    # Candidate threshold frequencies
    # ------------------------------------------------------

    anomaly_frequency = (
        calculate_threshold_frequency(
            metrics,
            "anomaly_pp",
        )
    )

    mom_frequency = (
        calculate_threshold_frequency(
            metrics,
            "mom_change_pp",
        )
    )

    threshold_frequency = pd.concat(
        [
            anomaly_frequency,
            mom_frequency,
        ],
        ignore_index=True,
    )

    # ------------------------------------------------------
    # County summary
    # ------------------------------------------------------

    county_summary = (
        calculate_county_summary(
            metrics
        )
    )

    # ------------------------------------------------------
    # Latest observations
    # ------------------------------------------------------

    latest = (
        get_latest_observations(
            metrics
        )
    )

    # ------------------------------------------------------
    # Extreme deterioration events
    # ------------------------------------------------------

    extreme = (
        get_extreme_events(
            metrics
        )
    )

    # ------------------------------------------------------
    # Indicator-specific records
    # ------------------------------------------------------

    fcs = metrics[
        metrics["indicator"]
        .str.lower()
        .eq("fcs")
    ].copy()

    rcsi = metrics[
        metrics["indicator"]
        .str.lower()
        .eq("rcsi")
    ].copy()

    lcs = metrics[
        metrics["indicator"]
        .str.lower()
        .eq("lcs")
    ].copy()

    # ------------------------------------------------------
    # Save workbook
    # ------------------------------------------------------

    os.makedirs(
        OUTPUT_FOLDER,
        exist_ok=True
    )

    with pd.ExcelWriter(
        OUTPUT_FILE,
        engine="openpyxl",
        datetime_format="yyyy-mm-dd",
    ) as writer:

        metric_summary.to_excel(
            writer,
            sheet_name="Summary",
            index=False,
        )

        positive_distribution.to_excel(
            writer,
            sheet_name="Positive Percentiles",
            index=False,
        )

        threshold_frequency.to_excel(
            writer,
            sheet_name="Threshold Frequency",
            index=False,
        )

        latest.to_excel(
            writer,
            sheet_name="Latest",
            index=False,
        )

        extreme.to_excel(
            writer,
            sheet_name="Extreme Events",
            index=False,
        )

        county_summary.to_excel(
            writer,
            sheet_name="County Summary",
            index=False,
        )

        fcs.to_excel(
            writer,
            sheet_name="FCS",
            index=False,
        )

        rcsi.to_excel(
            writer,
            sheet_name="rCSI",
            index=False,
        )

        lcs.to_excel(
            writer,
            sheet_name="LCS",
            index=False,
        )

        metrics.to_excel(
            writer,
            sheet_name="All Metrics",
            index=False,
        )

    # ------------------------------------------------------
    # Console summary
    # ------------------------------------------------------

    print("\n" + "=" * 80)
    print("METRIC SUMMARY")
    print("=" * 80)

    display_cols = [
        "indicator",
        "metric",
        "n_observations",
        "pct_positive",
        "positive_median",
        "positive_p75",
        "positive_p90",
        "positive_p95",
        "positive_max",
    ]

    print(
        metric_summary[
            display_cols
        ].to_string(
            index=False
        )
    )

    print("\n" + "=" * 80)
    print("THRESHOLD EXPLORATION COMPLETED")
    print("=" * 80)

    print(
        f"\n✅ Output saved to:\n"
        f"{OUTPUT_FILE}"
    )


# ==========================================================
# RUN
# ==========================================================

if __name__ == "__main__":
    main()
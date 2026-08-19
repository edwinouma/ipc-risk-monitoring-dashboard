# ==========================================================
# RAAp - OUTCOME INDICATOR PIPELINE
# ==========================================================
"""
Pipeline for preparing food security outcome indicators for RAAp.

PURPOSE
-------
This pipeline combines two complementary dimensions:

1. CURRENT CONDITION
   Original IPC-aligned outcome category prevalences.

   Examples:
       FCS Phase 1-2
       FCS Phase 3
       FCS Phase 4-5

2. CHANGE / DETERIORATION
   Metrics produced by the outcome hybrid methodology.

   Examples:
       adverse_prevalence
       baseline_value
       anomaly_pp
       mom_change_pp
       baseline_status
       mom_status
       deterioration_status

The final output contains one record per:

    country × adm1_name × date × indicator

This provides a dashboard-ready dataset containing both the
current outcome condition and the RAAp deterioration signal.

Methodology is implemented in:
    src/methods/outcome_hybrid.py

Threshold configuration is implemented in:
    src/config/thresholds.py
"""

import os
import sys
import pandas as pd


# ==========================================================
# PROJECT ROOT
# ==========================================================

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        ".."
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(
        0,
        PROJECT_ROOT
    )


# ==========================================================
# IMPORT OUTCOME HYBRID METHOD
# ==========================================================

from src.methods.outcome_hybrid import (
    compute_outcome_hybrid_metrics
)


# ==========================================================
# CONFIGURATION
# ==========================================================

MIN_HISTORY_MONTHS = 3


# ==========================================================
# REQUIRED COLUMNS
# ==========================================================

REQUIRED_COLUMNS = [
    "country",
    "date",
    "adm1_name",
    "indicator",
    "category",
    "value",
]


# ==========================================================
# VALIDATE INPUT DATA
# ==========================================================

def validate_outcome_data(df):
    """
    Validate the minimum input structure required by the
    outcome pipeline.
    """

    missing = [
        col
        for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required outcome columns: {missing}"
        )

    return True


# ==========================================================
# CLEAN OUTCOME DATA
# ==========================================================

def clean_outcome_data(df):
    """
    Standardize the outcome dataset before processing.

    Returns
    -------
    pandas.DataFrame
    """

    data = df.copy()

    validate_outcome_data(
        data
    )

    # ------------------------------------------------------
    # Standardize dates
    # ------------------------------------------------------

    data["date"] = pd.to_datetime(
        data["date"],
        errors="coerce"
    )

    # ------------------------------------------------------
    # Standardize numeric values
    # ------------------------------------------------------

    data["value"] = pd.to_numeric(
        data["value"],
        errors="coerce"
    )

    # ------------------------------------------------------
    # Clean text fields
    # ------------------------------------------------------

    for col in [
        "country",
        "adm1_name",
        "indicator",
        "category",
    ]:

        data[col] = (
            data[col]
            .astype("string")
            .str.strip()
        )

    # ------------------------------------------------------
    # Standardize indicator names
    # ------------------------------------------------------

    data["indicator"] = (
        data["indicator"]
        .str.lower()
    )

    # ------------------------------------------------------
    # Remove incomplete observations
    # ------------------------------------------------------

    data = data.dropna(
        subset=[
            "country",
            "date",
            "adm1_name",
            "indicator",
            "category",
            "value",
        ]
    )

    return data


# ==========================================================
# PREPARE CURRENT CONDITION
# ==========================================================

def prepare_current_condition(df):
    """
    Convert the original category prevalence dataset from
    long format to dashboard-ready wide format.

    Example
    -------

    Input:

        Kenya | Baringo | 2026-04 | fcs |
        FCS Phase 1-2 | 60

        Kenya | Baringo | 2026-04 | fcs |
        FCS Phase 3 | 34

        Kenya | Baringo | 2026-04 | fcs |
        FCS Phase 4-5 | 5

    Output:

        Kenya | Baringo | 2026-04 | fcs |
        FCS Phase 1-2 = 60 |
        FCS Phase 3 = 34 |
        FCS Phase 4-5 = 5

    Returns
    -------
    pandas.DataFrame
    """

    data = df.copy()

    # ------------------------------------------------------
    # Check for duplicate category records
    # ------------------------------------------------------

    duplicate_keys = [
        "country",
        "adm1_name",
        "date",
        "indicator",
        "category",
    ]

    duplicates = data.duplicated(
        subset=duplicate_keys,
        keep=False,
    )

    if duplicates.any():

        duplicate_count = (
            duplicates.sum()
        )

        raise ValueError(
            f"Found {duplicate_count} duplicate outcome "
            f"category records. Expected one value per "
            f"country × ADM1 × date × indicator × category."
        )

    # ------------------------------------------------------
    # Pivot categories
    # ------------------------------------------------------

    current = (
        data
        .pivot(
            index=[
                "country",
                "adm1_name",
                "date",
                "indicator",
            ],
            columns="category",
            values="value",
        )
        .reset_index()
    )

    # Remove pandas column-axis name
    current.columns.name = None

    return current


# ==========================================================
# CALCULATE DETERIORATION
# ==========================================================

def prepare_deterioration_metrics(
    df,
    min_history=MIN_HISTORY_MONTHS,
):
    """
    Run the outcome hybrid methodology.

    Returns one record per:

        country × adm1_name × date × indicator
    """

    metrics = (
        compute_outcome_hybrid_metrics(
            df,
            min_history=min_history,
        )
    )

    return metrics


# ==========================================================
# MERGE CURRENT CONDITION + DETERIORATION
# ==========================================================

def merge_outcome_components(
    current_condition,
    deterioration_metrics,
):
    """
    Merge current outcome condition with deterioration metrics.

    Join keys:
        country
        adm1_name
        date
        indicator
    """

    join_cols = [
        "country",
        "adm1_name",
        "date",
        "indicator",
    ]

    # ------------------------------------------------------
    # Ensure deterioration metrics are unique
    # ------------------------------------------------------

    duplicates = (
        deterioration_metrics
        .duplicated(
            subset=join_cols,
            keep=False,
        )
    )

    if duplicates.any():

        raise ValueError(
            "Deterioration metrics contain duplicate "
            "country × ADM1 × date × indicator records."
        )

    # ------------------------------------------------------
    # Merge
    # ------------------------------------------------------

    final = current_condition.merge(
        deterioration_metrics,
        on=join_cols,
        how="left",
        validate="one_to_one",
    )

    return final


# ==========================================================
# ORGANIZE OUTPUT COLUMNS
# ==========================================================

def organize_output_columns(df):
    """
    Organize the final dataset so that identification fields,
    current-condition prevalences and deterioration metrics
    appear in a logical order.
    """

    data = df.copy()

    id_cols = [
        "country",
        "adm1_name",
        "date",
        "indicator",
    ]

    metric_cols = [
        "adverse_prevalence",
        "history_months",
        "previous_value",
        "baseline_value",
        "anomaly_pp",
        "mom_change_pp",
        "deterioration_direction",
        "baseline_status",
        "mom_status",
        "deterioration_status",
    ]

    # ------------------------------------------------------
    # Category prevalence columns
    # ------------------------------------------------------

    category_cols = [
        col
        for col in data.columns
        if (
            col not in id_cols
            and col not in metric_cols
        )
    ]

    # ------------------------------------------------------
    # Keep only existing metric columns
    # ------------------------------------------------------

    metric_cols = [
        col
        for col in metric_cols
        if col in data.columns
    ]

    final_order = (
        id_cols
        + category_cols
        + metric_cols
    )

    data = data[
        final_order
    ]

    return data


# ==========================================================
# RUN OUTCOME PIPELINE
# ==========================================================

def run_outcome_pipeline(
    df,
    min_history=MIN_HISTORY_MONTHS,
):
    """
    Run the complete RAAp outcome indicator preparation
    pipeline.

    Workflow
    --------

    Raw outcome data
            ↓
    clean / validate
            ↓
        ┌───────────────┐
        │               │
        ↓               ↓
    current          deterioration
    condition           metrics
        │               │
        └───────┬───────┘
                ↓
              merge
                ↓
       dashboard-ready dataset

    Parameters
    ----------
    df : pandas.DataFrame
        Long-format outcome indicator data.

    min_history : int
        Minimum number of previous observations required
        before the recent baseline is considered available.

    Returns
    -------
    pandas.DataFrame
    """

    # ------------------------------------------------------
    # 1. Clean input
    # ------------------------------------------------------

    data = clean_outcome_data(
        df
    )

    # ------------------------------------------------------
    # 2. Current condition
    # ------------------------------------------------------

    current_condition = (
        prepare_current_condition(
            data
        )
    )

    # ------------------------------------------------------
    # 3. Deterioration metrics
    # ------------------------------------------------------

    deterioration_metrics = (
        prepare_deterioration_metrics(
            data,
            min_history=min_history,
        )
    )

    # ------------------------------------------------------
    # 4. Merge components
    # ------------------------------------------------------

    final = merge_outcome_components(
        current_condition,
        deterioration_metrics,
    )

    # ------------------------------------------------------
    # 5. Organize columns
    # ------------------------------------------------------

    final = organize_output_columns(
        final
    )

    # ------------------------------------------------------
    # 6. Sort
    # ------------------------------------------------------

    final = final.sort_values(
        [
            "country",
            "adm1_name",
            "indicator",
            "date",
        ]
    ).reset_index(
        drop=True
    )

    return final


# ==========================================================
# STANDALONE TEST
# ==========================================================

if __name__ == "__main__":

    # ------------------------------------------------------
    # Input
    # ------------------------------------------------------

    input_file = os.path.join(
        PROJECT_ROOT,
        "data",
        "ipc_indicators.xlsx"
    )

    # ------------------------------------------------------
    # Output
    # ------------------------------------------------------

    output_folder = os.path.join(
        PROJECT_ROOT,
        "src",
        "outputs"
    )

    output_file = os.path.join(
        output_folder,
        "outcome_pipeline_test.xlsx"
    )

    # ------------------------------------------------------
    # Load
    # ------------------------------------------------------

    print("=" * 80)
    print("RAAp OUTCOME INDICATOR PIPELINE")
    print("=" * 80)

    print(
        f"\n📂 Loading:\n"
        f"{input_file}"
    )

    df = pd.read_excel(
        input_file
    )

    print(
        f"\n📊 Raw records: "
        f"{len(df):,}"
    )

    # ------------------------------------------------------
    # Run pipeline
    # ------------------------------------------------------

    result = run_outcome_pipeline(
        df,
        min_history=MIN_HISTORY_MONTHS,
    )

    # ------------------------------------------------------
    # Save
    # ------------------------------------------------------

    os.makedirs(
        output_folder,
        exist_ok=True
    )

    result.to_excel(
        output_file,
        index=False,
    )

    # ------------------------------------------------------
    # Console checks
    # ------------------------------------------------------

    print(
        f"\n📊 Final records: "
        f"{len(result):,}"
    )

    print(
        f"\n📊 Final columns:"
    )

    for col in result.columns:
        print(f"   - {col}")

    print(
        "\nFirst 20 records:"
    )

    print(
        result.head(20)
        .to_string(
            index=False
        )
    )

    print("\n" + "=" * 80)
    print("✅ OUTCOME PIPELINE COMPLETED")
    print("=" * 80)

    print(
        f"\n📁 Output saved to:\n"
        f"{output_file}"
    )
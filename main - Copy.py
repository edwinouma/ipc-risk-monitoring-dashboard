from src.data_loader import load_data
from src.preprocessing import preprocess_data
from src.spatial_percentiles import compute_spatial_percentiles
from src.composite_thresholds import compute_composite_thresholds
from src.thresholds_tukey import compute_tukey_thresholds
from src.monthly_outputs import compute_monthly_quartiles_with_iqr
from src.trigger_counts import compute_monthly_trigger_counts
from src.plot_triggers import (
    plot_monthly_trigger_counts,
    plot_monthly_trigger_counts_interactive
)
from src.classification_matrix import compute_unit_month_classification_matrix
from src.export_colored_matrix import export_colored_classification_matrix
from src.unit_month import compute_unit_month_values
from src.config import *

import pandas as pd
import os


# 🔹 NEW: Robust retention threshold (does NOT affect baseline logic)
ROBUST_MIN_RETENTION = 40


def main():

    # ---------------------------------------------------
    # 0. Ensure outputs folder exists
    # ---------------------------------------------------
    os.makedirs("outputs", exist_ok=True)

    # ---------------------------------------------------
    # 1. Load Data
    # ---------------------------------------------------
    df = load_data("data/rainfall_ndvi.xlsx")

    # ---------------------------------------------------
    # 2. Preprocess
    # ---------------------------------------------------
    df = preprocess_data(df, DATE_COL)

    all_thresholds = []
    all_monthly_tables = []
    all_trigger_counts = []
    all_unit_month_values = []
    all_spatial_percentiles = []

    # ---------------------------------------------------
    # 3. Compute Thresholds Per Indicator
    # ---------------------------------------------------
    for ind in INDICATORS:

        print(f"\nProcessing Indicator: {ind}")

        # -----------------------------------------
        # A. Store unit-month values (for dashboard)
        # -----------------------------------------
        unit_month = compute_unit_month_values(
            df=df,
            unit_col=UNIT_COL,
            indicator_col=INDICATOR_COL,
            value_col=VALUE_COL,
            indicator_name=ind,
            aggregation="mean"
        )

        unit_month["indicator"] = ind
        all_unit_month_values.append(unit_month)

        # =========================================================
        # BASELINE (ALL MONTHS)
        # =========================================================

        spatial = compute_spatial_percentiles(
            df,
            UNIT_COL,
            DATE_COL,
            INDICATOR_COL,
            VALUE_COL,
            ind
        )

        spatial["retention_filter"] = "none"
        spatial["season_scope"] = "All Months"
        all_spatial_percentiles.append(spatial)

        monthly_table = compute_monthly_quartiles_with_iqr(
            spatial,
            DATE_COL
        )
        all_monthly_tables.append(monthly_table)

        percentile_thresholds = compute_composite_thresholds(spatial)

        percentile_thresholds = percentile_thresholds.rename(columns={
            "alert_threshold": "alert_percentile",
            "alarm_threshold": "alarm_percentile"
        })

        tukey_thresholds = compute_tukey_thresholds(spatial)

        merged_thresholds = percentile_thresholds.merge(
            tukey_thresholds,
            on="indicator",
            how="left"
        )

        merged_thresholds["retention_filter"] = "none"
        merged_thresholds["season_scope"] = "All Months"
        all_thresholds.append(merged_thresholds)

        # =========================================================
        # ROBUST (ALL MONTHS)
        # =========================================================

        spatial_robust = compute_spatial_percentiles(
            df,
            UNIT_COL,
            DATE_COL,
            INDICATOR_COL,
            VALUE_COL,
            ind,
            min_retention_pct=ROBUST_MIN_RETENTION
        )

        spatial_robust["retention_filter"] = f">={ROBUST_MIN_RETENTION}%"
        spatial_robust["season_scope"] = "All Months"
        all_spatial_percentiles.append(spatial_robust)

        if not spatial_robust.empty:

            pct_robust = compute_composite_thresholds(spatial_robust)
            pct_robust = pct_robust.rename(columns={
                "alert_threshold": "alert_percentile",
                "alarm_threshold": "alarm_percentile"
            })

            tukey_robust = compute_tukey_thresholds(spatial_robust)

            merged_robust = pct_robust.merge(
                tukey_robust,
                on="indicator",
                how="left"
            )

            merged_robust["retention_filter"] = f">={ROBUST_MIN_RETENTION}%"
            merged_robust["season_scope"] = "All Months"
            all_thresholds.append(merged_robust)

        # =========================================================
        # 🔹 NEW: SEASONAL THRESHOLDS (ADDITIONAL ONLY)
        # =========================================================

        seasonal_dict = SEASONAL_DEFINITIONS.get(ind, {})

        for season_name, season_months in seasonal_dict.items():

            if season_months is None:
                continue

            print(f"  → Seasonal thresholds: {season_name}")

            # ---- Baseline Seasonal ----
            spatial_season = compute_spatial_percentiles(
                df,
                UNIT_COL,
                DATE_COL,
                INDICATOR_COL,
                VALUE_COL,
                ind,
                season_months=season_months
            )

            if not spatial_season.empty:

                pct_season = compute_composite_thresholds(spatial_season)
                pct_season = pct_season.rename(columns={
                    "alert_threshold": "alert_percentile",
                    "alarm_threshold": "alarm_percentile"
                })

                tukey_season = compute_tukey_thresholds(spatial_season)

                merged_season = pct_season.merge(
                    tukey_season,
                    on="indicator",
                    how="left"
                )

                merged_season["retention_filter"] = "none"
                merged_season["season_scope"] = season_name
                all_thresholds.append(merged_season)

            # ---- Robust Seasonal ----
            spatial_season_robust = compute_spatial_percentiles(
                df,
                UNIT_COL,
                DATE_COL,
                INDICATOR_COL,
                VALUE_COL,
                ind,
                min_retention_pct=ROBUST_MIN_RETENTION,
                season_months=season_months
            )

            if not spatial_season_robust.empty:

                pct_season_r = compute_composite_thresholds(spatial_season_robust)
                pct_season_r = pct_season_r.rename(columns={
                    "alert_threshold": "alert_percentile",
                    "alarm_threshold": "alarm_percentile"
                })

                tukey_season_r = compute_tukey_thresholds(spatial_season_robust)

                merged_season_r = pct_season_r.merge(
                    tukey_season_r,
                    on="indicator",
                    how="left"
                )

                merged_season_r["retention_filter"] = f">={ROBUST_MIN_RETENTION}%"
                merged_season_r["season_scope"] = season_name
                all_thresholds.append(merged_season_r)

    # ---------------------------------------------------
    # 4. Combine Thresholds
    # ---------------------------------------------------
    final_thresholds = pd.concat(all_thresholds, ignore_index=True)

    # ---------------------------------------------------
    # 5. Combine Unit-Month Values
    # ---------------------------------------------------
    final_unit_month = pd.concat(all_unit_month_values, ignore_index=True)

    # ---------------------------------------------------
    # 6. Combine Spatial Percentiles
    # ---------------------------------------------------
    final_spatial_percentiles = pd.concat(
        all_spatial_percentiles,
        ignore_index=True
    )

    # ---------------------------------------------------
    # 7. Compute Trigger Counts (BASELINE ONLY - unchanged)
    # ---------------------------------------------------
    for ind in INDICATORS:

        trigger_counts = compute_monthly_trigger_counts(
            df,
            UNIT_COL,
            INDICATOR_COL,
            VALUE_COL,
            ind,
            final_thresholds[
                (final_thresholds["retention_filter"] == "none") &
                (final_thresholds["season_scope"] == "All Months")
            ]
        )

        all_trigger_counts.append(trigger_counts)

    final_trigger_counts = pd.concat(all_trigger_counts, ignore_index=True)

    # ---------------------------------------------------
    # 8. Combine Monthly Quartile Tables
    # ---------------------------------------------------
    final_monthly_table = pd.concat(all_monthly_tables, ignore_index=True)

    # ---------------------------------------------------
    # 9. Save Tables
    # ---------------------------------------------------
    final_thresholds.to_csv("outputs/thresholds_results.csv", index=False)
    final_monthly_table.to_csv("outputs/monthly_quartiles_iqr.csv", index=False)
    final_trigger_counts.to_csv("outputs/monthly_trigger_counts.csv", index=False)
    final_unit_month.to_parquet("outputs/unit_month_values.parquet", index=False)
    final_spatial_percentiles.to_csv("outputs/spatial_percentiles_with_proportions.csv", index=False)

    print("\nTables saved successfully.")

    # ---------------------------------------------------
    # 10. Charts (UNCHANGED)
    # ---------------------------------------------------
    for ind in INDICATORS:

        print(f"Generating charts for: {ind}")

        plot_monthly_trigger_counts(
            final_trigger_counts,
            indicator_name=ind,
            method="percentile",
            use_percent=False,
            save_path="outputs"
        )

        plot_monthly_trigger_counts(
            final_trigger_counts,
            indicator_name=ind,
            method="tukey",
            use_percent=False,
            save_path="outputs"
        )

        plot_monthly_trigger_counts_interactive(
            final_trigger_counts,
            indicator_name=ind,
            method="percentile",
            use_percent=False,
            save_path="outputs"
        )

        plot_monthly_trigger_counts_interactive(
            final_trigger_counts,
            indicator_name=ind,
            method="tukey",
            use_percent=False,
            save_path="outputs"
        )

    # ---------------------------------------------------
    # 11. Classification Matrices (UNCHANGED)
    # ---------------------------------------------------
    for ind in INDICATORS:

        print(f"Generating classification matrix for: {ind}")

        row = final_thresholds[
            (final_thresholds["indicator"] == ind) &
            (final_thresholds["retention_filter"] == "none") &
            (final_thresholds["season_scope"] == "All Months")
        ].iloc[0]

        alarm_percentile = row["alarm_percentile"]
        alert_percentile = row["alert_percentile"]
        alarm_tukey = row["alarm_tukey"]
        alert_tukey = row["alert_tukey"]

        matrix_percentile = compute_unit_month_classification_matrix(
            df=df,
            unit_col=UNIT_COL,
            indicator_col=INDICATOR_COL,
            value_col=VALUE_COL,
            indicator_name=ind,
            alarm_threshold=alarm_percentile,
            alert_threshold=alert_percentile
        )

        matrix_tukey = compute_unit_month_classification_matrix(
            df=df,
            unit_col=UNIT_COL,
            indicator_col=INDICATOR_COL,
            value_col=VALUE_COL,
            indicator_name=ind,
            alarm_threshold=alarm_tukey,
            alert_threshold=alert_tukey
        )

        safe_name = ind.replace(" ", "_").replace("%", "")

        export_colored_classification_matrix(
            matrix_percentile,
            f"outputs/{safe_name}_percentile_classification_matrix.xlsx"
        )

        export_colored_classification_matrix(
            matrix_tukey,
            f"outputs/{safe_name}_tukey_classification_matrix.xlsx"
        )

    print("\nFinal Threshold Comparison:")
    print(final_thresholds)

    print("\nAll products generated successfully.")


if __name__ == "__main__":
    main()
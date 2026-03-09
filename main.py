from src.data_loader import load_rainfall_data, load_price_data
from src.price_monthly import compute_monthly_prices
from src.ltm_baseline import compute_long_term_monthly_median
from src.ltm_anomaly import compute_ltm_anomaly
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
from src.price_baselines import compute_price_baseline
from src.config import BASELINE_METHODS
import pandas as pd
import os


ROBUST_MIN_RETENTION = 40


def main():

    import time
    start_time = time.time()

    os.makedirs("outputs", exist_ok=True)

    all_rainfall = []
    all_prices = []

    for country, cfg in COUNTRY_CONFIG.items():

        print(f"Loading data for {country}")

        rainfall_path = cfg["rainfall_file"]

        if os.path.exists(rainfall_path):

            df_rain = load_rainfall_data(rainfall_path)
            df_rain = preprocess_data(df_rain, DATE_COL)

            df_rain["country"] = country
            all_rainfall.append(df_rain)

        else:
            print(f"Rainfall file not found for {country}")

        price_path = cfg["price_file"]

        if os.path.exists(price_path):

            df_price = load_price_data(price_path)
            df_price = preprocess_data(df_price, DATE_COL)

            df_price["country"] = country
            all_prices.append(df_price)

        else:
            print(f"Price file not found for {country}")

    df_rainfall = pd.concat(all_rainfall, ignore_index=True)
    df_price_raw = pd.concat(all_prices, ignore_index=True)

    df_price_monthly = compute_monthly_prices(df_price_raw)

    baseline = compute_long_term_monthly_median(df_price_monthly)

    baseline_export = baseline.copy()

    baseline_export["month_name"] = pd.to_datetime(
        baseline_export["month"], format="%m"
    ).dt.strftime("%b")

    baseline_export = baseline_export[
        [UNIT_COL, INDICATOR_COL, "month", "month_name", "baseline_median"]
    ]

    baseline_export.to_excel(
        "outputs/price_long_term_monthly_median_baseline.xlsx",
        index=False
    )

    print("Price long-term monthly median baseline saved.")

    price_datasets = []

    for method in BASELINE_METHODS:

        print(f"Computing price baseline: {method}")

        df_method = compute_price_baseline(
            method,
            df_price_monthly,
            baseline
        )

        price_datasets.append(df_method)

    df_price_anom = pd.concat(price_datasets, ignore_index=True)

    df_price_standard = df_price_anom[
        ["country", UNIT_COL, "year_month", INDICATOR_COL, VALUE_COL, "baseline_method"]
    ].copy()

    df_price_standard = df_price_standard.rename(columns={
        UNIT_COL: "adm1_name",
        INDICATOR_COL: "indicator",
        VALUE_COL: "value"
    })

    price_export = df_price_standard.copy()
    price_export["year_month"] = price_export["year_month"].astype(str)

    price_export.to_excel(
        "outputs/price_monthly_percent_deviation.xlsx",
        index=False
    )

    print("Price monthly percent deviation file saved.")

    df_rainfall_standard = df_rainfall[
        ["country", UNIT_COL, "year_month", INDICATOR_COL, VALUE_COL]
    ].copy()

    df_rainfall_standard = df_rainfall_standard.rename(columns={
        UNIT_COL: "adm1_name",
        INDICATOR_COL: "indicator",
        VALUE_COL: "value"
    })

    df_rainfall_standard["baseline_method"] = DEFAULT_BASELINE

    df = pd.concat(
        [df_rainfall_standard, df_price_standard],
        ignore_index=True
    ).sort_values(["country", "year_month", UNIT_COL])

    df.to_csv("outputs/merged_standardized_dataset.csv", index=False)

    print(f"\nTotal indicators to process: {len(INDICATORS)}")

    all_thresholds = []
    all_monthly_tables = []
    all_trigger_counts = []
    all_unit_month_values = []
    all_spatial_percentiles = []

    for country in df["country"].unique():

        df_country = df[df["country"] == country].copy()
        country_indicators = df_country["indicator"].unique()

        for ind in country_indicators:

            if ind in PRICE_INDICATORS:
                baseline_list = BASELINE_METHODS
            else:
                baseline_list = [DEFAULT_BASELINE]

            for baseline_method in baseline_list:

                print(f"\nProcessing Indicator: {ind} | Baseline: {baseline_method}")

                df_indicator = df_country[df_country["indicator"] == ind].copy()

                df_indicator = df_indicator[
                    (df_indicator["baseline_method"] == baseline_method)
                ] if "baseline_method" in df_indicator.columns else df_indicator

                if df_indicator.empty:
                    print(f"Skipping {ind} | {baseline_method} (no data)")
                    continue

                unit_month = compute_unit_month_values(
                    df=df_indicator,
                    unit_col=UNIT_COL,
                    indicator_col=INDICATOR_COL,
                    value_col=VALUE_COL,
                    indicator_value=ind,
                    aggregation="mean"
                )

                unit_month["indicator"] = ind
                unit_month["baseline_method"] = baseline_method

                all_unit_month_values.append(unit_month)

                spatial = compute_spatial_percentiles(
                    df_indicator,
                    UNIT_COL,
                    DATE_COL,
                    INDICATOR_COL,
                    VALUE_COL,
                    ind
                )

                spatial["retention_filter"] = "none"
                spatial["season_scope"] = "All Months"
                all_spatial_percentiles.append(spatial)

                monthly_table = compute_monthly_quartiles_with_iqr(spatial, DATE_COL)
                all_monthly_tables.append(monthly_table)

                percentile_thresholds = compute_composite_thresholds(spatial, ind)

                percentile_thresholds = percentile_thresholds.rename(columns={
                    "alert_threshold": "alert_percentile",
                    "alarm_threshold": "alarm_percentile"
                })

                tukey_thresholds = compute_tukey_thresholds(spatial, ind)

                merged_thresholds = percentile_thresholds.merge(
                    tukey_thresholds,
                    on="indicator",
                    how="left"
                )

                merged_thresholds["retention_filter"] = "none"
                merged_thresholds["season_scope"] = "All Months"
                merged_thresholds["baseline_method"] = baseline_method
                merged_thresholds["country"] = country

                all_thresholds.append(merged_thresholds)

                spatial_robust = compute_spatial_percentiles(
                    df_indicator,
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

                    pct_robust = compute_composite_thresholds(spatial_robust, ind)

                    pct_robust = pct_robust.rename(columns={
                        "alert_threshold": "alert_percentile",
                        "alarm_threshold": "alarm_percentile"
                    })

                    tukey_robust = compute_tukey_thresholds(spatial_robust, ind)

                    merged_robust = pct_robust.merge(
                        tukey_robust,
                        on="indicator",
                        how="left"
                    )

                    merged_robust["retention_filter"] = f">={ROBUST_MIN_RETENTION}%"
                    merged_robust["season_scope"] = "All Months"
                    merged_robust["baseline_method"] = baseline_method
                    merged_robust["country"] = country

                    all_thresholds.append(merged_robust)

                seasonal_dict = SEASONAL_DEFINITIONS.get(ind, {})

                for season_name, season_months in seasonal_dict.items():

                    if season_months is None:
                        continue

                    spatial_season = compute_spatial_percentiles(
                        df_indicator,
                        UNIT_COL,
                        DATE_COL,
                        INDICATOR_COL,
                        VALUE_COL,
                        ind,
                        season_months=season_months
                    )

                    if not spatial_season.empty:

                        pct_season = compute_composite_thresholds(spatial_season, ind)

                        pct_season = pct_season.rename(columns={
                            "alert_threshold": "alert_percentile",
                            "alarm_threshold": "alarm_percentile"
                        })

                        tukey_season = compute_tukey_thresholds(spatial_season, ind)

                        merged_season = pct_season.merge(
                            tukey_season,
                            on="indicator",
                            how="left"
                        )

                        merged_season["retention_filter"] = "none"
                        merged_season["season_scope"] = season_name
                        merged_season["baseline_method"] = baseline_method
                        merged_season["country"] = country

                        all_thresholds.append(merged_season)

    final_thresholds = pd.concat(
        [df for df in all_thresholds if not df.empty],
        ignore_index=True
    ) if any(not df.empty for df in all_thresholds) else pd.DataFrame()

    final_unit_month = pd.concat(
        [df for df in all_unit_month_values if not df.empty],
        ignore_index=True
    ) if any(not df.empty for df in all_unit_month_values) else pd.DataFrame()

    valid_spatial = [df for df in all_spatial_percentiles if not df.empty]

    final_spatial_percentiles = (
        pd.concat(valid_spatial, ignore_index=True)
        .sort_values(["indicator", "year_month"])
        if valid_spatial else pd.DataFrame()
    )

    print("\nPipeline completed successfully.")

    # ---------------------------------------------------
    # 7. Compute Trigger Counts
    # ---------------------------------------------------
    for ind in INDICATORS:

        if final_thresholds.empty:
            print("No thresholds available. Skipping trigger counts.")
            break

        # Skip indicators that have no thresholds
        if ind not in final_thresholds["indicator"].values:
            print(f"Skipping trigger counts for {ind} (no thresholds)")
            continue

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

    final_trigger_counts = pd.concat(
        [df for df in all_trigger_counts if not df.empty],
        ignore_index=True
    ) if any(not df.empty for df in all_trigger_counts) else pd.DataFrame()

    # ---------------------------------------------------
    # 8. Combine Monthly Quartile Tables
    # ---------------------------------------------------
    final_monthly_table = pd.concat(
        [df for df in all_monthly_tables if not df.empty],
        ignore_index=True
    ) if any(not df.empty for df in all_monthly_tables) else pd.DataFrame()

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
            indicator_value=ind,
            method="percentile",
            use_percent=False,
            save_path="outputs"
        )

        plot_monthly_trigger_counts(
            final_trigger_counts,
            indicator_value=ind,
            method="tukey",
            use_percent=False,
            save_path="outputs"
        )

        plot_monthly_trigger_counts_interactive(
            final_trigger_counts,
            indicator_value=ind,
            method="percentile",
            use_percent=False,
            save_path="outputs"
        )

        plot_monthly_trigger_counts_interactive(
            final_trigger_counts,
            indicator_value=ind,
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
            (final_thresholds["season_scope"] == "All Months") &
            (final_thresholds["baseline_method"] == DEFAULT_BASELINE)
            ]

        if row.empty:
            print(f"No thresholds found for {ind}")
            continue

        row = row.iloc[0]

        alarm_percentile = row["alarm_percentile"]
        alert_percentile = row["alert_percentile"]
        alarm_tukey = row["alarm_tukey"]
        alert_tukey = row["alert_tukey"]

        df_matrix = df.copy()

        # Use default baseline for pipeline outputs
        if "baseline_method" in df_matrix.columns:
            df_matrix = df_matrix[df_matrix["baseline_method"] == DEFAULT_BASELINE]

        matrix_percentile = compute_unit_month_classification_matrix(
            df=df_matrix,
            unit_col=UNIT_COL,
            indicator_col=INDICATOR_COL,
            value_col=VALUE_COL,
            indicator_value=ind,
            alarm_threshold=alarm_percentile,
            alert_threshold=alert_percentile
        )

        matrix_tukey = compute_unit_month_classification_matrix(
            df=df_matrix,
            unit_col=UNIT_COL,
            indicator_col=INDICATOR_COL,
            value_col=VALUE_COL,
            indicator_value=ind,
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

    print(f"\nPipeline completed in {round(time.time() - start_time, 2)} seconds.")


if __name__ == "__main__":
    main()
from src.conflict_hybrid import classify_conflict_row
from src.config import ADM1_GROUP_MAPPING
from src.zscore_true import compute_true_zscore
from src.data_loader import (
    load_rainfall_data,
    load_price_data,
    load_conflict_data,
    load_flood_data,
    load_ipc_data   # 🔥 ADD THIS
)

from src.config import CLASSIFICATION_LABELS

from src.preprocessing import preprocess_data, process_flood_data
from src.price_monthly import compute_monthly_prices
from src.ltm_baseline import compute_long_term_monthly_median
from src.ltm_anomaly import compute_ltm_anomaly
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
from src.config import BASELINE_METHODS, INDICATOR_ALLOWED_BASELINES, EVENT_THRESHOLDS
from src.conflict_baseline import compute_conflict_baseline
from src.tot_calculation import compute_tot
from src.config import TOT_CONFIG, DERIVED_INDICATORS
from src.spi_true import compute_true_spi
import pandas as pd
import os
import numpy as np

ROBUST_MIN_RETENTION = 40

import streamlit as st

# ---------------------------------------------------
# IPC MATRIX PREPARATION
# ---------------------------------------------------
def prepare_ipc_matrix(df_ipc):
    import pandas as pd

    if df_ipc is None or df_ipc.empty:
        return pd.DataFrame()

    df = df_ipc.copy()

    # -----------------------------------------
    # Short labels for analysis_type
    # -----------------------------------------
    df["analysis_short"] = df["analysis_type"].map({
        "current": "C",
        "projection 1": "P1",
        "projection 2": "P2",
        "projection 2 update":"P2-U"
    }).fillna(df["analysis_type"])

    # -----------------------------------------
    # Combine phase + type (KEEP "phase X")
    # -----------------------------------------
    df["ipc_combined"] = (
        df["ipc_phase"] + " (" + df["analysis_short"] + ")"
    )

    # -----------------------------------------
    # Pivot → ONE CELL PER UNIT-MONTH
    # -----------------------------------------
    ipc_matrix = df.pivot_table(
        index="adm1_name",
        columns="year_month",
        values="ipc_combined",
        aggfunc=lambda x: " | ".join(sorted(x))
    )

    # 🔥 ADD THIS (CRITICAL FIX)
    ipc_matrix = ipc_matrix.fillna("No data")

    return ipc_matrix

@st.cache_data
def main():

    import time
    start_time = time.time()

    os.makedirs("outputs", exist_ok=True)

    all_rainfall = []
    all_prices = []
    all_conflict = []
    all_flood = []
    all_ipc = []

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

        # -------------------------
        # Conflict
        # -------------------------
        conflict_path = cfg.get("conflict_file")

        if conflict_path and os.path.exists(conflict_path):

            df_conflict = load_conflict_data(conflict_path, country=country)

            # Ensure outputs folder exists
            output_dir = "outputs"
            os.makedirs(output_dir, exist_ok=True)

            # Save file in outputs folder
            output_path = os.path.join(output_dir, f"conflict_data_{country}.csv")
            df_conflict.to_csv(output_path, index=False)

            print(f"Conflict data for {country} saved successfully at: {output_path}")

            all_conflict.append(df_conflict)

        else:
            print(f"Conflict file not found for {country}")

        # -------------------------
        # Flood
        # -------------------------
        flood_path = cfg.get("flood_file")

        if flood_path and os.path.exists(flood_path):

            df_flood = load_flood_data(flood_path)
            df_flood = process_flood_data(df_flood, country=country)

            output_dir = "outputs"
            os.makedirs(output_dir, exist_ok=True)

            output_path = os.path.join(output_dir, f"flood_data_{country}.csv")
            df_flood.to_csv(output_path, index=False)

            print(f"Flood data for {country} saved successfully at: {output_path}")

            all_flood.append(df_flood)

        else:
            print(f"Flood file not found for {country}")

        # -------------------------
        # IPC (NEW)
        # -------------------------
        ipc_path = cfg.get("ipc_file")

        if ipc_path and os.path.exists(ipc_path):

            df_ipc_country = load_ipc_data(ipc_path)
            df_ipc_country["country"] = country

            all_ipc.append(df_ipc_country)

            print(f"IPC data for {country} loaded successfully.")

        else:
            print(f"IPC file not found for {country}")

    df_rainfall = pd.concat(all_rainfall, ignore_index=True)
    df_price_raw = pd.concat(all_prices, ignore_index=True)
    df_conflict = (
        pd.concat(all_conflict, ignore_index=True)
        if all_conflict else pd.DataFrame()
    )

    df_flood = (
        pd.concat(all_flood, ignore_index=True)
        if all_flood else pd.DataFrame()
    )

    # -------------------------
    # IPC CONCAT (FINAL FIX)
    # -------------------------
    df_ipc = (
        pd.concat(all_ipc, ignore_index=True)
        if all_ipc else pd.DataFrame()
    )

    df_price_monthly = compute_monthly_prices(df_price_raw)

    # ---------------------------------------------------
    # 🔥 Compute ToT EARLY (BEFORE BASELINES)
    # ---------------------------------------------------
    tot_all = []

    for c in df_price_monthly["country"].unique():

        df_c = df_price_monthly[df_price_monthly["country"] == c].copy()

        tot_df = compute_tot(df_c, c, TOT_CONFIG)

        if not tot_df.empty:
            tot_df["country"] = c
            tot_all.append(tot_df)

    # Combine all ToT into monthly data
    if tot_all:
        tot_all_df = pd.concat(tot_all, ignore_index=True)

        df_price_monthly = pd.concat(
            [df_price_monthly, tot_all_df],
            ignore_index=True
        )

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

    df_price_standard["group"] = df_price_standard["adm1_name"].map(ADM1_GROUP_MAPPING)

    df_price_standard = df_price_standard.rename(columns={
        UNIT_COL: "adm1_name",
        INDICATOR_COL: "indicator",
        VALUE_COL: "value"
    })

    price_export = df_price_standard.copy()
    price_export["year_month"] = price_export["year_month"].astype(str)

    # AFTER ToT computation
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

    df_rainfall_standard["group"] = df_rainfall_standard["adm1_name"].map(ADM1_GROUP_MAPPING)

    df_rainfall_standard = df_rainfall_standard.rename(columns={
        UNIT_COL: "adm1_name",
        INDICATOR_COL: "indicator",
        VALUE_COL: "value"
    })

    df_rainfall_standard["baseline_method"] = "none"

    # ---------------------------------------------------
    # Flood standardization
    # ---------------------------------------------------
    if not df_flood.empty:

        df_flood_standard = df_flood[
            ["country", UNIT_COL, "year_month", INDICATOR_COL, VALUE_COL]
        ].copy()

        df_flood_standard["group"] = df_flood_standard["adm1_name"].map(ADM1_GROUP_MAPPING)

        df_flood_standard = df_flood_standard.rename(columns={
            UNIT_COL: "adm1_name",
            INDICATOR_COL: "indicator",
            VALUE_COL: "value"
        })

        df_flood_standard["baseline_method"] = "none"

    else:
        df_flood_standard = pd.DataFrame()

    # ---------------------------------------------------
    # Conflict baseline processing
    # ---------------------------------------------------
    conflict_datasets = []

    for ind in df_conflict["indicator"].unique():

        method_type = INDICATOR_METHOD.get(ind, "percentile")

        df_ind = df_conflict[df_conflict["indicator"] == ind].copy()

        # ---------------------------------------------------
        # EVENT INDICATORS → NO BASELINE
        # ---------------------------------------------------
        if method_type == "event" and ind not in ["conflict_events", "conflict_fatalities"]:

            df_ind["baseline_method"] = "none"
            conflict_datasets.append(df_ind)

            print(f"Skipping baseline for {ind} (event-based)")


        else:

            # ---------------------------------------------------

            # 🔥 FORCE HYBRID FOR CONFLICT (CRITICAL FIX)

            # ---------------------------------------------------

            if ind in ["conflict_events", "conflict_fatalities"]:
                print(f"Applying hybrid baseline for {ind}")

                df_method = compute_conflict_baseline(

                    method="hybrid",

                    monthly_conflict=df_ind

                )

                conflict_datasets.append(df_method)

                continue  # 🔥 skip normal baseline logic

            # ---------------------------------------------------

            # NORMAL BASELINE LOGIC (UNCHANGED)

            # ---------------------------------------------------

            methods = INDICATOR_ALLOWED_BASELINES.get(ind, [])

            for method in methods:

                # 🔥 skip NONE before calling function

                if method.upper() == "NONE":
                    df_copy = df_ind.copy()

                    df_copy["baseline_method"] = "none"

                    conflict_datasets.append(df_copy)

                    print(f"Using raw values for {ind} (NONE)")

                    continue

                print(f"Computing {ind} baseline: {method}")

                df_method = compute_conflict_baseline(method, df_ind)

                conflict_datasets.append(df_method)

    df_conflict_anom = pd.concat(conflict_datasets, ignore_index=True)

    # ---------------------------------------------------
    # 🔍 DEBUG: Inspect conflict dataset after concat
    # ---------------------------------------------------

    print("\n===== DEBUG: df_conflict_anom COLUMNS =====")
    print(df_conflict_anom.columns.tolist())

    print("\n===== DEBUG: SAMPLE ROWS =====")
    print(df_conflict_anom.head(10))

    print("\n===== DEBUG: CHECK SIGNAL PRESENCE =====")
    required_cols = [
        "yoy_signal",
        "yoy_ratio",
        "anomaly_signal",
        "anomaly_ratio"
    ]

    for col in required_cols:
        print(f"{col}: {'✅ EXISTS' if col in df_conflict_anom.columns else '❌ MISSING'}")

    # Optional: export to file for inspection
    df_conflict_anom.to_excel("outputs/debug_conflict_anom.xlsx", index=False)
    print("\n✅ Debug file saved: outputs/debug_conflict_anom.xlsx")

    df_conflict_standard = df_conflict_anom[
        [
            "country",
            UNIT_COL,
            "year_month",
            INDICATOR_COL,
            VALUE_COL,
            "baseline_method",
            "yoy_signal",
            "yoy_ratio",
            "anomaly_signal",
            "anomaly_ratio"
        ]
    ].copy()

    df_conflict_standard["group"] = df_conflict_standard["adm1_name"].map(ADM1_GROUP_MAPPING)

    df_conflict_standard = df_conflict_standard.rename(columns={
        UNIT_COL: "adm1_name",
        INDICATOR_COL: "indicator",
        VALUE_COL: "value"
    })

    print("\n--- df_conflict_standard sample ---")
    print(df_conflict_standard.head(5))
    print("\nColumns:", df_conflict_standard.columns)
    print("Shape:", df_conflict_standard.shape)
    print("\nIndicators:", df_conflict_standard["indicator"].unique())
    df = pd.concat(
        [
            df_rainfall_standard,
            df_price_standard,
            df_conflict_standard,
            df_flood_standard
        ],
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

            baseline_list = INDICATOR_ALLOWED_BASELINES.get(
                ind,
                [DEFAULT_BASELINE]
            )

            for baseline_method in baseline_list:

                print(f"\nProcessing Indicator: {ind} | Baseline: {baseline_method}")

                if ind in PRICE_INDICATORS and baseline_method == "none":
                    continue

                df_indicator = df_country[df_country["indicator"] == ind].copy()

                method_type = INDICATOR_METHOD.get(ind, "percentile")

                # -----------------------------------------
                # 🔥 TRUE SPI (Gamma-based)
                # -----------------------------------------
                if method_type == "spi_true" and ind in SPI_TRUE_INDICATORS:

                    try:
                        df_spi_source = df_rainfall[
                            (df_rainfall["country"] == country) &
                            (df_rainfall[INDICATOR_COL] == ind)
                            ].copy()

                        df_spi = compute_true_spi(df_spi_source)

                        df_spi["indicator"] = ind
                        df_spi["baseline_method"] = "none"

                        df_indicator = df_spi.copy()

                        print(f"✅ TRUE SPI applied for {ind}")

                    except Exception as e:
                        print(f"SPI-TRUE failed for {ind}: {e}")
                        continue

                # -----------------------------------------
                # 🔥 TRUE Z-SCORE (Seasonal standardized)
                # -----------------------------------------
                elif ind in ZSCORE_TRUE_INDICATORS:

                    try:
                        # -----------------------------------------
                        # 🔥 SELECT CORRECT DATA SOURCE
                        # -----------------------------------------
                        if ind in PRICE_INDICATORS:
                            df_z_source = df_indicator.copy()
                        else:
                            df_z_source = df_rainfall[
                                (df_rainfall["country"] == country) &
                                (df_rainfall[INDICATOR_COL] == ind)
                                ].copy()

                        # -----------------------------------------
                        # 🔥 CRITICAL FIX: FILTER BASELINE FIRST
                        # -----------------------------------------
                        if ind in PRICE_INDICATORS and "baseline_method" in df_z_source.columns:
                            df_z_source = df_z_source[
                                df_z_source["baseline_method"] == baseline_method
                                ]

                        # ✅ ADD THIS HERE
                        if "date" not in df_z_source.columns:
                            df_z_source["date"] = df_z_source["year_month"].dt.to_timestamp()

                        # -----------------------------------------
                        # Apply zscore_true
                        # -----------------------------------------
                        df_z = compute_true_zscore(df_z_source)

                        df_z["indicator"] = ind

                        # -----------------------------------------
                        # ONLY set baseline for NON-PRICE
                        # -----------------------------------------
                        if ind not in PRICE_INDICATORS:
                            df_z["baseline_method"] = "none"

                        # -----------------------------------------
                        # 🔥 SAFE Z-SCORE MERGE (FINAL FIX)
                        # -----------------------------------------
                        df_z_small = df_z[
                            ["adm1_name", "year_month", "baseline_method", "value_zscore"]
                        ].drop_duplicates()

                        df_indicator = df_indicator.merge(
                            df_z_small,
                            on=["adm1_name", "year_month", "baseline_method"],
                            how="left"
                        )

                        print(f"✅ TRUE Z-SCORE applied for {ind}")

                    except Exception as e:
                        print(f"Z-SCORE-TRUE failed for {ind}: {e}")
                        continue

                # -----------------------------------------
                # 🔥 Ensure date exists (AFTER transformations)
                # -----------------------------------------
                if "date" not in df_indicator.columns and DATE_COL in df_country.columns:
                    df_indicator = df_indicator.merge(
                        df_country[[UNIT_COL, "year_month", DATE_COL]],
                        on=[UNIT_COL, "year_month"],
                        how="left"
                    )

                # -----------------------------------------
                # 🔥 FIX: Handle RAW indicators correctly
                # -----------------------------------------
                if "baseline_method" in df_indicator.columns:

                    # 🔥 DO NOT FILTER CONFLICT (CRITICAL FIX)
                    if ind in ["conflict_events", "conflict_fatalities"]:
                        pass

                    elif method_type == "spi_true":
                        df_indicator = df_indicator[
                            df_indicator["baseline_method"] == "none"
                            ]

                    else:
                        df_indicator = df_indicator[
                            df_indicator["baseline_method"] == baseline_method
                            ]

                if df_indicator.empty:
                    print(f"Skipping {ind} | {baseline_method} (no data)")
                    continue

                # ---------------------------------------------------
                # 🔥 SPECIAL HANDLING FOR CONFLICT (event indicators)
                # ---------------------------------------------------
                if method_type in ["event", "event_combined"]:
                    unit_month = df_indicator.copy()

                    # ✅ Ensure structure consistency
                    if "value" not in unit_month.columns:
                        unit_month["value"] = unit_month.get(VALUE_COL, np.nan)

                    unit_month["indicator"] = ind
                    unit_month["baseline_method"] = baseline_method

                    # 🔥 ADD GROUP TO UNIT-MONTH (CRITICAL FIX)
                    unit_month["group"] = unit_month["adm1_name"].map(ADM1_GROUP_MAPPING)
                    unit_month["group"] = unit_month["group"].fillna("Unknown")

                else:
                    # -----------------------------------------
                    # 🔥 SELECT VALUE COLUMN
                    # -----------------------------------------
                    # -----------------------------------------
                    # 🔥 ALWAYS USE ANOMALY FOR AGGREGATION
                    # -----------------------------------------
                    value_col_unit = VALUE_COL

                    # -----------------------------------------
                    # 🔥 AGGREGATE
                    # -----------------------------------------
                    unit_month = compute_unit_month_values(
                        df=df_indicator,
                        unit_col=UNIT_COL,
                        indicator_col=INDICATOR_COL,
                        value_col=value_col_unit,
                        indicator_value=ind,
                        aggregation="mean"
                    )

                    # ---------------------------------------------------
                    # 🔥 MERGE HYBRID SIGNALS INTO UNIT-MONTH (CRITICAL)
                    # ---------------------------------------------------
                    signal_cols = [
                        "adm1_name",
                        "year_month",
                        "baseline_method",
                        "yoy_signal",
                        "yoy_ratio",
                        "anomaly_signal",
                        "anomaly_ratio"
                    ]

                    available_cols = [col for col in signal_cols if col in df_indicator.columns]

                    if len(available_cols) > 3:  # ensure signals exist

                        df_signals = df_indicator[available_cols].drop_duplicates()

                        unit_month = unit_month.merge(
                            df_signals,
                            on=["adm1_name", "year_month", "baseline_method"],
                            how="left"
                        )

                    # -----------------------------------------
                    # 🔥 MERGE Z-SCORE AT UNIT-MONTH LEVEL
                    # -----------------------------------------
                    if "value_zscore" in df_indicator.columns:
                        df_z_unit = (
                            df_indicator[
                                ["adm1_name", "year_month", "baseline_method", "value_zscore"]
                            ]
                            .dropna(subset=["value_zscore"])
                            .drop_duplicates()
                        )

                        unit_month = unit_month.merge(
                            df_z_unit,
                            on=["adm1_name", "year_month", "baseline_method"],
                            how="left"
                        )

                    unit_month["indicator"] = ind
                    unit_month["baseline_method"] = baseline_method

                all_unit_month_values.append(unit_month)

                # -----------------------------------------
                # 🔥 SELECT VALUE COLUMN (SPATIAL - FINAL FIX)
                # -----------------------------------------
                if method_type == "zscore_true":
                    value_col_spatial = "value_zscore"
                else:
                    value_col_spatial = VALUE_COL

                # fallback safety
                if value_col_spatial not in df_indicator.columns:
                    value_col_spatial = VALUE_COL

                spatial = compute_spatial_percentiles(
                    df_indicator,
                    UNIT_COL,
                    DATE_COL,
                    INDICATOR_COL,
                    value_col_spatial,
                    ind
                )

                spatial["retention_filter"] = "none"
                spatial["season_scope"] = "All Months"
                all_spatial_percentiles.append(spatial)

                # -----------------------------------------
                # 🔥 TRUE SPI THRESHOLDS (FIXED)
                # -----------------------------------------
                if method_type == "spi_true":
                    thresholds = SPI_TRUE_THRESHOLDS.get(
                        ind,
                        SPI_TRUE_THRESHOLDS["default"]
                    )

                    df_threshold = pd.DataFrame([{
                        "indicator": ind,
                        "alert_percentile": thresholds["alert"],
                        "alarm_percentile": thresholds["alarm"],
                        "alert_tukey": None,
                        "alarm_tukey": None,
                        "retention_filter": "none",
                        "season_scope": "All Months",
                        "baseline_method": baseline_method,
                        "country": country
                    }])

                    all_thresholds.append(df_threshold)

                    continue

                # ---------------------------------------------------
                # SKIP THRESHOLDS FOR EVENT INDICATORS
                # ---------------------------------------------------
                if method_type not in ["event", "event_combined"]:

                    monthly_table = compute_monthly_quartiles_with_iqr(spatial, DATE_COL)
                    all_monthly_tables.append(monthly_table)

                    # -----------------------------------------
                    # Percentile
                    # -----------------------------------------
                    percentile_thresholds = compute_composite_thresholds(spatial, ind)

                    percentile_thresholds = percentile_thresholds.rename(columns={
                        "alert_threshold": "alert_percentile",
                        "alarm_threshold": "alarm_percentile"
                    })

                    # -----------------------------------------
                    # Tukey
                    # -----------------------------------------
                    tukey_thresholds = compute_tukey_thresholds(spatial, ind)

                    # -----------------------------------------
                    # 🔥 NEW: Z-score
                    # -----------------------------------------
                    from src.zscore_thresholds import compute_zscore_thresholds

                    zscore_thresholds = compute_zscore_thresholds(
                        df_indicator,
                        ind,
                        value_col=value_col_spatial
                    )

                    # -----------------------------------------
                    # Merge ALL
                    # -----------------------------------------
                    merged_thresholds = percentile_thresholds.merge(
                        tukey_thresholds,
                        on="indicator",
                        how="left"
                    )

                    if not zscore_thresholds.empty:
                        merged_thresholds = merged_thresholds.merge(
                            zscore_thresholds[["indicator", "alert_zscore", "alarm_zscore"]],
                            on="indicator",
                            how="left"
                        )
                    else:
                        merged_thresholds["alert_zscore"] = None
                        merged_thresholds["alarm_zscore"] = None

                    merged_thresholds["retention_filter"] = "none"
                    merged_thresholds["season_scope"] = "All Months"
                    merged_thresholds["baseline_method"] = baseline_method
                    merged_thresholds["country"] = country

                    all_thresholds.append(merged_thresholds)

                else:

                    print(f"Adding event-based thresholds for {ind}")

                    # ---------------------------------------------------

                    # conflict_events (uses EVENT_THRESHOLDS)

                    # ---------------------------------------------------

                    if ind in EVENT_THRESHOLDS:

                        thresholds = EVENT_THRESHOLDS[ind]

                        df_threshold = pd.DataFrame([{

                            "indicator": ind,

                            "alert_percentile": thresholds.get("alert"),

                            "alarm_percentile": thresholds.get("alarm"),

                            "alert_tukey": None,

                            "alarm_tukey": None,

                            "retention_filter": "none",

                            "season_scope": "All Months",

                            "baseline_method": baseline_method,

                            "country": country

                        }])

                        all_thresholds.append(df_threshold)

                    # ---------------------------------------------------

                    # conflict_fatalities (manual thresholds or config)

                    # ---------------------------------------------------

                    elif ind == "conflict_fatalities":

                        df_threshold = pd.DataFrame([{

                            "indicator": ind,

                            "alert_percentile": 1,

                            "alarm_percentile": 5,

                            "alert_tukey": None,

                            "alarm_tukey": None,

                            "retention_filter": "none",

                            "season_scope": "All Months",

                            "baseline_method": baseline_method,

                            "country": country

                        }])

                        all_thresholds.append(df_threshold)

                spatial_robust = compute_spatial_percentiles(
                    df_indicator,
                    UNIT_COL,
                    DATE_COL,
                    INDICATOR_COL,
                    value_col_spatial,
                    ind,
                    min_retention_pct=ROBUST_MIN_RETENTION
                )

                spatial_robust["retention_filter"] = f">={ROBUST_MIN_RETENTION}%"
                spatial_robust["season_scope"] = "All Months"

                all_spatial_percentiles.append(spatial_robust)

                if not spatial_robust.empty and method_type not in ["event", "event_combined"]:

                    pct_robust = compute_composite_thresholds(spatial_robust, ind)

                    pct_robust = pct_robust.rename(columns={
                        "alert_threshold": "alert_percentile",
                        "alarm_threshold": "alarm_percentile"
                    })

                    tukey_robust = compute_tukey_thresholds(spatial_robust, ind)

                    from src.zscore_thresholds import compute_zscore_thresholds

                    zscore_thresholds = compute_zscore_thresholds(
                        df_indicator,
                        ind,
                        value_col=value_col_spatial
                    )

                    merged_robust = pct_robust.merge(
                        tukey_robust,
                        on="indicator",
                        how="left"
                    )

                    if not zscore_thresholds.empty:
                        merged_robust = merged_robust.merge(
                            zscore_thresholds[["indicator", "alert_zscore", "alarm_zscore"]],
                            on="indicator",
                            how="left"
                        )
                    else:
                        merged_robust["alert_zscore"] = None
                        merged_robust["alarm_zscore"] = None

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
                        value_col_spatial,
                        ind,
                        season_months=season_months
                    )

                    if not spatial_season.empty and method_type not in ["event", "event_combined"]:

                        pct_season = compute_composite_thresholds(spatial_season, ind)

                        pct_season = pct_season.rename(columns={
                            "alert_threshold": "alert_percentile",
                            "alarm_threshold": "alarm_percentile"
                        })

                        tukey_season = compute_tukey_thresholds(spatial_season, ind)

                        from src.zscore_thresholds import compute_zscore_thresholds

                        zscore_thresholds = compute_zscore_thresholds(
                            df_indicator,
                            ind,
                            value_col=value_col_spatial
                        )

                        merged_season = pct_season.merge(
                            tukey_season,
                            on="indicator",
                            how="left"
                        )

                        if not zscore_thresholds.empty:
                            merged_season = merged_season.merge(
                                zscore_thresholds[["indicator", "alert_zscore", "alarm_zscore"]],
                                on="indicator",
                                how="left"
                            )
                        else:
                            merged_season["alert_zscore"] = None
                            merged_season["alarm_zscore"] = None

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

    # ---------------------------------------------------
    # 🔍 DEBUG: CHECK UNIT MONTH CONTENT (CONFLICT)
    # ---------------------------------------------------
    print("\n===== DEBUG: UNIT MONTH CHECK =====")

    df_debug = final_unit_month.copy()

    print("\n--- Conflict sample ---")
    print(
        df_debug[
            df_debug["indicator"].isin(["conflict_events", "conflict_fatalities"])
        ].head(10)
    )

    print("\n--- Available columns ---")
    print(df_debug.columns.tolist())

    # ---------------------------------------------------
    # IPC MATRIX (NEW)
    # ---------------------------------------------------
    ipc_matrix = prepare_ipc_matrix(df_ipc)

    final_unit_month["group"] = final_unit_month["adm1_name"].map(ADM1_GROUP_MAPPING)
    final_unit_month["group"] = final_unit_month["group"].fillna("Unknown")

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

        method_type = INDICATOR_METHOD.get(ind, "percentile")

        # ---------------------------------------------------
        # EVENT INDICATORS (conflict)
        # ---------------------------------------------------
        if method_type == "event_combined" and ind == "conflict_events":
            print(f"Computing event-based triggers for {ind}")

            # ---------------------------------------------------
            # 🔥 GET BOTH EVENTS + FATALITIES FROM UNIT-MONTH
            # ---------------------------------------------------
            df_events = final_unit_month[
                final_unit_month["indicator"] == "conflict_events"
                ].copy()

            df_fatal = final_unit_month[
                final_unit_month["indicator"] == "conflict_fatalities"
                ].copy()

            df_combined = df_events.merge(
                df_fatal,
                on=["year_month", "adm1_name"],
                suffixes=("_events", "_fatalities")
            )

            # ---------------------------------------------------
            # 🔥 LOAD RULES FROM CONFIG
            # ---------------------------------------------------
            rules = CONFLICT_COMBINED_RULES.get(ind)

            if rules is None:
                raise ValueError(f"No combined rules for {ind}")

            event_alert = rules["event_alert_threshold"]
            event_alarm = rules["event_alarm_threshold"]
            fatal_alarm = rules["fatality_alarm_threshold"]

            # ---------------------------------------------------
            # 🔥 APPLY SAME LOGIC AS CLASSIFICATION
            # ---------------------------------------------------
            df_combined["alert"] = (
                    (df_combined["value_events"] >= event_alert) &
                    (df_combined["value_fatalities"] < fatal_alarm)
            ).astype(int)

            df_combined["alarm"] = (
                    (df_combined["value_events"] >= event_alarm) |
                    (df_combined["value_fatalities"] >= fatal_alarm)
            ).astype(int)

            # ---------------------------------------------------
            # 🔥 AGGREGATE
            # ---------------------------------------------------
            trigger_counts = (
                df_combined
                .groupby("year_month")
                .agg(
                    alert_count=("alert", "sum"),
                    alarm_count=("alarm", "sum")
                )
                .reset_index()
            )

            trigger_counts["indicator"] = ind

            all_trigger_counts.append(trigger_counts)

            continue

        # ---------------------------------------------------
        # NORMAL INDICATORS
        # ---------------------------------------------------
        if final_thresholds.empty:
            print("No thresholds available. Skipping trigger counts.")
            break

        if ind not in final_thresholds["indicator"].values:
            print(f"Skipping trigger counts for {ind} (no thresholds)")
            continue

        method_type = INDICATOR_METHOD.get(ind, "percentile")

        # -----------------------------------------
        # 🔥 SAFE VALUE COLUMN (TRIGGER - FINAL)
        # -----------------------------------------
        if (
                ind in ZSCORE_TRUE_INDICATORS
                and "value_zscore" in final_unit_month.columns
                and final_unit_month["value_zscore"].notna().any()
        ):
            value_col_trigger = "value_zscore"
        else:
            value_col_trigger = VALUE_COL

        # -----------------------------------------
        # 🔥 ALWAYS USE UNIT-MONTH DATA (CRITICAL FIX)
        # -----------------------------------------
        df_trigger_source = final_unit_month

        trigger_counts = compute_monthly_trigger_counts(
            df_trigger_source,
            UNIT_COL,
            INDICATOR_COL,
            value_col_trigger,
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
    final_unit_month.to_excel("outputs/unit_month_values.xlsx", index=False)
    final_spatial_percentiles.to_csv("outputs/spatial_percentiles_with_proportions.csv", index=False)

    print("\nTables saved successfully.")
    import streamlit as st

    # ---------------------------------------------------
    for ind in INDICATORS:
        print(f"Generating charts for: {ind}")

        fig = plot_monthly_trigger_counts(
            final_trigger_counts,
            indicator_value=ind,
            method="percentile",
            use_percent=False
        )

        st.subheader(f"{ind} – Percentile Triggers")
        st.plotly_chart(fig, width="stretch")

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

        method_type = INDICATOR_METHOD.get(ind, "percentile")

        # ---------------------------------------------------
        # EVENT INDICATORS (conflict)
        # ---------------------------------------------------
        if method_type not in ["event", "event_combined"]:

            row = final_thresholds[
                (final_thresholds["indicator"] == ind) &
                (final_thresholds["retention_filter"] == "none") &
                (final_thresholds["season_scope"] == "All Months") &
                (
                        (final_thresholds["baseline_method"] == DEFAULT_BASELINE)
                        | (final_thresholds["baseline_method"] == "none")
                )
                ]

            if row.empty:
                print(f"No thresholds found for {ind}")
                continue

            # 🔥 Ensure correct baseline selection (CRITICAL FIX)
            row = row.sort_values(by=["baseline_method"])

            row = row[row["baseline_method"] == DEFAULT_BASELINE]

            if row.empty:
                print(f"No valid thresholds for {ind}")
                continue

            row = row.iloc[0]

            alarm_percentile = row["alarm_percentile"]
            alert_percentile = row["alert_percentile"]
            alarm_tukey = row["alarm_tukey"]
            alert_tukey = row["alert_tukey"]

        else:
            # 🔥 thresholds are NOT used for event_combined
            alarm_percentile = None
            alert_percentile = None
            alarm_tukey = None
            alert_tukey = None

        df_matrix = final_unit_month.copy()

        # Use default baseline for pipeline outputs
        if "baseline_method" in df_matrix.columns:
            df_matrix = df_matrix[df_matrix["baseline_method"] == DEFAULT_BASELINE].copy()

        if (
                ind in ZSCORE_TRUE_INDICATORS
                and "value_zscore" in df_matrix.columns
                and df_matrix["value_zscore"].notna().any()
        ):
            value_col_classification = "value_zscore"
        else:
            value_col_classification = VALUE_COL

        # ---------------------------------------------------
        # 🔥 CUSTOM CONFLICT CLASSIFICATION (NEW)
        # ---------------------------------------------------
        if ind in ["conflict_events", "conflict_fatalities"]:
            print(f"Applying hybrid classification for: {ind}")

            df_matrix_conflict = final_unit_month[
                final_unit_month["indicator"] == ind
                ].copy()

            # 🔥 Apply selected method (categorical / hybrid / percentile)
            selected_method = INDICATOR_METHOD.get(ind, "categorical")

            df_matrix_conflict["classification"] = df_matrix_conflict.apply(
                lambda row: classify_conflict_row(
                    row,
                    indicator=ind,
                    method=selected_method
                ),
                axis=1
            )

            df_matrix_conflict["classification_label"] = (
                df_matrix_conflict["classification"]
                .map(CLASSIFICATION_LABELS)
            )

            # Pivot to matrix format
            matrix_conflict = df_matrix_conflict.pivot_table(
                index="adm1_name",
                columns="year_month",
                values="classification_label",
                aggfunc="first"
            )

            safe_name = ind.replace(" ", "_")

            export_colored_classification_matrix(
                matrix_conflict,
                f"outputs/{safe_name}_{selected_method}_classification_matrix.xlsx"
            )

            continue  # 🔥 VERY IMPORTANT (skip normal logic)

        matrix_percentile = compute_unit_month_classification_matrix(
            df=df_matrix,
            unit_col=UNIT_COL,
            indicator_col=INDICATOR_COL,
            value_col=value_col_classification,
            indicator_value=ind,
            alarm_threshold=alarm_percentile,
            alert_threshold=alert_percentile
        )

        matrix_tukey = compute_unit_month_classification_matrix(
            df=df_matrix,
            unit_col=UNIT_COL,
            indicator_col=INDICATOR_COL,
            value_col=value_col_classification,
            indicator_value=ind,
            alarm_threshold=alarm_tukey,
            alert_threshold=alert_tukey
        )

        safe_name = ind.replace(" ", "_").replace("%", "")

        if method_type in ["event", "event_combined"]:

            # Only export once (same thresholds anyway)
            export_colored_classification_matrix(
                matrix_percentile,
                f"outputs/{safe_name}_classification_matrix.xlsx"
            )

        else:

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

    # -----------------------------------------
    # RETURN OUTPUTS (🔥 ADD THIS)
    # -----------------------------------------
    ipc_matrix.to_csv("outputs/ipc_matrix.csv")

    return {
        "thresholds": final_thresholds,
        "unit_month": final_unit_month,
        "trigger_counts": final_trigger_counts,
        "ipc_matrix": ipc_matrix
    }

if __name__ == "__main__":
    main()
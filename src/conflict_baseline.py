import pandas as pd
from src.config import UNIT_COL, INDICATOR_COL

from src.conflict_rolling_anomaly import compute_conflict_rolling_anomaly
from src.conflict_yoy_abs import compute_conflict_yoy_abs


def compute_conflict_baseline(method, monthly_conflict):

    df_list = []

    # 🔥 DYNAMIC INDICATORS (CRITICAL FIX)
    indicators = monthly_conflict["indicator"].dropna().unique()

    print("\n--- DEBUG: AVAILABLE INDICATORS ---")
    print(indicators)

    for indicator in indicators:

        df_ind = monthly_conflict[
            monthly_conflict["indicator"] == indicator
        ].copy()

        # 🔥 DEBUG INSIDE LOOP
        print(f"\nProcessing indicator: {indicator}")
        print(f"Shape: {df_ind.shape}")

        # 🔥 SKIP EMPTY (CRITICAL)
        if df_ind.empty:
            print(f"⚠️ Skipping {indicator} (no data)")
            continue

        df_yoy = compute_conflict_yoy_abs(df_ind)
        df_roll = compute_conflict_rolling_anomaly(df_ind)

        # 🔥 HANDLE EMPTY ROLLING OUTPUT
        if df_roll.empty:
            print(f"⚠️ Rolling output empty for {indicator}")
            continue

        # 🔥 SAFE MERGE
        df = df_yoy.merge(
            df_roll[
                [
                    UNIT_COL,
                    INDICATOR_COL,
                    "year_month",
                    "rolling_mean_6",
                    "anomaly_signal",
                    "anomaly_ratio"
                ]
            ],
            on=[UNIT_COL, INDICATOR_COL, "year_month"],
            how="left"
        )

        # Ensure signal exists
        df["yoy_signal"] = df["conflict_yoy_abs"]

        df["indicator"] = indicator
        df["baseline_method"] = method

        df_list.append(df)

    # 🔥 FINAL PROTECTION
    if not df_list:
        print("❌ No conflict data processed — returning empty dataframe")
        return pd.DataFrame()

    return pd.concat(df_list, ignore_index=True)
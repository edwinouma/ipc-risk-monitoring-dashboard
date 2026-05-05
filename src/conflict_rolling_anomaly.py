import pandas as pd
from src.config import UNIT_COL, INDICATOR_COL, VALUE_COL


def compute_conflict_rolling_anomaly(monthly_df_conflict):

    df = monthly_df_conflict.copy()

    # 🔥 ensure correct type
    df["year_month"] = df["year_month"].astype("period[M]")

    df = df.sort_values([UNIT_COL, INDICATOR_COL, "year_month"])

    result_list = []

    for (unit, indicator), group in df.groupby([UNIT_COL, INDICATOR_COL]):

        g = group.copy()

        # 🔥 STEP 1: full monthly timeline (temporary)
        full_index = pd.period_range(
            g["year_month"].min(),
            g["year_month"].max(),
            freq="M"
        )

        g_full = (
            g.set_index("year_month")
             .reindex(full_index)
        )

        # 🔥 ensure value column exists
        g_full[VALUE_COL] = g_full[VALUE_COL]

        # 🔥 STEP 2: rolling on TRUE timeline
        g_full["rolling_mean_6"] = (
            g_full[VALUE_COL]
            .rolling(6, min_periods=3)
            .mean()
        )

        # 🔥 STEP 3: anomaly
        g_full["conflict_anomaly"] = (
            g_full[VALUE_COL] - g_full["rolling_mean_6"]
        )

        g_full["anomaly_ratio"] = (
            g_full[VALUE_COL] / g_full["rolling_mean_6"]
        )

        g_full.loc[
            (g_full["rolling_mean_6"].isna()) |
            (g_full["rolling_mean_6"] == 0),
            "anomaly_ratio"
        ] = None

        # 🔥 STEP 4: KEEP ONLY ORIGINAL MONTHS
        g_full = g_full.loc[g["year_month"]]

        # restore columns
        g_full = g_full.reset_index().rename(columns={"index": "year_month"})
        g_full[UNIT_COL] = unit
        g_full[INDICATOR_COL] = indicator

        result_list.append(g_full)

    df_out = pd.concat(result_list, ignore_index=True)

    # preserve signals
    df_out["value"] = df_out[VALUE_COL]
    df_out["anomaly_signal"] = df_out["conflict_anomaly"]
    df_out["baseline_method"] = "ROLLING_MEAN_6_ANOMALY"

    return df_out
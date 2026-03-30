from src.unit_month import compute_unit_month_values
import pandas as pd
from src.config import (
    INDICATOR_DIRECTION,
    CLIMATE_INDICATORS,
    PRICE_INDICATORS,
    SHOCK_INDICATORS,
    INDICATOR_METHOD
)
from src.utils import get_filtered_distribution

def compute_spatial_percentiles(
    df,
    unit_col,
    date_col,
    indicator_col,
    value_col,
    indicator_value,
    min_obs=5,
    min_retention_pct=None,
    season_months=None,
    debug=False
):
    """
    Compute spatial percentiles across units per month.

    Features
    --------
    • Seasonal filtering
    • Direction-aware filtering
    • Minimum observation rule
    • Monthly retention diagnostics
    • Overall retention diagnostics
    """

    # ---------------------------------------------------
    # 1. Compute unit-month values
    # ---------------------------------------------------
    df_unit_month = compute_unit_month_values(
        df,
        unit_col,
        indicator_col,
        value_col,
        indicator_value
    )

    # 🔥 DEBUG ONLY FOR ToT
    if indicator_value == "ToT":
        print("\n====== DEBUG ToT (UNIT-MONTH) ======")
        print(df_unit_month[value_col].describe())

        print("Negative count:", (df_unit_month[value_col] < 0).sum())
        print("Positive count:", (df_unit_month[value_col] > 0).sum())
        print("====================================\n")

    if df_unit_month.empty:
        return pd.DataFrame()

    if debug:
        print(f"Indicator: {indicator_value}")
        print("Rows:", len(df_unit_month))

    # ---------------------------------------------------
    # EVENT-BASED INDICATORS (conflict, flood occurrence)
    # ---------------------------------------------------
    method = INDICATOR_METHOD.get(indicator_value, "percentile")

    if method == "event":
        df_unit_month = df_unit_month.copy()
        df_unit_month[date_col] = df_unit_month["year_month"].dt.to_timestamp()
        df_unit_month["indicator"] = indicator_value
        return df_unit_month

    # ---------------------------------------------------
    # 2. Seasonal filtering
    # ---------------------------------------------------
    if season_months is not None:

        df_unit_month = df_unit_month.copy()
        df_unit_month["month"] = df_unit_month["year_month"].dt.month

        df_unit_month = df_unit_month[
            df_unit_month["month"].isin(season_months)
        ]

        if df_unit_month.empty:
            return pd.DataFrame()

    # ---------------------------------------------------
    # 3. Count total observations
    # ---------------------------------------------------
    total_counts = (
        df_unit_month
        .groupby("year_month")[value_col]
        .count()
        .reset_index(name="count_total")
    )

    # ---------------------------------------------------
    # 4. Directional filtering
    # ---------------------------------------------------

    direction = INDICATOR_DIRECTION.get(indicator_value, "lower")

    # ---------------------------------------------------
    # Climate indicators (anomaly-based)
    # ---------------------------------------------------
    if indicator_value in CLIMATE_INDICATORS:

        df_filtered = df_unit_month[
            df_unit_month[value_col] < 100
            ].copy()

    # ---------------------------------------------------
    # Market indicators (prices, livestock, ToT)
    # ---------------------------------------------------
    elif indicator_value in PRICE_INDICATORS:

        if direction == "upper":

            # food price inflation
            df_filtered = df_unit_month[
                df_unit_month[value_col] > 0
                ].copy()

        elif direction == "lower":

            # livestock / ToT decline
            df_filtered = df_unit_month[
                df_unit_month[value_col] < 0
                ].copy()

            if indicator_value == "ToT":
                print("---- AFTER FILTER ----")
                print(df_filtered[value_col].describe())
                print("Count after filter:", len(df_filtered))
                print("----------------------")

        else:
            df_filtered = df_unit_month.copy()

    # ---------------------------------------------------
    # Shock indicators (conflict, floods)
    # ---------------------------------------------------
    elif indicator_value in SHOCK_INDICATORS:

        # No directional filtering — keep all values
        df_filtered = df_unit_month.copy()

    # ---------------------------------------------------
    # Fallback (future indicators)
    # ---------------------------------------------------
    else:

        df_filtered = df_unit_month.copy()

    if df_filtered.empty:
        return pd.DataFrame()

    # ---------------------------------------------------
    # 5. Compute spatial percentiles
    # ---------------------------------------------------
    grouped = (
        df_filtered
        .groupby("year_month")[value_col]
        .agg(
            q25=lambda x: x.quantile(0.25),
            q50=lambda x: x.quantile(0.50),
            q75=lambda x: x.quantile(0.75),
            count="count"
        )
        .reset_index()
    )

    grouped["count_filtered"] = grouped["count"]

    # ---------------------------------------------------
    # 6. Merge total counts
    # ---------------------------------------------------
    grouped = grouped.merge(total_counts, on="year_month", how="left")

    # ---------------------------------------------------
    # 7. Monthly retention
    # ---------------------------------------------------
    grouped["percent_used_month"] = (
        grouped["count_filtered"] /
        grouped["count_total"] * 100
    ).round(1)

    grouped["n_used_display"] = (
        grouped["count_filtered"].astype(str)
        + " ("
        + grouped["percent_used_month"].astype(str)
        + "%)"
    )

    # ---------------------------------------------------
    # 8. Convert period to timestamp
    # ---------------------------------------------------
    grouped[date_col] = grouped["year_month"].dt.to_timestamp()

    # ---------------------------------------------------
    # 9. Minimum observation rule
    # ---------------------------------------------------
    grouped = grouped[grouped["count"] >= min_obs]

    # ---------------------------------------------------
    # 10. Retention rule
    # ---------------------------------------------------
    if min_retention_pct is not None:
        grouped = grouped[
            grouped["percent_used_month"] >= min_retention_pct
        ]

    # ---------------------------------------------------
    # 11. Overall retention stats
    # ---------------------------------------------------
    total_points_available = grouped["count_total"].sum()
    total_points_used = grouped["count_filtered"].sum()

    overall_percent = (
        round(total_points_used / total_points_available * 100, 1)
        if total_points_available > 0 else 0
    )

    grouped["overall_count_total"] = total_points_available
    grouped["overall_count_filtered"] = total_points_used
    grouped["overall_percent_used"] = overall_percent

    grouped["overall_display"] = (
        f"{total_points_used} ({overall_percent}%)"
    )

    # ---------------------------------------------------
    # 12. Indicator label
    # ---------------------------------------------------
    grouped["indicator"] = indicator_value

    return grouped
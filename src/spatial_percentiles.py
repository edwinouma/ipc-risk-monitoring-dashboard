from src.unit_month import compute_unit_month_values
import pandas as pd
from src.config import INDICATOR_DIRECTION


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

    if df_unit_month.empty:
        return pd.DataFrame()

    if debug:
        print(f"Indicator: {indicator_value}")
        print("Rows:", len(df_unit_month))

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

    if direction == "lower":

        # drought-style indicators
        df_filtered = df_unit_month[
            df_unit_month[value_col] < 100
        ].copy()

    elif direction == "upper":

        # inflation-style indicators
        df_filtered = df_unit_month[
            df_unit_month[value_col] > 0
        ].copy()

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
    overall_total = len(df_unit_month)
    overall_filtered = len(df_filtered)

    overall_percent = (
        round(overall_filtered / overall_total * 100, 1)
        if overall_total > 0 else 0
    )

    grouped["overall_count_total"] = overall_total
    grouped["overall_count_filtered"] = overall_filtered
    grouped["overall_percent_used"] = overall_percent

    grouped["overall_display"] = (
        f"{overall_filtered} ({overall_percent}%)"
    )

    # ---------------------------------------------------
    # 12. Indicator label
    # ---------------------------------------------------
    grouped["indicator"] = indicator_value

    return grouped
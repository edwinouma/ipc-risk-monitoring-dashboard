import pandas as pd


def compute_unit_month_values(
    df,
    unit_col,
    indicator_col,
    value_col,
    indicator_value,
    aggregation="mean"
):
    """
    Create one aggregated value per unit per month (year_month).

    IMPORTANT:
    This function does NOT filter drought values (<100).
    All months must be retained for classification and dashboard display.
    """

    # ---------------------------------------------------
    # 1. Validate required columns
    # ---------------------------------------------------
    required_cols = ["country", unit_col, indicator_col, value_col, "year_month"]

    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Column '{col}' missing from dataset.")

    # ---------------------------------------------------
    # 2. Filter indicator
    # ---------------------------------------------------
    df_indicator = df[df[indicator_col] == indicator_value].copy()

    if df_indicator.empty:
        return pd.DataFrame()

    # ---------------------------------------------------
    # 3. Aggregation method
    # ---------------------------------------------------
    if aggregation not in ["mean", "median"]:
        raise ValueError("aggregation must be 'mean' or 'median'")

    # ---------------------------------------------------
    # 4. Define grouping columns
    # ---------------------------------------------------
    group_cols = ["country", "year_month", unit_col]

    if "baseline_method" in df_indicator.columns:
        group_cols.append("baseline_method")

    # ---------------------------------------------------
    # 5. Aggregate
    # ---------------------------------------------------
    df_unit_month = (
        df_indicator
        .groupby(group_cols)[value_col]
        .agg(aggregation)
        .reset_index()
    )

    # ---------------------------------------------------
    # 6. Attach indicator label
    # ---------------------------------------------------
    df_unit_month[indicator_col] = indicator_value

    # ---------------------------------------------------
    # 7. Sort
    # ---------------------------------------------------
    df_unit_month = df_unit_month.sort_values(
        ["country", "year_month", unit_col]
    )

    return df_unit_month
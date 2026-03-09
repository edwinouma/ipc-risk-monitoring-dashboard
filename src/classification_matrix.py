import pandas as pd
from src.unit_month import compute_unit_month_values
from src.classification_utils import classify_series

def compute_unit_month_classification_matrix(
    df,
    unit_col,
    indicator_col,
    value_col,
    indicator_value,
    alarm_threshold,              # ← DIRECT THRESHOLDS
    alert_threshold,              # ← DIRECT THRESHOLDS
    selected_units=None,
    start_date=None,
    end_date=None,
    add_proportions=True
):
    """
    Create wide classification matrix:
    Rows    = Units
    Columns = Year-Month
    Values  = Alarm / Alert / Minimal

    Fully consistent with:
        - Selected provinces
        - Dynamic thresholds
        - Time window
    """

    # ---------------------------------------------------
    # 1. Compute unit-month values
    # ---------------------------------------------------
    df_unit_month = compute_unit_month_values(
        df=df,
        unit_col=unit_col,
        indicator_col=indicator_col,
        value_col=value_col,
        indicator_value=indicator_value,
        aggregation="mean"
    )

    if df_unit_month.empty:
        return pd.DataFrame()

    # ---------------------------------------------------
    # 2. Filter selected units
    # ---------------------------------------------------
    if selected_units is not None and len(selected_units) > 0:
        df_unit_month = df_unit_month[
            df_unit_month[unit_col].isin(selected_units)
        ]

    if df_unit_month.empty:
        return pd.DataFrame()

    # ---------------------------------------------------
    # 3. Convert Period to Timestamp
    # ---------------------------------------------------
    df_unit_month["year_month_date"] = df_unit_month["year_month"].dt.to_timestamp()

    # ---------------------------------------------------
    # 4. Filter by date window
    # ---------------------------------------------------
    if start_date is not None and end_date is not None:
        df_unit_month = df_unit_month[
            (df_unit_month["year_month_date"] >= pd.to_datetime(start_date)) &
            (df_unit_month["year_month_date"] <= pd.to_datetime(end_date))
        ]

    if df_unit_month.empty:
        return pd.DataFrame()


    # ---------------------------------------------------
    # 5. Classification using shared engine
    # ---------------------------------------------------

    df_unit_month["classification"] = classify_series(
        df_unit_month[value_col],
        indicator_value,
        alarm_threshold,
        alert_threshold
    )

    # ---------------------------------------------------
    # 6. Convert to month string
    # ---------------------------------------------------
    df_unit_month["year_month_str"] = df_unit_month["year_month_date"].dt.strftime("%Y %b")

    # ---------------------------------------------------
    # 7. Pivot
    # ---------------------------------------------------
    matrix = df_unit_month.pivot(
        index=unit_col,
        columns="year_month_str",
        values="classification"
    )

    # ---------------------------------------------------
    # 8. Chronological ordering
    # ---------------------------------------------------
    month_order = (
        df_unit_month[["year_month_str", "year_month_date"]]
        .drop_duplicates()
        .sort_values("year_month_date")["year_month_str"]
        .tolist()
    )

    matrix = matrix.reindex(columns=month_order)

    # ---------------------------------------------------
    # 9. Replace NaNs
    # ---------------------------------------------------
    matrix = matrix.fillna("Minimal")

    # ---------------------------------------------------
    # 10. Structural proportions (based ONLY on visible months)
    # ---------------------------------------------------
    if add_proportions and len(month_order) > 0:

        total_months = len(month_order)

        alarm_pct = (matrix == "Alarm").sum(axis=1) / total_months * 100
        alert_pct = (matrix == "Alert").sum(axis=1) / total_months * 100
        sum_pct = alarm_pct + alert_pct

        matrix["% Alarm"] = alarm_pct.round(0).astype(int).astype(str) + "%"
        matrix["% Alert"] = alert_pct.round(0).astype(int).astype(str) + "%"
        matrix["Sum"] = sum_pct.round(0).astype(int).astype(str) + "%"

    # ---------------------------------------------------
    # 11. Sort alphabetically
    # ---------------------------------------------------
    matrix = matrix.sort_index()

    return matrix
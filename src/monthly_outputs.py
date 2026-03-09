import pandas as pd


def compute_monthly_quartiles_with_iqr(spatial_df, date_col):
    """
    Produce quartiles + IQR per month-year
    using existing year_month backbone.
    Fully robust to empty inputs.
    """

    # ---------------------------------------------------
    # If spatial_df is empty OR missing required column
    # ---------------------------------------------------
    if spatial_df.empty or "year_month" not in spatial_df.columns:
        return pd.DataFrame(
            columns=[
                "indicator",
                "year",
                "month",
                "month_name",
                "q25",
                "q50",
                "q75",
                "iqr",
                "count",
            ]
        )

    df = spatial_df.copy()

    # ---------------------------------------------------
    # Derive year and month directly from year_month
    # ---------------------------------------------------
    df["year"] = df["year_month"].dt.year
    df["month"] = df["year_month"].dt.month
    df["month_name"] = df["year_month"].dt.strftime("%b")

    # ---------------------------------------------------
    # Compute IQR per month
    # ---------------------------------------------------
    df["iqr"] = df["q75"] - df["q25"]

    # ---------------------------------------------------
    # Select clean output columns
    # ---------------------------------------------------
    df = df[
        [
            "indicator",
            "year",
            "month",
            "month_name",
            "q25",
            "q50",
            "q75",
            "iqr",
            "count",
        ]
    ]

    return df
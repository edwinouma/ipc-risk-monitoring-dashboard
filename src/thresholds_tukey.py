import pandas as pd
from src.config import INDICATOR_DIRECTION


def compute_tukey_thresholds(spatial_df, indicator_value):
    """
    Compute Tukey-based thresholds using
    median-of-monthly-IQR approach.
    """

    # If empty → return row with NaNs but keep structure
    if spatial_df.empty:
        return pd.DataFrame({
            "indicator": [indicator_value],
            "q1_median": [None],
            "q3_median": [None],
            "median_iqr": [None],
            "alert_tukey": [None],
            "alarm_tukey": [None]
        })

    spatial_df = spatial_df.copy()

    spatial_df["iqr_month"] = spatial_df["q75"] - spatial_df["q25"]

    q1_median = spatial_df["q25"].median()
    q3_median = spatial_df["q75"].median()
    median_iqr = spatial_df["iqr_month"].median()

    direction = INDICATOR_DIRECTION.get(indicator_value, "lower")

    if direction == "lower":
        alert_tukey = q1_median - 1.0 * median_iqr
        alarm_tukey = q1_median - 1.5 * median_iqr
    else:
        alert_tukey = q3_median + 1.0 * median_iqr
        alarm_tukey = q3_median + 1.5 * median_iqr

    return pd.DataFrame({
        "indicator": [indicator_value],
        "q1_median": [q1_median],
        "q3_median": [q3_median],
        "median_iqr": [median_iqr],
        "alert_tukey": [alert_tukey],
        "alarm_tukey": [alarm_tukey]
    })
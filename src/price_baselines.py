import pandas as pd

from src.ltm_anomaly import compute_ltm_anomaly
from src.yoy_anomaly import compute_yoy_anomaly
from src.five_year_anomaly import compute_five_year_anomaly


def compute_price_baseline(method, monthly_prices, baseline=None):

    if method == "LTM":
        df = compute_ltm_anomaly(monthly_prices, baseline)

    elif method == "YOY":
        df = compute_yoy_anomaly(monthly_prices)

    elif method == "FIVE_YEAR":
        df = compute_five_year_anomaly(monthly_prices)

    else:
        raise ValueError(f"Unknown baseline method: {method}")

    df["baseline_method"] = method

    return df
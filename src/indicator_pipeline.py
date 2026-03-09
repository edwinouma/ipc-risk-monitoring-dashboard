from src.indicator_groups import is_climate_indicator, is_price_indicator
from src.indicator_metadata import get_indicator_seasons

from src.spatial_percentiles import compute_spatial_percentiles
from src.thresholds_tukey import compute_tukey_thresholds

from src.price_monthly import compute_monthly_prices
from src.ltm_baseline import compute_long_term_monthly_median

from src.ltm_anomaly import compute_ltm_anomaly
from src.yoy_anomaly import compute_yoy_anomaly
from src.five_year_anomaly import compute_five_year_anomaly


def run_indicator_pipeline(
    df,
    indicator_value,
    unit_col,
    date_col,
    indicator_col,
    value_col,
    baseline_method="LTM"
):
    """
    Run the correct processing pipeline depending on indicator type.

    Climate indicators:
        spatial percentiles -> Tukey thresholds

    Price indicators:
        monthly prices -> anomaly calculation
    """

    results = []

    seasons = get_indicator_seasons(indicator_value)

    for season_name, season_months in seasons.items():

        # ------------------------------
        # CLIMATE PIPELINE
        # ------------------------------
        if is_climate_indicator(indicator_value):

            spatial_df = compute_spatial_percentiles(
                df,
                unit_col=unit_col,
                date_col=date_col,
                indicator_col=indicator_col,
                value_col=value_col,
                indicator_value=indicator_value,
                season_months=season_months
            )

            thresholds_df = compute_tukey_thresholds(spatial_df)

            thresholds_df["indicator"] = indicator_value
            thresholds_df["season"] = season_name

            results.append(thresholds_df)

        # ------------------------------
        # PRICE PIPELINE
        # ------------------------------
        elif is_price_indicator(indicator_value):

            # Filter data for this indicator
            df_price = df[df[indicator_col] == indicator_value]

            # Step 1: Convert to monthly prices
            monthly_df = compute_monthly_prices(df_price)

            # Step 2: Choose anomaly method
            if baseline_method == "LTM":

                baseline_df = compute_long_term_monthly_median(monthly_df)

                anomaly_df = compute_ltm_anomaly(
                    monthly_df,
                    baseline_df
                )

            elif baseline_method == "YOY":

                anomaly_df = compute_yoy_anomaly(monthly_df)

            elif baseline_method == "FIVE_YEAR":

                anomaly_df = compute_five_year_anomaly(monthly_df)

            else:
                raise ValueError(f"Unknown baseline method: {baseline_method}")

            anomaly_df["indicator"] = indicator_value
            anomaly_df["season"] = season_name

            results.append(anomaly_df)

    return results
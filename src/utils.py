def get_filtered_distribution(df, indicator):

    from src.config import CLIMATE_INDICATORS, PRICE_INDICATORS, INDICATOR_DIRECTION

    df = df.copy()

    if indicator in CLIMATE_INDICATORS:
        return df[df["value"] < 100]

    elif indicator in PRICE_INDICATORS:
        direction = INDICATOR_DIRECTION.get(indicator, "upper")

        if direction == "upper":
            return df[df["value"] > 0]
        elif direction == "lower":
            return df[df["value"] < 0]

    return df
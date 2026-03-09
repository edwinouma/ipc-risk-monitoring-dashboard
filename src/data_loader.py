import pandas as pd

def load_rainfall_data(filepath):
    df_rainfall = pd.read_excel(filepath)
    return df_rainfall

def load_price_data(filepath):
    df_price_raw = pd.read_excel(filepath)
    return df_price_raw
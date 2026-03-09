import pandas as pd

df = pd.read_parquet("outputs/unit_month_values.parquet")

print(df.columns)
print(df["country"].unique())
print(df["indicator"].unique())
print(df.groupby("country")["indicator"].unique())
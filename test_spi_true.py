import pandas as pd
from src.zscore_true import compute_true_zscore

print("\n🔍 TESTING Z-SCORE ON REAL PRICE ANOMALIES\n")

# -----------------------------------------
# LOAD REAL ANOMALY DATA
# -----------------------------------------
df_price_standard = pd.read_excel(
    "outputs/price_monthly_percent_deviation.xlsx"
)

# -----------------------------------------
# Ensure correct types
# -----------------------------------------
df_price_standard["year_month"] = pd.to_datetime(
    df_price_standard["year_month"]
).dt.to_period("M")

# 🔥 CRITICAL FIX: recreate 'date' column
df_price_standard["date"] = df_price_standard["year_month"].dt.to_timestamp()

# -----------------------------------------
# Pick one country + one indicator
# -----------------------------------------
test_country = df_price_standard["country"].iloc[0]
test_indicator = df_price_standard["indicator"].dropna().unique()[0]

df_test = df_price_standard[
    (df_price_standard["country"] == test_country) &
    (df_price_standard["indicator"] == test_indicator)
].copy()

print(f"Testing indicator: {test_indicator} | Country: {test_country}")

print("\n📊 Input anomaly sample:")
print(df_test.head())

# -----------------------------------------
# APPLY Z-SCORE
# -----------------------------------------
df_z = compute_true_zscore(df_test)

print("\n✅ Z-score output sample:")
print(df_z.head())

# -----------------------------------------
# CHECK DISTRIBUTION
# -----------------------------------------
print("\n📈 Z-score distribution:")
print(df_z["value_zscore"].describe())

# -----------------------------------------
# CHECK BASELINE SEPARATION
# -----------------------------------------
if "baseline_method" in df_z.columns:
    print("\n🔍 Z-score by baseline:")
    print(df_z.groupby("baseline_method")["value_zscore"].describe())

# -----------------------------------------
# MERGE BACK FOR COMPARISON
# -----------------------------------------
df_compare = df_test.merge(
    df_z,
    on=["country", "adm1_name", "year_month", "baseline_method"],
    how="left",
    suffixes=("_anom", "_z")
)

print("\n🔎 Anomaly vs Z-score:")
print(df_compare[["value_anom", "value_zscore"]].head())

print("\n🎯 TEST COMPLETE\n")
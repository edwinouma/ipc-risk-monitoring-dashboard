import pandas as pd
from src.spi_true import compute_true_spi
from src.config import COUNTRY_CONFIG, SPI_TRUE_INDICATORS

# -----------------------------------------
# Select country
# -----------------------------------------
country = "Afghanistan"

# -----------------------------------------
# Load rainfall file from config
# -----------------------------------------
rainfall_file = COUNTRY_CONFIG[country]["rainfall_file"]
df = pd.read_excel(rainfall_file)

print(f"✅ Loaded rainfall file: {rainfall_file}")
print("SHAPE:", df.shape)

print("\nAVAILABLE INDICATORS:")
print(df["indicator"].unique())

# -----------------------------------------
# 🔥 FILTER: Only SPI-relevant indicator
# -----------------------------------------
indicator = SPI_TRUE_INDICATORS[0]  # "rainfall-mm"

df_spi = df[df["indicator"] == indicator].copy()

print(f"\n✅ Using indicator for SPI: {indicator}")
print("FILTERED SHAPE:", df_spi.shape)

# -----------------------------------------
# Run TRUE SPI
# -----------------------------------------
spi_df = compute_true_spi(df_spi)

# -----------------------------------------
# 🔥 ADD BACK INDICATOR COLUMN (IMPORTANT)
# -----------------------------------------
spi_df["indicator"] = indicator

# -----------------------------------------
# Inspect output
# -----------------------------------------
print("\nCOLUMNS:")
print(spi_df.columns)

print("\nHEAD:")
print(spi_df.head())

print("\nVALUE STATS:")
print(spi_df["value"].describe())

print("\nUNIQUE UNITS:", spi_df["adm1_name"].nunique())
print("DATE RANGE:", spi_df["date"].min(), "→", spi_df["date"].max())

# -----------------------------------------
# Save output
# -----------------------------------------
spi_df.to_csv("outputs/test_spi_true_afghanistan.csv", index=False)

print("\n✅ Test file saved: outputs/test_spi_true_afghanistan.csv")
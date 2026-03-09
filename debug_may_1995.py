from src.data_loader import load_data
from src.preprocessing import preprocess_data
from src.unit_month import compute_unit_month_values
from src.config import *

# -----------------------------------------
# 1. Load & preprocess
# -----------------------------------------
df = load_data("data/rainfall_ndvi.xlsx")
df = preprocess_data(df, DATE_COL)

# -----------------------------------------
# 2. Compute unit-month values
# -----------------------------------------
df_unit_month = compute_unit_month_values(
    df,
    UNIT_COL,
    INDICATOR_COL,
    VALUE_COL,
    "rainfall 1-month anomaly [%]"
)

# -----------------------------------------
# 3. Filter May 1995
# -----------------------------------------
may_1995 = df_unit_month[df_unit_month["year_month"] == "1995-05"]

print(may_1995.sort_values(VALUE_COL).to_string())
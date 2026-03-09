# Climatic Threshold Framework – Afghanistan


## Objective
To compute drought alert and alarm thresholds using rainfall and NDVI anomaly data.

## Methodology
- Exclude anomaly values >= 100% (normal or above)
- Compute monthly percentiles per month across units
- Alarm threshold = 25th percentile
- Alarm Tukey threshold  = Q1 - 1.5*IQR
- Compare and validate against reference events

## Architecture
Raw weekly data\
   ↓\
Monthly aggregation (unit level)\
   ↓\
Spatial percentiles\
   ↓\
Threshold calculation\
   ↓\
Trigger classification\
   ↓\
Monthly counts


## Project Structure
- data_loader.py → Load datasets
- preprocessing.py → Cleaning and anomaly filtering
- spatial_percentiles.py → Percentile calculations
- thresholds.py → Alert & alarm logic
- composite_thresholds.py → Combined risk index
- main.py → Orchestrates full pipeline

## Outputs
- County threshold tables
- Saved figures in /outputs


# Tukey Outlier Detection Method for Drought Threshold Setting

1. What is the Tukey Method?

The Tukey method is a robust statistical technique used to detect unusually low or high values in a dataset. It is based on the Interquartile Range (IQR), which measures the spread of the middle 50% of observations.
For drought (lower anomalies worse):

IQR=Q3−Q1

Where:

Q1 = 25th percentile

Q3 = 75th percentile

Tukey defines extreme low values using the lower fence:

Lower Fence=Q1−k×IQR

Where:


- k=1.5 is the classical statistical standard for identifying outliers.

- Lower values beyond this fence are considered statistically abnormal.


This method was introduced by John Tukey and is widely used in boxplots and anomaly detection.

2. Why We Use It in This Project

This project focuses on detecting drought conditions using rainfall and NDVI anomalies.

Using simple percentiles (e.g., Q1 alone) only identifies “below-normal” conditions. However, drought monitoring requires identifying statistically abnormal deficits, not just moderately low values.

For example, if we were to use Q1 as our alert, it would mean, Any value below the historical 25th percentile is an alert. 
But statistically, Q1 is not an extreme value. It simply means:

- 25% of historical observations are below this value.

- So this condition will happen relatively often.

In other words:

👉 Q1 identifies below-normal conditions,\
👉 but not necessarily abnormal or alarming drought.

3. How It Is Applied Here

For each indicator:

1.  Monthly spatial Q1 and Q3 are computed.

2. The median Q1 and median IQR across time are calculated.

3. Two drought thresholds are defined:


- **Alert Threshold**

`Q1_median - 1.0 × IQR_median`

- **Alarm Threshold**

`Q1_median - 1.5 × IQR_median`


Where:

1.0 × IQR identifies moderate drought stress.

1.5 × IQR identifies statistically extreme drought conditions.


4. Why 1.0 and 1.5 Multipliers?

- 1.5 × IQR is the classical statistical definition of an outlier.

- 1.0 × IQR is used as an early-warning level to detect emerging stress.

- These values balance sensitivity and stability.

- Thresholds can be calibrated based on historical drought validation.


5. Interpretation

- Values below the Alert threshold indicate meaningful drought stress.

- Values below the Alarm threshold indicate statistically extreme drought.

- Thresholds are dynamic and adapt to each indicator’s variability.




Lower Fence

= 𝑄1 − 1.5 × 𝐼𝑄𝑅 

Lower Fence =Q1−1.5×IQR

Where:

Q1 = 25th percentile

Q3 = 75th percentile

IQR = Q3 − Q1

This identifies statistically extreme drought years.


## DASHBOARD

🎯 FINAL REQUIREMENTS (Confirmed)

The dashboard must:

Controls

✅ Indicator selector

✅ Method selector (Percentile / Tukey)

✅ Admin selector (Province OR National)

✅ Editable thresholds

✅ Thresholds persist between sessions

Outputs

✅ Stacked trigger chart

✅ Trigger counts table

✅ Classification matrix

✅ National aggregation option

✅ Export updated matrices

❌ No seasonal filtering (for now)

🔒 Internal (TWG only)


## SYSTEM ARCHITECTURE

We divide the system into 4 layers.

## 1. DATA LAYER (Static)

This should be precomputed once and saved:

unit_month_values

default thresholds

historical percentiles

Dashboard will NOT recompute these every time.

We load them once at startup.

## 2. THRESHOLD ENGINE (Dynamic)

We create a small persistent storage:

## 3. CLASSIFICATION ENGINE (Reactive)

When threshold changes:

We DO NOT recompute percentiles.

## We:

1. Load precomputed unit-month values

2. Apply chosen thresholds

3. Recalculate:

- Alarm

- Alert

- Minimal

4. Recompute:

- Counts

- National aggregation

- Matrix

## 4. PRESENTATION LAYER (Streamlit)

Layout structure:

---------------------------------------------------
| Indicator | Method | Admin | Apply Button     |
---------------------------------------------------
| Editable Threshold Table                        |
---------------------------------------------------
| Stacked Chart                                   |
---------------------------------------------------
| Tabs:                                           |
|  - Trigger Counts                               |
|  - Classification Matrix                        |
|  - Download Buttons                             |
---------------------------------------------------

## 🧠 NATIONAL AGGREGATION DESIGN

National aggregation must not simply average values.

It should compute:

- provinces in Alarm
- provinces in Alert

- % provinces in Alarm

- % provinces in Alert


## BUILDING DASHBOARD WORK BEGINS

- ## threshold_storage.py

This is the persistence layer.

It will:

- Load default thresholds (from outputs/thresholds_results.csv)

- Load overrides (from data/threshold_overrides.json)

- Return active thresholds

- Save overrides

- Reset overrides

| Function                | Purpose                 |
| ----------------------- | ----------------------- |
| load_default_thresholds | Read backend thresholds |
| load_overrides          | Read JSON overrides     |
| save_override           | Save TWG edits          |
| reset_override          | Reset to default        |
| get_active_thresholds   | Return correct values   |


- ## classification_engine.py

This will:

- Take unit_month_values
- Apply thresholds
- Return classification
- Return counts
- Return proportions

This module must:

1. Take precomputed unit_month_values
2. Filter selected provinces
3. Apply alarm & alert thresholds
4. Create classification
5. Compute:
- Counts per month
- Percentages
6. Return clean data structures


## 🧠 Why This Is Clean

- Works for national
- Works for regional subsets
- Works for dynamic thresholds
- No percentile computation
- No persistence logic

Pure classification engine

- ## spatial_recalculation.py

It will:

- Recompute spatial percentiles
- Recompute composite thresholds
- Recompute Tukey thresholds

This is the Dynamic Baseline Engine

It will:

- Filter selected provinces
- Recompute spatial percentiles per month
- Recompute composite thresholds
- Recompute Tukey thresholds
- Return fresh thresholds


- ## national_aggregation.py

It will:

- Aggregate classification results
- Recalculate counts
- Recalculate proportions
- Guarantee fixed total_units logic

We now move to the final piece, the streamlit dashboard

## 🚀 app.py — The Streamlit Dashboard

This is where everything connects.

🎯 What This Dashboard Now Supports

- Indicator selection
- Method selection
- Multi-select provinces
- Fixed vs Dynamic baseline
- Recalculate thresholds
- Edit thresholds
- Persist thresholds
- Reset to default
- Aggregated stacked chart
- Province matrix toggle
- Download results

## POWERFUL EVIDENCE-BASED UNITS GROUPING

In the classification matrix (unit × month), we need additional columns at the far right:

For each unit:

- % of Alarm months

- % of Alert months

- Possibly Sum (Alarm + Alert)

## 🧠 Why This Is Powerful

This allows TWG to:

 - Identify chronically vulnerable provinces

- Identify stable provinces

- Cluster provinces objectively

- Compare dynamic baseline vs national baseline behaviour

- Justify region grouping statistically
## This becomes a vulnerability signature.


## THRESHOLD SETTING FOR PRICES.

1️⃣ Compute Long-Term Monthly Average (LTA)

For example:

For May baseline:

𝐿𝑇𝐴𝑀𝑎𝑦 = mean of all May prices across historical years\



So:

Jan baseline = average of all Januaries

Feb baseline = average of all Februaries

...

Dec baseline = average of all Decembers

This gives you 12 seasonal baselines per province.

2️⃣ Compute % Deviation from LTA

So:

- Each month is compared to its own seasonal norm.

- Seasonality is controlled.

- You avoid comparing harvest months to lean months.

3️⃣ Build Time Series of % Deviations

## STRUCTURE

✅ STEP 1 — Weekly → Monthly Aggregation

We must first bring weekly prices to monthly.

We’ll use monthly mean of weekly prices (standard approach unless you prefer median).

Create a new file:

## 🧠 Important Notes

- Median baseline is robust for 5-year data.

- Baseline uses full historical monthly dataset.

- Time slider filtering happens AFTER anomaly computation.

This keeps methodology clean and IPC-defensible.

## SCALING UP OUR SYSTEM TO MULTI-COUNTRY

DATA LAYER
----------
- country
- adm1
- date
- indicator
- value
- baseline

THRESHOLD LAYER
---------------
- country
- indicator
- baseline
- method
- season_scope
- alarm
- alert

CLASSIFICATION LAYER
--------------------
- classification_utils.py (unchanged)

DASHBOARD LAYER
---------------
- country toggle
- indicator toggle
- baseline toggle
- method toggle
- season toggle


## 🎯 PHASE 1 — Lock Afghanistan as the Reference Model

We will:

1. Add country = "Afghanistan" column to your dataset

2. Add baseline column for prices

3. Compute:

- LTM

- YoY

- 5-year average deviation

4. Regenerate:

- unit_month_values.parquet

- thresholds_results.csv

5. Add country + baseline toggles in dashboard

6. Confirm everything works end-to-end

Then the system becomes extensible.

## 🧱 STEP 1 — Data Model Upgrade (Very Important)

The new core dataset structure should be:

| country | adm1_name | date | indicator | value | baseline |
| ------- | --------- | ---- | --------- | ----- | -------- |

For non-price indicators:

- baseline = "standard"

For price indicators:

- baseline = "LTM"

- baseline = "YoY"

- baseline = "5yr_avg"

This avoids duplicating indicator names.

## 🧠 STEP 2 — Baseline Calculations (Using Afghanistan Data)

We do this inside preprocessing, not inside dashboard.

## A. LTM (Last 12 Months Deviation)

For each province & commodity:

## B. YoY (Year-on-Year)

For each province & commodity:

## C. 5-Year Average Deviation

For each province & month:

## 🏗 STEP 3 — Threshold Table Must Expand

Your thresholds_results.csv must now include:

| country | indicator | baseline | method | season_scope | alarm | alert |

Otherwise:

Afghanistan YoY thresholds could mix with Afghanistan LTM thresholds.

## 🎛 STEP 4 — Dashboard Toggles

We add:

- Country Toggle
- Baseline Toggle (only if price indicator)

## 🚀 Final System Will Support

| Country     | Indicator | Baseline | Method     | Season     |
| ----------- | --------- | -------- | ---------- | ---------- |
| Afghanistan | Wheat     | YoY      | Percentile | Planting   |
| Afghanistan | Wheat     | LTM      | Tukey      | All Months |
| Afghanistan | Rainfall  | standard | Tukey      | Off-Season |
| Kenya       | Maize     | 5yr_avg  | Percentile | Long Rains |


src\
│
├── data_loader.py\
├── preprocessing.py\
|── indicator_groups.py
│
├──baselines\
│   ├── ltm.py\
│   ├── yoy.py\
│   ├── five_year_avg.py\
│   └── baseline_selector.py\
│
├── spatial_percentiles.py\
├── thresholds_tukey.py\
├── composite_thresholds.py\
├── classification_matrix.py



df_unit_month   →  country_df  →  df_filtered
(all data)         (country)      (indicator)


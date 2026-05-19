# Jimmy John's Inventory Demand Predictor

Portfolio project for forecasting daily bread demand and evaluating inventory decisions for a quick-service restaurant workflow.

This public version keeps the project structure, feature engineering, modeling code, and analysis approach while excluding private operational data. The included sample files are synthetic and are only meant to show the expected schema.

## Problem

Bread preparation depends on projected sales, day-of-week patterns, recent demand, and store-level operating rules. Over-projecting creates waste, while under-projecting risks stockouts during service.

This project turns weekly usage reports and daily sales projection sheets into a forecasting workflow that can:

- Extract bread usage and sales projection data from Excel reports.
- Build daily demand features from sales and recent bread usage.
- Train a time-series regression model for bread demand.
- Compare projection rules, including tray value scenarios such as 275 vs. 300.
- Estimate gaps between projected, theoretical, and actual usage.

## Repository Contents

```text
src/
  extract_bread_weekly.py                 # Extract weekly bread usage from raw Excel reports
  extract_daily_sales.py                  # Extract daily sales and projection fields
  analyze_bread_projection_efficiency.py  # Compare daily projections against weekly usage
  compare_tray_value_275_vs_300.py        # Evaluate tray value policy scenarios
  train_daily_bread_model.py              # Train demand forecasting model

data/sample/
  daily_sales_sample.csv                  # Synthetic sample schema
  bread_weekly_sample.csv                 # Synthetic sample schema
```

Private folders are intentionally ignored:

```text
Data_raw_daily_sales_reports/
Data_raw_weekly_reports/
data/processed/
models/
```

## Approach

1. Parse raw Excel reports into clean tabular datasets.
2. Join daily sales projections with weekly bread usage.
3. Create time-series features such as day of week, lag demand, rolling bread demand, and rolling sales.
4. Train a `GradientBoostingRegressor` with `TimeSeriesSplit` validation.
5. Analyze operational scenarios by comparing projected bread counts against actual and theoretical usage.

## Model Features

The current model uses:

- `total_sales`
- `dow`
- `lag_1`
- `roll7`
- `sales_roll7`

The target is estimated daily bread usage.

## How To Run Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

With private source reports available locally, run the pipeline in this order:

```bash
python src/extract_bread_weekly.py
python src/extract_daily_sales.py
python src/analyze_bread_projection_efficiency.py
python src/compare_tray_value_275_vs_300.py
python src/train_daily_bread_model.py
```

The scripts write generated CSVs to `data/processed/` and the trained model to `models/`. Those outputs are ignored in the public repo because they are derived from private data.

## Data Privacy

This repository does not include real sales reports, usage reports, processed business data, or trained model artifacts. Public sample files are synthetic and do not represent actual store performance.

## Why This Project Matters

The project demonstrates an end-to-end analytics workflow for an operational forecasting problem: extracting messy Excel data, engineering practical time-series features, validating a model without future leakage, and translating predictions into inventory decisions.

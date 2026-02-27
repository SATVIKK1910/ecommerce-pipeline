# E-Commerce Pipeline

End-to-end data pipeline: synthetic data generation → PostgreSQL → analytics SQL → feature engineering → ML model.

## Setup
```bash
pip install -r requirements.txt
```

## How to Generate Data
```bash
python src/generate_data.py --customers 1000 --orders 5000 --seed 42 --out_dir data
```

## How to Start Postgres

This project uses [Neon.tech](https://neon.tech) — a free cloud PostgreSQL service.
1. Sign up at neon.tech
2. Create a project called `ecommerce`
3. Copy your connection string
4. Set it as environment variable: `export DATABASE_URL="postgresql://..."`

## How to Load Data
```bash
python src/load_data.py
```

This creates the schema and bulk loads all CSVs using PostgreSQL `COPY` via psycopg3.

## Indexes Added
| Index | Reason |
|---|---|
| `idx_orders_customer_id` | speeds up JOIN between orders and customers |
| `idx_orders_created_at` | speeds up date range filters in analytics queries |
| `idx_order_items_order_id` | speeds up JOIN between order_items and orders |

## How to Run Analytics Queries

Run queries in `sql/queries.sql` against your Neon database using any Postgres client,
or run them via psycopg3 in Python as shown in the Colab notebook.

## How to Build Features
```bash
python src/feature_pipeline.py
```

Uses Polars LazyFrames for memory-efficient processing. Outputs `artifacts/features.parquet`.

## How to Train and Evaluate the Model
```bash
python src/train.py
```

Trains Logistic Regression and Random Forest, prints ROC-AUC, F1, confusion matrix,
and saves the best model to `artifacts/model.joblib`.

## Run Full Pipeline
```bash
bash scripts/run_pipeline.sh
```

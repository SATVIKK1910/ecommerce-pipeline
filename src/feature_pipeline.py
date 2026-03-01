import polars as pl
from datetime import datetime
import os

os.makedirs("artifacts", exist_ok=True)
NOW = datetime(2025, 6, 30)

orders_lazy      = pl.scan_csv("data/orders.csv", try_parse_dates=True)
order_items_lazy = pl.scan_csv("data/order_items.csv", try_parse_dates=True)
labels_lazy      = pl.scan_csv("data/labels.csv")

spend_90d = (
    orders_lazy
    .filter(pl.col("created_at") >= pl.lit(datetime(2024, 10, 1)))
    .group_by("customer_id")
    .agg([pl.col("total_amount").sum().alias("customer_total_spend_90d"),
          pl.col("order_id").count().alias("customer_order_count_90d")])
)
avg_basket = (
    orders_lazy.group_by("customer_id")
    .agg(pl.col("total_amount").mean().alias("avg_basket_size"))
)
categories = (
    order_items_lazy
    .join(pl.scan_csv("data/orders.csv").select(["order_id","customer_id"]), on="order_id")
    .join(pl.scan_csv("data/products.csv").select(["product_id","category"]), on="product_id")
    .group_by("customer_id")
    .agg(pl.col("category").n_unique().alias("distinct_categories_bought"))
)
recency = (
    orders_lazy.group_by("customer_id")
    .agg(pl.col("created_at").max().alias("last_order_date"))
    .with_columns((pl.lit(NOW) - pl.col("last_order_date")).dt.total_days().alias("days_since_last_order"))
    .select(["customer_id","days_since_last_order"])
)
total_orders = (
    orders_lazy.group_by("customer_id")
    .agg(pl.col("order_id").count().alias("total_orders_alltime"))
)

features = (
    labels_lazy
    .join(spend_90d, on="customer_id", how="left")
    .join(avg_basket, on="customer_id", how="left")
    .join(categories, on="customer_id", how="left")
    .join(recency, on="customer_id", how="left")
    .join(total_orders, on="customer_id", how="left")
    .fill_null(0)
)

features_df = features.collect()
print(f"Features shape: {features_df.shape}")
features_df.write_parquet("artifacts/features.parquet")
print("artifacts/features.parquet saved!")

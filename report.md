# Model Report

## Features Built
| Feature | Reason |
|---|---|
| customer_total_spend_90d | Recent spend signals buying intent |
| customer_order_count_90d | Recent activity frequency |
| avg_basket_size | Spending behaviour per order |
| distinct_categories_bought | Breadth of interest across catalogue |
| days_since_last_order | Recency - key RFM signal |
| total_orders_alltime | Overall engagement with platform |

All features were computed using Polars LazyFrames (scan_csv) to avoid
loading entire datasets into RAM - important for big-data scalability.

## Models Tried
- Logistic Regression - fast, interpretable baseline, features scaled with StandardScaler
- Random Forest - non-linear, handles feature interactions, no scaling needed

## Results
| Model | ROC-AUC | F1 Score |
|---|---|---|
| Logistic Regression | 0.9028 | 0.7763 |
| Random Forest | 0.8821 | 0.7568 |

Winner: Logistic Regression (ROC-AUC 0.9028)

Confusion Matrix (Logistic Regression, test set n=200):
- TN=107  FP=17
- FN=17   TP=59

## Loading the Model for Inference
import joblib
artifact = joblib.load("artifacts/model.joblib")
model    = artifact["model"]
scaler   = artifact["scaler"]
features = artifact["features"]

## 3 Concrete Next Improvements

1. More features - add customer_age, city, marketing_opt_in,
   and product-level features like favourite category or avg product price tier.

2. Better label design - instead of a binary label from order gaps,
   use a proper train/validation time split (train on Jan-Apr, predict May-Jun)
   to avoid data leakage and simulate real deployment.

3. Gradient Boosting model - try XGBoost or LightGBM which typically
   outperform Random Forest on tabular data, with built-in handling of
   missing values and faster training at scale.

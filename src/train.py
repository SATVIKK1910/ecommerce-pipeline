import polars as pl
import numpy as np
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, f1_score, confusion_matrix
from sklearn.preprocessing import StandardScaler

os.makedirs("artifacts", exist_ok=True)
df = pl.read_parquet("artifacts/features.parquet").to_pandas()

FEATURES = ["customer_total_spend_90d","customer_order_count_90d","avg_basket_size",
            "distinct_categories_bought","days_since_last_order","total_orders_alltime"]
TARGET = "will_purchase_next_30d"

X = df[FEATURES].values
y = df[TARGET].values
print(f"Dataset: {X.shape[0]} rows | Label balance: {y.mean():.1%} positive")

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc  = scaler.transform(X_test)

def evaluate(name, model, X_tr, X_te, y_tr, y_te):
    model.fit(X_tr, y_tr)
    y_pred  = model.predict(X_te)
    y_proba = model.predict_proba(X_te)[:, 1]
    auc = roc_auc_score(y_te, y_proba)
    f1  = f1_score(y_te, y_pred)
    cm  = confusion_matrix(y_te, y_pred)
    print(f"\n{\'=\'*45}\n  {name}\n{\'=\'*45}")
    print(f"  ROC-AUC : {auc:.4f}\n  F1 Score: {f1:.4f}")
    print(f"  Confusion Matrix:\n    TN={cm[0,0]}  FP={cm[0,1]}\n    FN={cm[1,0]}  TP={cm[1,1]}")
    return model, auc, f1

lr, lr_auc, lr_f1 = evaluate("Logistic Regression",
    LogisticRegression(random_state=42, max_iter=1000), X_train_sc, X_test_sc, y_train, y_test)
rf, rf_auc, rf_f1 = evaluate("Random Forest",
    RandomForestClassifier(n_estimators=100, random_state=42), X_train, X_test, y_train, y_test)

best_model = rf if rf_auc >= lr_auc else lr
best_name  = "RandomForest" if rf_auc >= lr_auc else "LogisticRegression"
joblib.dump({"model": best_model, "scaler": scaler, "features": FEATURES}, "artifacts/model.joblib")
print(f"\n🏆 Best model: {best_name}")
print("✅ artifacts/model.joblib saved!")

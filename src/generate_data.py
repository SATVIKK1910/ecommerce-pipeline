import argparse
import random
import os
from datetime import datetime, timedelta
import csv
import numpy as np
from collections import defaultdict

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--customers", type=int, default=1000)
    parser.add_argument("--orders",    type=int, default=5000)
    parser.add_argument("--seed",      type=int, default=42)
    parser.add_argument("--out_dir",   type=str, default="data")
    return parser.parse_args()

args = get_args()
random.seed(args.seed)
np.random.seed(args.seed)
os.makedirs(args.out_dir, exist_ok=True)

CITIES = ["New York","Los Angeles","Chicago","Houston","Phoenix",
          "Philadelphia","San Antonio","San Diego","Dallas","San Jose"]
CATEGORIES = ["Electronics","Clothing","Books","Home","Sports","Beauty","Toys","Food"]
PAYMENT_METHODS = ["credit_card","debit_card","paypal","bank_transfer"]
NOW = datetime(2025, 6, 30)
START_DATE = datetime(2023, 1, 1)

def rand_date(start, end):
    delta = end - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))

# Products
N_PRODUCTS = 200
products = []
for i in range(1, N_PRODUCTS + 1):
    category = random.choice(CATEGORIES)
    base = {"Electronics":150,"Clothing":40,"Books":20,"Home":60,
            "Sports":55,"Beauty":30,"Toys":25,"Food":15}[category]
    price = round(random.uniform(base * 0.5, base * 2.5), 2)
    products.append({"product_id": i, "category": category, "price": price})

with open(f"{args.out_dir}/products.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["product_id","category","price"])
    w.writeheader(); w.writerows(products)
print("✅ products.csv")

# Customers
customers = []
customer_types = []
for i in range(1, args.customers + 1):
    is_power = random.random() < 0.10
    customer_types.append("power" if is_power else "casual")
    customers.append({
        "customer_id": i,
        "created_at": rand_date(START_DATE, NOW - timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S"),
        "city": random.choice(CITIES),
        "age": random.randint(18, 70),
        "marketing_opt_in": random.choice([True, False])
    })

with open(f"{args.out_dir}/customers.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["customer_id","created_at","city","age","marketing_opt_in"])
    w.writeheader(); w.writerows(customers)
print("✅ customers.csv")

# Orders + Order Items
weights = [5 if t == "power" else 1 for t in customer_types]
total_w = sum(weights)
probs = [w / total_w for w in weights]
customer_ids = [c["customer_id"] for c in customers]

orders, order_items, item_id = [], [], 1

def seasonal_date():
    d = rand_date(START_DATE, NOW)
    if d.month not in (11, 12) and random.random() < 0.3:
        d = rand_date(START_DATE, NOW)
    return d

for order_id in range(1, args.orders + 1):
    cust_id = int(np.random.choice(customer_ids, p=probs))
    order_date = seasonal_date()
    n_items = random.randint(1, 5)
    chosen_products = random.choices(products, k=n_items)
    total = 0.0
    for prod in chosen_products:
        qty = random.randint(1, 4)
        unit_price = prod["price"]
        total += round(qty * unit_price, 2)
        order_items.append({
            "order_item_id": item_id, "order_id": order_id,
            "product_id": prod["product_id"], "quantity": qty, "unit_price": unit_price
        })
        item_id += 1
    orders.append({
        "order_id": order_id, "customer_id": cust_id,
        "created_at": order_date.strftime("%Y-%m-%d %H:%M:%S"),
        "total_amount": round(total, 2),
        "payment_method": random.choice(PAYMENT_METHODS)
    })

with open(f"{args.out_dir}/orders.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["order_id","customer_id","created_at","total_amount","payment_method"])
    w.writeheader(); w.writerows(orders)
print("✅ orders.csv")

with open(f"{args.out_dir}/order_items.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["order_item_id","order_id","product_id","quantity","unit_price"])
    w.writeheader(); w.writerows(order_items)
print("✅ order_items.csv")

# Labels
customer_order_dates = defaultdict(list)
for o in orders:
    customer_order_dates[o["customer_id"]].append(
        datetime.strptime(o["created_at"], "%Y-%m-%d %H:%M:%S"))

labels = []
for cust in customers:
    cid = cust["customer_id"]
    dates = sorted(customer_order_dates.get(cid, []))
    if len(dates) < 2:
        labels.append({"customer_id": cid, "will_purchase_next_30d": 0})
        continue
    purchased_again = any((dates[i+1] - dates[i]).days <= 30 for i in range(len(dates)-1))
    labels.append({"customer_id": cid, "will_purchase_next_30d": int(purchased_again)})

with open(f"{args.out_dir}/labels.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["customer_id","will_purchase_next_30d"])
    w.writeheader(); w.writerows(labels)
pos = sum(l["will_purchase_next_30d"] for l in labels)
print(f"✅ labels.csv (positive rate: {pos/len(labels):.1%})")
print("🎉 Dataset generation complete!")

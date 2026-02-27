import psycopg
import csv
import io
import os

CONN_STRING = os.environ.get("DATABASE_URL", "YOUR_NEON_CONNECTION_STRING")

def bulk_copy(cursor, table, columns, filepath):
    with open(filepath, "r") as f:
        reader = csv.DictReader(f)
        rows = [tuple(row[c] for c in columns) for row in reader]
    buf = io.StringIO()
    import csv as _csv
    writer = _csv.writer(buf)
    writer.writerows(rows)
    buf.seek(0)
    col_str = ", ".join(columns)
    with cursor.copy(f"COPY {table} ({col_str}) FROM STDIN WITH (FORMAT CSV)") as copy:
        copy.write(buf.read())
    print(f"✅ Loaded {len(rows)} rows into {table}")

with psycopg.connect(CONN_STRING) as conn:
    with conn.cursor() as cur:
        with open("sql/schema.sql") as f:
            cur.execute(f.read())
        conn.commit()
        print("✅ Schema created")
        bulk_copy(cur, "customers",   ["customer_id","created_at","city","age","marketing_opt_in"],  "data/customers.csv")
        bulk_copy(cur, "products",    ["product_id","category","price"],                              "data/products.csv")
        bulk_copy(cur, "orders",      ["order_id","customer_id","created_at","total_amount","payment_method"], "data/orders.csv")
        bulk_copy(cur, "order_items", ["order_item_id","order_id","product_id","quantity","unit_price"],        "data/order_items.csv")
        conn.commit()
        print("🎉 All data loaded!")

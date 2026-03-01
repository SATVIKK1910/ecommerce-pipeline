
CREATE TABLE IF NOT EXISTS customers (
    customer_id       INTEGER PRIMARY KEY,
    created_at        TIMESTAMP NOT NULL,
    city              VARCHAR(100),
    age               INTEGER CHECK (age BETWEEN 0 AND 120),
    marketing_opt_in  BOOLEAN
);

CREATE TABLE IF NOT EXISTS products (
    product_id  INTEGER PRIMARY KEY,
    category    VARCHAR(100),
    price       NUMERIC(10,2) CHECK (price > 0)
);

CREATE TABLE IF NOT EXISTS orders (
    order_id        INTEGER PRIMARY KEY,
    customer_id     INTEGER NOT NULL REFERENCES customers(customer_id),
    created_at      TIMESTAMP NOT NULL,
    total_amount    NUMERIC(10,2) CHECK (total_amount >= 0),
    payment_method  VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS order_items (
    order_item_id  INTEGER PRIMARY KEY,
    order_id       INTEGER NOT NULL REFERENCES orders(order_id),
    product_id     INTEGER NOT NULL REFERENCES products(product_id),
    quantity       INTEGER CHECK (quantity > 0),
    unit_price     NUMERIC(10,2) CHECK (unit_price > 0)
);

CREATE INDEX IF NOT EXISTS idx_orders_customer_id   ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_created_at    ON orders(created_at);
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);

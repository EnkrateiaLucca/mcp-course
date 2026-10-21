"""Build shop.db: a small, deterministic e-commerce dataset (~2 years of orders)."""

import random
import sqlite3
import sys
from datetime import date, timedelta

DB = sys.argv[1] if len(sys.argv) > 1 else "shop.db"
random.seed(42)

PRODUCTS = [
    ("Trail Running Shoes", "Footwear", 129.0),
    ("Everyday Sneakers", "Footwear", 89.0),
    ("Hiking Boots", "Footwear", 179.0),
    ("Merino T-Shirt", "Apparel", 59.0),
    ("Rain Jacket", "Apparel", 149.0),
    ("Fleece Hoodie", "Apparel", 79.0),
    ("Running Shorts", "Apparel", 39.0),
    ("Insulated Bottle", "Gear", 34.0),
    ("Daypack 20L", "Gear", 99.0),
    ("Headlamp", "Gear", 45.0),
    ("Trekking Poles", "Gear", 119.0),
    ("Wool Socks (3-pack)", "Accessories", 29.0),
    ("Sun Cap", "Accessories", 25.0),
    ("Sunglasses", "Accessories", 69.0),
]
COUNTRIES = ["US", "US", "US", "UK", "DE", "FR", "BR", "PT", "CA", "AU"]
FIRST = ["Ana", "Ben", "Chloe", "Diego", "Emma", "Felix", "Grace", "Hugo", "Ines", "Jon", "Kai", "Lena", "Maya", "Noah"]
LAST = ["Silva", "Smith", "Muller", "Martin", "Costa", "Brown", "Rossi", "Lee", "Garcia", "Novak"]
START, END = date(2024, 11, 1), date(2026, 10, 20)

con = sqlite3.connect(DB)
con.executescript("""
DROP VIEW IF EXISTS sales;
DROP TABLE IF EXISTS order_items; DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products; DROP TABLE IF EXISTS customers;
CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT, email TEXT, country TEXT, signup_date TEXT);
CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, category TEXT, price REAL);
CREATE TABLE orders (id INTEGER PRIMARY KEY, customer_id INTEGER REFERENCES customers(id),
                     order_date TEXT, status TEXT CHECK (status IN ('completed', 'refunded')));
CREATE TABLE order_items (order_id INTEGER REFERENCES orders(id), product_id INTEGER REFERENCES products(id),
                          quantity INTEGER, unit_price REAL);
-- The one official definition of revenue: completed orders only, refunds excluded.
CREATE VIEW sales AS
  SELECT o.id AS order_id, o.order_date, o.customer_id, c.country,
         p.id AS product_id, p.name AS product, p.category, i.quantity, i.quantity * i.unit_price AS revenue
  FROM orders o JOIN order_items i ON i.order_id = o.id
  JOIN products p ON p.id = i.product_id JOIN customers c ON c.id = o.customer_id
  WHERE o.status = 'completed';
""")
con.executemany("INSERT INTO products (name, category, price) VALUES (?, ?, ?)", PRODUCTS)

customers, order_id = [], 0
for day in range((END - START).days + 1):
    d = START + timedelta(days=day)
    # New signups grow over time.
    for _ in range(random.randint(0, 2 + day // 200)):
        name = f"{random.choice(FIRST)} {random.choice(LAST)}"
        cur = con.execute(
            "INSERT INTO customers (name, email, country, signup_date) VALUES (?, ?, ?, ?)",
            (name, f"{name.lower().replace(' ', '.')}{len(customers)}@example.com", random.choice(COUNTRIES), d.isoformat()),
        )
        customers.append(cur.lastrowid)
    if not customers:
        continue
    # Orders: growth trend + holiday spike + weekend bump.
    base = 4 + day / 60 + (8 if d.month in (11, 12) else 0) + (2 if d.weekday() >= 5 else 0)
    for _ in range(int(random.gauss(base, 2)) if base > 0 else 0):
        order_id += 1
        status = "refunded" if random.random() < 0.06 else "completed"
        con.execute("INSERT INTO orders VALUES (?, ?, ?, ?)", (order_id, random.choice(customers), d.isoformat(), status))
        for pid in random.sample(range(1, len(PRODUCTS) + 1), random.choice([1, 1, 1, 2, 2, 3])):
            price = PRODUCTS[pid - 1][2] * (0.8 if d.month == 11 and d.day >= 25 else 1.0)  # Black Friday sale
            con.execute("INSERT INTO order_items VALUES (?, ?, ?, ?)", (order_id, pid, random.choice([1, 1, 1, 2]), price))

con.commit()
print(f"{DB}: {len(customers)} customers, {order_id} orders")

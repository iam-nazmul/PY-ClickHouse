"""Insert 1 million fake demo rows into demo.sales, in batches."""

import random
import time
from datetime import date, timedelta
from decimal import Decimal

import clickhouse_connect

TOTAL_ROWS = 1_000_000
BATCH_SIZE = 100_000

CATALOG = {
    "Electronics": ["Laptop", "Mouse", "Monitor", "Keyboard", "Headphones", "Webcam", "Tablet", "Smartphone"],
    "Furniture": ["Desk Chair", "Bookshelf", "Standing Desk", "Filing Cabinet", "Sofa", "Coffee Table"],
    "Stationery": ["Notebook", "Pen Pack", "Sticky Notes", "Whiteboard", "Stapler"],
    "Appliances": ["Coffee Maker", "Microwave", "Air Purifier", "Kettle", "Vacuum"],
    "Sports": ["Yoga Mat", "Dumbbell Set", "Running Shoes", "Water Bottle", "Bicycle"],
}
CATEGORIES = list(CATALOG)

START_DATE = date(2024, 1, 1)
DATE_RANGE_DAYS = 730  # two years of sales

COLUMNS = ["id", "product", "category", "quantity", "price", "sale_date"]

client = clickhouse_connect.get_client(
    host="localhost",
    port=8123,
    username="nazmul",
    password="testPass123",
)

client.command("CREATE DATABASE IF NOT EXISTS demo")

client.command("""
    CREATE TABLE IF NOT EXISTS demo.sales (
        id          UInt32,
        product     String,
        category    LowCardinality(String),
        quantity    UInt32,
        price       Decimal(10, 2),
        sale_date   Date,
        created_at  DateTime DEFAULT now()
    )
    ENGINE = MergeTree()
    ORDER BY id
""")

# Continue ids after whatever is already in the table.
start_id = int(client.command("SELECT ifNull(max(id), 0) FROM demo.sales")) + 1
print(f"Seeding {TOTAL_ROWS:,} rows starting at id={start_id:,}")


def make_batch(first_id, size):
    rows = []
    for offset in range(size):
        category = random.choice(CATEGORIES)
        rows.append([
            first_id + offset,
            random.choice(CATALOG[category]),
            category,
            random.randint(1, 20),
            Decimal(str(round(random.uniform(5.0, 2500.0), 2))),
            START_DATE + timedelta(days=random.randrange(DATE_RANGE_DAYS)),
        ])
    return rows


started = time.time()
inserted = 0

while inserted < TOTAL_ROWS:
    size = min(BATCH_SIZE, TOTAL_ROWS - inserted)
    batch = make_batch(start_id + inserted, size)
    client.insert("demo.sales", batch, column_names=COLUMNS)
    inserted += size
    elapsed = time.time() - started
    print(f"  {inserted:>9,} / {TOTAL_ROWS:,} rows  ({elapsed:6.1f}s, {inserted / elapsed:,.0f} rows/s)")

print(f"\nDone in {time.time() - started:.1f}s")

total = client.command("SELECT count() FROM demo.sales")
print(f"Total rows in demo.sales: {int(total):,}")

result = client.query("""
    SELECT category,
           count()                  AS orders,
           sum(quantity * price)    AS revenue,
           round(avg(price), 2)     AS avg_price
    FROM demo.sales
    GROUP BY category
    ORDER BY revenue DESC
""")
print("\n--- revenue by category ---")
for row in result.result_rows:
    print(row)

size = client.query("""
    SELECT formatReadableSize(sum(bytes_on_disk)) AS on_disk,
           formatReadableQuantity(sum(rows))      AS rows
    FROM system.parts
    WHERE database = 'demo' AND table = 'sales' AND active
""")
print(f"\nOn disk: {size.result_rows[0][0]} for {size.result_rows[0][1]} rows")

client.close()

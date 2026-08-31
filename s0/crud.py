"""CRUD operations on a ClickHouse `demo.sales` table."""

from datetime import date
from decimal import Decimal

import clickhouse_connect

client = clickhouse_connect.get_client(
    host="localhost",
    port=8123,
    username="nazmul",
    password="testPass123",
)

# Mutations (UPDATE/DELETE) are async by default; wait for them so the
# next SELECT sees the change.
MUTATION_SETTINGS = {"mutations_sync": 1}
DELETE_SETTINGS = {"mutations_sync": 1, "lightweight_deletes_sync": 2}


def show(title, rows):
    print(f"\n--- {title} ---")
    if not rows:
        print("(no rows)")
        return
    for row in rows:
        print(row)


# ---------------------------------------------------------------- setup ----
client.command("CREATE DATABASE IF NOT EXISTS demo")

client.command("DROP TABLE IF EXISTS demo.sales")

client.command("""
    CREATE TABLE demo.sales (
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

print("Table demo.sales ready!")


# ------------------------------------------------------------- CREATE ------
columns = ["id", "product", "category", "quantity", "price", "sale_date"]
rows = [
    [1, "Laptop", "Electronics", 2, Decimal("1200.50"), date(2026, 1, 15)],
    [2, "Mouse", "Electronics", 10, Decimal("25.00"), date(2026, 1, 16)],
    [3, "Desk Chair", "Furniture", 4, Decimal("310.75"), date(2026, 2, 1)],
    [4, "Monitor", "Electronics", 3, Decimal("450.00"), date(2026, 2, 3)],
    [5, "Bookshelf", "Furniture", 1, Decimal("180.25"), date(2026, 2, 10)],
]

summary = client.insert("demo.sales", rows, column_names=columns)
print(f"\nCREATE: inserted {summary.written_rows} rows")


# --------------------------------------------------------------- READ ------
result = client.query("SELECT id, product, category, quantity, price, sale_date FROM demo.sales ORDER BY id")
show("READ: all rows", result.result_rows)

# Filtered read with server-side parameters (safe against injection).
result = client.query(
    """
    SELECT id, product, quantity, price
    FROM demo.sales
    WHERE category = {cat:String} AND price > {min_price:Decimal(10, 2)}
    ORDER BY price DESC
    """,
    parameters={"cat": "Electronics", "min_price": Decimal("100.00")},
)
show("READ: Electronics over 100", result.result_rows)

# Aggregation.
result = client.query("""
    SELECT category, count() AS orders, sum(quantity * price) AS revenue
    FROM demo.sales
    GROUP BY category
    ORDER BY revenue DESC
""")
show("READ: revenue by category", result.result_rows)


# ------------------------------------------------------------- UPDATE ------
client.command(
    """
    ALTER TABLE demo.sales
    UPDATE quantity = {qty:UInt32}, price = {price:Decimal(10, 2)}
    WHERE id = {id:UInt32}
    """,
    parameters={"qty": 5, "price": Decimal("1150.00"), "id": 1},
    settings=MUTATION_SETTINGS,
)
print("\nUPDATE: id=1 quantity -> 5, price -> 1150.00")

# Bulk update across matching rows.
client.command(
    "ALTER TABLE demo.sales UPDATE price = round(price * 0.9, 2) WHERE category = {cat:String}",
    parameters={"cat": "Furniture"},
    settings=MUTATION_SETTINGS,
)
print("UPDATE: 10% discount on Furniture")

result = client.query("SELECT id, product, category, quantity, price FROM demo.sales ORDER BY id")
show("READ: after update", result.result_rows)


# ------------------------------------------------------------- DELETE ------
client.command(
    "DELETE FROM demo.sales WHERE id = {id:UInt32}",
    parameters={"id": 2},
    settings=DELETE_SETTINGS,
)
print("\nDELETE: removed id=2")

client.command(
    "DELETE FROM demo.sales WHERE quantity < {qty:UInt32}",
    parameters={"qty": 2},
    settings=DELETE_SETTINGS,
)
print("DELETE: removed rows with quantity < 2")

result = client.query("SELECT id, product, category, quantity, price FROM demo.sales ORDER BY id")
show("READ: after delete", result.result_rows)

count = client.command("SELECT count() FROM demo.sales")
print(f"\nRemaining rows: {count}")

client.close()

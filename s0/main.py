import clickhouse_connect

client = clickhouse_connect.get_client(
    host="localhost",
    port=8123,
    username="nazmul",
    password="testPass123",
)

result = client.query("SELECT version()")
print("Connected!")
print("ClickHouse version:", result.result_rows[0][0])
result = client.query("SELECT 1")
print("Query result:", result.result_rows[0][0])


client.command("""
    CREATE DATABASE IF NOT EXISTS demo
""")

print("Database created!")

query = client.query("""
SHOW DATABASES;
""")

print("Databases:", [row[0] for row in query.result_rows])
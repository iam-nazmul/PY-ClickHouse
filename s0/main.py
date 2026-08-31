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
হ্যাঁ। একদম fresh ClickHouse container `nazmul / testPass123` দিয়ে চালাতে পারেন।

### 1. পুরনো `clickhouse` container থাকলে remove করুন

```bash
docker rm -f clickhouse 2>/dev/null || true
```

### 2. ClickHouse container চালান

```bash
docker run -d \
  --name clickhouse \
  -p 8123:8123 \
  -p 9000:9000 \
  -e CLICKHOUSE_USER=nazmul \
  -e CLICKHOUSE_PASSWORD=testPass123 \
  -e CLICKHOUSE_DEFAULT_ACCESS_MANAGEMENT=1 \
  clickhouse/clickhouse-server:latest
```

এখানে:

```text
Username: nazmul
Password: testPass123
HTTP:     localhost:8123
Native:   localhost:9000
```

### 3. Container status check

```bash
docker ps
```

তারপর logs:

```bash
docker logs clickhouse
```

---

## 4. ClickHouse client দিয়ে test

```bash
docker exec -it clickhouse clickhouse-client \
  --user nazmul \
  --password
```

Password চাইলে:

```text
testPass123
```

তারপর:

```sql
SELECT 1;
```

Expected:

```text
┌─1─┐
│ 1 │
└───┘
```

---

## 5. HTTP connection test

Host Ubuntu থেকে:

```bash
curl -u nazmul:testPass123 \
  "http://localhost:8123/?query=SELECT%201"
```

Expected:

```text
1
```

---

## 6. Python connection

আপনার `main.py`:

```python
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
```

Run:

```bash
python main.py
```

Expected:

```text
Connected!
ClickHouse version: 26.x.x.x
```

### গুরুত্বপূর্ণ

Development-এর জন্য `testPass123` ঠিক আছে। Production-এ password সরাসরি Python code বা Docker command history-তে রাখা উচিত নয়; `.env`/Docker secrets ব্যবহার করবেন।

আর যদি data persist করতে চান, পরেরবার আমরা **Docker volume সহ ClickHouse setup** করব, যাতে `docker rm` করলেও database data হারিয়ে না যায়।

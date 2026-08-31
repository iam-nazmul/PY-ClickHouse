সব Docker container মুছে ফেলতে চাইলে:

### 1. সব container stop করুন

```bash
docker stop $(docker ps -aq)
```

### 2. সব container remove করুন

```bash
docker rm $(docker ps -aq)
```

### এক command-এ

```bash
docker rm -f $(docker ps -aq)
```

এটি **running + stopped সব container** forcefully remove করবে।

### Verify

```bash
docker ps -a
```

যদি কোনো container না থাকে, দেখাবে:

```text
CONTAINER ID   IMAGE   COMMAND   CREATED   STATUS   PORTS   NAMES
```

**নোট:** এগুলো container মুছবে, কিন্তু Docker images এবং volumes মুছবে না।

যদি **containers + images + volumes + networks সবকিছু পরিষ্কার করে একদম fresh Docker environment** চান, সেটা আলাদা command—বললে সেটাও দেব।

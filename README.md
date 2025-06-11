# 🧠 Process Insight Ingestion Pipeline

This project provides a lightweight ingestion service for collecting, processing, and storing raw OS process data (e.g., from `ps auxww` or `tasklist`) to support researcher queries like:

> “What is the most commonly used application by law students on Windows?”

---

## 🧱 Architecture Overview

### 🗃 Components:
- **Uploader Service (FastAPI)**  
  Accepts raw command output + metadata via HTTP, then publishes to RabbitMQ.

- **RabbitMQ**  
  Buffers ingestion traffic using the `pre_normalise` exchange and `raw_process_input` queue.

- **Consumer Service**  
  Listens to `raw_process_input`, stores raw process data in PostgreSQL.

- **Normalizer**  
  Will process raw text into normalized structured format for querying.

---

## 🚀 Quick Start

### 📦 Prerequisites

- Docker & Docker Compose
- Python 3.10+ (for local dev)
- docker compose 3.4+

---

### 🐳 Run the full system

```bash
docker-compose up --build
```

Visit:
- API: [http://localhost:8000/docs](http://localhost:8000/docs)  
- RabbitMQ UI: [http://localhost:15672](http://localhost:15672)  
  (Login: `guest` / `guest`)

---

### 📤 Upload a process snapshot

```bash
curl -X POST http://localhost:8000/ingest/ \
  -F "timestamp=2025-06-10 22:01:00.000000" \
  -F "os=linux" \
  -F "command=ps auxww" \
  -F "machine_id=my-machine-01" \
  -F "machine_name=Dev Laptop" \
  -F "extra={\"location\": \"labA\", \"owner\": \"research\"}" \
  -F "file=@sample_output.txt"
```

---

## 🗄 Database Schema

- **raw_process_data**  
  Stores the raw process output with metadata.

- **normalized_process_data** *(planned)*  
  Will contain parsed data: process name, PID, user, etc.

- **extra_ps_data**, **extra_tasklist_data**  
  Hold OS-specific extra columns connected via foreign key.

---

## 🔐 Credentials

| Service   | Username | Password |
|-----------|----------|----------|
| RabbitMQ  | `guest`  | `guest`  |
| PostgreSQL| `postgres` | `postgres` |

---

## 🧪 Testing

You can use Postman or `curl` to test the `/ingest/` API.


---


## 📜 License

MIT License

---

## 👥 Contributors

- Yogev Shachar

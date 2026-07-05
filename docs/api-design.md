# REST API Design

Personal Data Lakehouse 的 API 服务，用于对外提供数据访问。

---

## 1. Overview

| 属性 | 值 |
|------|-----|
| Base URL | `http://localhost:8000/api/v1` |
| Protocol | HTTP/1.1, HTTP/2 |
| Auth | API Key (Header: `X-API-Key`) |
| Format | JSON |
| Rate Limit | 100 req/min (可配置) |

---

## 2. Authentication

### 2.1 API Key

所有请求需要携带 API Key：

```bash
curl -H "X-API-Key: your-api-key" \
     http://localhost:8000/api/v1/tables
```

### 2.2 Response Headers

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1704067200
```

---

## 3. Endpoints

### 3.1 Health Check

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | 服务健康检查 |

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime_seconds": 3600,
  "services": {
    "trino": "healthy",
    "gravitino": "healthy",
    "minio": "healthy"
  }
}
```

---

### 3.2 Catalog

#### List Tables

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tables` | 列出所有表 |

**Query Parameters:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| layer | string | all | 过滤层级 (bronze/silver/gold) |
| source | string | - | 过滤数据源 (youtube/chrome/github) |
| limit | int | 50 | 返回数量 |
| offset | int | 0 | 偏移量 |

**Example:**
```bash
GET /api/v1/tables?layer=silver&source=youtube&limit=10
```

**Response:**
```json
{
  "tables": [
    {
      "name": "silver_youtube_watches",
      "layer": "silver",
      "source": "youtube",
      "row_count": 15000,
      "size_bytes": 52428800,
      "last_updated": "2024-01-15T10:30:00Z",
      "partition_columns": ["watch_year", "watch_month"]
    }
  ],
  "total": 15,
  "limit": 10,
  "offset": 0
}
```

#### Get Table Schema

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tables/{table_name}/schema` | 获取表结构 |

**Response:**
```json
{
  "table_name": "silver_youtube_watches",
  "columns": [
    {
      "name": "video_id",
      "type": "string",
      "nullable": false,
      "description": "视频唯一ID"
    },
    {
      "name": "video_title",
      "type": "string",
      "nullable": false,
      "description": "视频标题"
    },
    {
      "name": "watch_timestamp",
      "type": "timestamp",
      "nullable": false,
      "description": "观看时间"
    }
  ],
  "partition_columns": ["watch_year", "watch_month"]
}
```

---

### 3.3 Data Query

#### Query Table Data

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tables/{table_name}/data` | 查询表数据 |

**Query Parameters:**

| Param | Type | Description |
|-------|------|-------------|
| columns | string | 选择的列 (逗号分隔) |
| where | string | WHERE 条件 (URL encoded) |
| order_by | string | 排序字段 |
| order | string | 排序方向 (asc/desc) |
| limit | int | 返回数量 (默认100, 最大1000) |
| offset | int | 偏移量 |

**Example:**
```bash
GET "/api/v1/tables/silver_youtube_watches/data?where=watch_date='2024-01-15'&order_by=watch_timestamp&order=desc&limit=10"
```

**Response:**
```json
{
  "table_name": "silver_youtube_watches",
  "columns": ["video_id", "video_title", "watch_timestamp"],
  "rows": [
    {
      "video_id": "dQw4w9WgXcQ",
      "video_title": "Never Gonna Give You Up",
      "watch_timestamp": "2024-01-15T23:45:00Z"
    }
  ],
  "row_count": 10,
  "total_matching": 150
}
```

#### Execute Raw SQL

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/query` | 执行 SQL 查询 |

**Request:**
```json
{
  "sql": "SELECT date_trunc('month', watch_date) as month, COUNT(*) as cnt FROM silver_youtube_watches GROUP BY 1 ORDER BY 1",
  "limit": 100
}
```

**Response:**
```json
{
  "columns": ["month", "cnt"],
  "rows": [
    {"month": "2024-01-01", "cnt": 500},
    {"month": "2024-02-01", "cnt": 650}
  ],
  "row_count": 2,
  "execution_time_ms": 250
}
```

---

### 3.4 Time Travel

#### List Snapshots

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tables/{table_name}/snapshots` | 列出表的所有快照 |

**Response:**
```json
{
  "table_name": "silver_youtube_watches",
  "snapshots": [
    {
      "snapshot_id": 1234567890000,
      "timestamp": "2024-01-15T10:30:00Z",
      "operation": "append",
      "added_files": 5,
      "deleted_files": 0
    },
    {
      "snapshot_id": 1234567890001,
      "timestamp": "2024-01-16T10:30:00Z",
      "operation": "overwrite",
      "added_files": 10,
      "deleted_files": 5
    }
  ]
}
```

#### Query Historical Data

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tables/{table_name}/history` | 查询历史版本数据 |

**Query Parameters:**

| Param | Type | Description |
|-------|------|-------------|
| version | string | 版本号 (timestamp 或 snapshot_id) |
| as_of | string | 时间点 (如 "2024-01-15 10:00:00") |

**Example:**
```bash
GET /api/v1/tables/silver_youtube_watches/history?as_of=2024-01-15T10:00:00
```

---

### 3.5 Statistics

#### Get Table Statistics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tables/{table_name}/stats` | 获取表统计信息 |

**Response:**
```json
{
  "table_name": "silver_youtube_watches",
  "row_count": 15000,
  "size_bytes": 52428800,
  "file_count": 45,
  "last_updated": "2024-01-15T10:30:00Z",
  "partitions": [
    {
      "year": 2024,
      "month": 1,
      "row_count": 5000,
      "size_bytes": 17400000
    }
  ],
  "column_stats": [
    {
      "column": "video_id",
      "null_count": 0,
      "unique_count": 4500
    }
  ]
}
```

#### Get Dashboard Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/dashboard/summary` | 获取仪表盘汇总 |

**Response:**
```json
{
  "date": "2024-01-15",
  "youtube": {
    "watches_today": 45,
    "watches_this_month": 1200,
    "top_channel": "Tech Reviewer"
  },
  "github": {
    "commits_today": 5,
    "commits_this_month": 85,
    "active_repos": 3
  },
  "social": {
    "weibo_top": "某明星结婚",
    "twitter_top": "#AI"
  },
  "stocks": {
    "portfolio_value": 150000,
    "daily_change": 2.5
  }
}
```

---

### 3.6 Data Sources

#### List Available Sources

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/sources` | 列出所有数据源 |

**Response:**
```json
{
  "sources": [
    {
      "name": "youtube",
      "type": "batch (takeout)",
      "update_frequency": "weekly",
      "last_updated": "2024-01-15T10:00:00Z"
    },
    {
      "name": "github",
      "type": "stream (webhook)",
      "update_frequency": "realtime",
      "last_updated": "2024-01-15T23:59:00Z"
    },
    {
      "name": "stock",
      "type": "stream (api)",
      "update_frequency": "5min",
      "last_updated": "2024-01-15T15:00:00Z"
    }
  ]
}
```

---

## 4. Error Handling

### 4.1 Error Response Format

```json
{
  "error": {
    "code": "INVALID_PARAMETER",
    "message": "Invalid limit value: must be between 1 and 1000",
    "details": {
      "field": "limit",
      "value": "5000"
    }
  }
}
```

### 4.2 HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request (参数错误) |
| 401 | Unauthorized (API Key 无效) |
| 403 | Forbidden (权限不足) |
| 404 | Not Found (表/资源不存在) |
| 429 | Too Many Requests (限流) |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

### 4.3 Error Codes

| Code | Description |
|------|-------------|
| `INVALID_PARAMETER` | 参数无效 |
| `TABLE_NOT_FOUND` | 表不存在 |
| `SNAPSHOT_NOT_FOUND` | 快照不存在 |
| `SQL_EXECUTION_ERROR` | SQL 执行错误 |
| `RATE_LIMIT_EXCEEDED` | 超出限流 |
| `AUTHENTICATION_FAILED` | 认证失败 |
| `PERMISSION_DENIED` | 权限拒绝 |

---

## 5. Implementation

### 5.1 Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | FastAPI |
| Query Engine | Trino (via TrinoDB Python client) |
| Metadata | Gravitino REST API |

### 5.2 Project Structure

```
src/api/
├── main.py                 # FastAPI app entry
├── config.py               # Configuration
├── auth.py                 # API Key 认证
├── routers/
│   ├── health.py           # Health check endpoints
│   ├── catalog.py          # Table/Schema endpoints
│   ├── query.py            # Data query endpoints
│   ├── time_travel.py      # Snapshot endpoints
│   └── dashboard.py        # Dashboard endpoints
├── services/
│   ├── trino_client.py     # Trino connection
│   ├── gravitino_client.py # Gravitino client
│   └── query_builder.py    # SQL builder
└── models/
    ├── schemas.py          # Pydantic models
    └── errors.py           # Error models
```

### 5.3 Quick Start

```python
# src/api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import health, catalog, query, time_travel, dashboard
from auth import api_key_auth

app = FastAPI(
    title="Personal Lakehouse API",
    version="1.0.0",
    description="REST API for Personal Data Lakehouse"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
)

app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(catalog.router, prefix="/api/v1", tags=["Catalog"])
app.include_router(query.router, prefix="/api/v1", tags=["Query"])
app.include_router(time_travel.router, prefix="/api/v1", tags=["Time Travel"])
app.include_router(dashboard.router, prefix="/api/v1", tags=["Dashboard"])
```

---

## 6. Clients

### 6.1 Python Client

```python
from lakehouse_client import LakehouseClient

client = LakehouseClient(
    base_url="http://localhost:8000",
    api_key="your-api-key"
)

# Query table
df = client.query_table(
    "silver_youtube_watches",
    where="watch_date = '2024-01-15'",
    limit=100
)

# Execute SQL
result = client.execute_sql("SELECT * FROM gold_dashboard LIMIT 10")
```

### 6.2 JavaScript/TypeScript Client

```typescript
import { LakehouseClient } from '@lakehouse/client';

const client = new LakehouseClient({
  baseUrl: 'http://localhost:8000',
  apiKey: 'your-api-key'
});

const data = await client.queryTable('silver_youtube_watches', {
  where: "watch_date = '2024-01-15'",
  limit: 100
});
```

---

## 7. Rate Limiting

| Plan | Requests/min | Burst | Daily |
|------|-------------|-------|-------|
| Free | 100 | 20 | 10,000 |
| Pro | 1000 | 200 | 100,000 |
| Enterprise | Unlimited | Unlimited | Unlimited |

---

*Generated: 2025-06-07*
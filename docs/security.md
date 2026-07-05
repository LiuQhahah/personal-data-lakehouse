# Security & Access Control

Personal Data Lakehouse 的安全架构设计。

---

## 1. Overview

| Aspect | Implementation |
|--------|---------------|
| Authentication | API Key (External), OAuth (Internal) |
| Authorization | RBAC (Role-Based Access Control) |
| Encryption | TLS/SSL for all connections |
| Storage | MinIO with encryption at rest |
| Network | Docker network isolation |

---

## 2. Authentication

### 2.1 External API Access

**API Key Authentication**

```bash
# 所有 API 请求需要携带 API Key
curl -H "X-API-Key: lk_live_xxxxxxxxxxxx" \
     http://localhost:8000/api/v1/tables
```

**API Key Format**
```
lk_live_<32_char_random>
lk_test_<32_char_random>
```

### 2.2 API Key Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/keys` | GET | 列出所有 API Keys |
| `/auth/keys` | POST | 创建新 API Key |
| `/auth/keys/{key_id}` | DELETE | 撤销 API Key |

**Create API Key:**
```bash
POST /api/v1/auth/keys
Content-Type: application/json

{
  "name": "My App",
  "scopes": ["read:tables", "read:data"],
  "expires_in_days": 90
}
```

**Response:**
```json
{
  "key_id": "key_abc123",
  "key": "lk_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "name": "My App",
  "scopes": ["read:tables", "read:data"],
  "created_at": "2024-01-15T10:00:00Z",
  "expires_at": "2024-04-15T10:00:00Z"
}
```

> ⚠️ **重要**: Key 只在创建时返回一次，之后无法查看。请妥善保存！

---

## 3. Authorization

### 3.1 Role-Based Access Control (RBAC)

```
┌─────────────────────────────────────────────────────────────────┐
│                         ROLES                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌────────────┐                                                │
│   │  Admin     │  全部权限: 读写所有表, 管理用户, 管理API Key    │
│   └────────────┘                                                │
│                                                                  │
│   ┌────────────┐                                                │
│   │  Analyst   │  读权限: 所有表, 执行 SQL                      │
│   └────────────┘                                                │
│                                                                  │
│   ┌────────────┐                                                │
│   │  Viewer    │  只读: Gold 层表, 仪表盘                       │
│   └────────────┘                                                │
│                                                                  │
│   ┌────────────┐                                                │
│   │  Pipeline  │  写权限: 数据摄入, 执行 ETL                    │
│   └────────────┘                                                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Permission Matrix

| Resource | Admin | Analyst | Viewer | Pipeline |
|----------|-------|---------|--------|----------|
| **Catalog** |
| List tables | ✓ | ✓ | ✓ | ✓ |
| View schema | ✓ | ✓ | ✓ | - |
| **Data - Bronze** |
| Read | ✓ | ✓ | - | ✓ |
| Write | ✓ | - | - | ✓ |
| **Data - Silver** |
| Read | ✓ | ✓ | - | ✓ |
| Write | ✓ | - | - | ✓ |
| **Data - Gold** |
| Read | ✓ | ✓ | ✓ | ✓ |
| Write | ✓ | - | - | ✓ |
| **API Keys** |
| Manage | ✓ | - | - | - |
| **Users** |
| Manage | ✓ | - | - | - |

### 3.3 Scope Definitions

| Scope | Description |
|-------|-------------|
| `read:tables` | 列出和查看表结构 |
| `read:data:*` | 读取所有层的数据 |
| `read:data:gold` | 只读 Gold 层 |
| `write:data` | 写入数据（ETL 用） |
| `execute:sql` | 执行自定义 SQL |
| `admin:*` | 管理员权限 |

---

## 4. Network Security

### 4.1 Docker Network Isolation

```yaml
# docker-compose.yml
networks:
  lakehouse:
    driver: bridge
    ipam:
      config:
        - subnet: 172.28.0.0/16

services:
  api:
    networks:
      - lakehouse
    ports:
      - "8000:8000"  # 只暴露 API

  spark:
    networks:
      - lakehouse
    # 不暴露端口，内部使用

  trino:
    networks:
      - lakehouse
    # 只通过 API 访问
```

### 4.2 Service Communication

```
┌─────────────────────────────────────────────────────────────────┐
│                      EXTERNAL (HTTPS/TLS)                       │
│                   browser / app / curl                          │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         API Gateway                              │
│                   (FastAPI + TLS terminated)                    │
│                                                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Auth Layer   │  │ Rate Limit   │  │ Audit Log    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    INTERNAL (Docker Network)                    │
│                                                                 │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    │
│   │  API    │───▶│ Trino   │───▶│ Gravitino│───│ MinIO   │    │
│   └─────────┘    └─────────┘    └───────���─┘    └─────────┘    │
│        │                                                   │    │
│        │    ┌─────────┐    ┌─────────┐                     │    │
│        └───▶│ Spark   │───▶│ Iceberg │─────────────────────┘    │
│             └─────────┘    └─────────┘                             │
│                  │                                                   │
│                  ▼                                                   │
│             ┌─────────┐                                             │
│             │ Redpanda │◀── Flink                                   │
│             └─────────┘                                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. Data Encryption

### 5.1 In-Transit (TLS)

所有外部通信使用 TLS 1.3：

```yaml
# MinIO TLS 配置
minio:
  command: server /data --console-address ":9001"
  environment:
    MINIO_SERVER_TLS_KEY: /certs/private.key
    MINIO_SERVER_TLS_CERTIFICATE: /certs/public.crt
```

### 5.2 At-Rest (Encryption)

MinIO 启用默认加密：

```yaml
minio:
  environment:
    MINIO_KMS_KES_KEY_NAME: lakehouse-master-key
    MINIO_KMS_KES_ENDPOINT: https://kes:7373
    MINIO_KMS_KES_KEY_FILE: /config/kes-config.yaml
```

### 5.3 Column-Level Encryption

敏感数据可在 Silver 层加密：

```sql
-- 示例：对敏感字段加密
CREATE TABLE silver_user_data (
    user_id STRING,
    email STRING ENCRYPTED,  -- E2E 加密
    phone STRING ENCRYPTED,
    ...
);
```

---

## 6. Audit Logging

### 6.1 Audit Events

| Event Type | Logged Fields |
|------------|---------------|
| API Request | timestamp, user_id, api_key_id, endpoint, method |
| Query Execution | timestamp, user_id, sql, duration |
| Data Access | timestamp, user_id, table, columns |
| Authentication | timestamp, api_key_id, status |
| Admin Action | timestamp, user_id, action |

### 6.2 Audit Log Storage

```
Iceberg Table: audit_logs
┌─────────────┬───────────┬──────────┬───────────────┐
│ timestamp   │ user_id   │ action   │ details       │
│ TIMESTAMP   │ STRING    │ STRING   │ STRING (JSON) │
├─────────────┴───────────┴──────────┴───────────────┤
│ Partitioned by: day (timestamp)                    │
└────────────────────────────────────────────────────┘
```

### 6.3 Query Audit Logs

```bash
# 查看特定用户的操作
SELECT * FROM audit_logs
WHERE user_id = 'user_123'
  AND timestamp > current_timestamp - interval '7' day;

# 查看数据访问
SELECT * FROM audit_logs
WHERE action = 'READ_DATA'
  AND details:table = 'silver_chrome_history';
```

---

## 7. User Management

### 7.1 Internal Users

| User Type | Description |
|-----------|-------------|
| `owner` | 账户所有者，所有权限 |
| `family` | 家庭成员，只读 Gold 层 |
| `pipeline` | 数据管道专用服务账户 |

### 7.2 User CRUD

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/users` | GET | 列出用户 |
| `/auth/users` | POST | 创建用户 |
| `/auth/users/{id}` | PATCH | 更新用户 |
| `/auth/users/{id}` | DELETE | 删除用户 |

---

## 8. Security Configuration

### 8.1 Environment Variables

```bash
# .env 文件

# API Security
API_BASE_URL=http://localhost:8000
API_KEY_HEADER=X-API-Key

# TLS Certificates
TLS_CERT_PATH=/path/to/cert.pem
TLS_KEY_PATH=/path/to/key.pem

# Gravitino
GRAVITINO_AUTH=true
GRAVITINO_SSL=true

# MinIO
MINIO_TLS_ENABLED=true
MINIO_KMS_ENABLED=true
```

### 8.2 Security Checklist

| Item | Status | Implementation |
|------|--------|----------------|
| API TLS | ✅ | Nginx reverse proxy with TLS |
| Internal TLS | ✅ | Docker network mTLS (可选) |
| API Key Rotation | ✅ | 90天过期，可手动撤销 |
| RBAC | ✅ | 基于角色的权限控制 |
| Audit Logging | ✅ | 所有操作记录到 Iceberg |
| Rate Limiting | ✅ | 每分钟 100 请求 |
| SQL Injection | ✅ | 参数化查询 |
| Secrets Management | ✅ | Docker secrets / Vault |

---

## 9. Compliance

### 9.1 个人数据保护

| Data Type | Protection Level | Action |
|-----------|-----------------|--------|
| 股票持仓 | 高 | 加密存储 |
| 浏览器历史 | 高 | 加密存储 |
| 观看历史 | 中 | 访问控制 |
| GitHub 公开数据 | 低 | 标准访问 |

### 9.2 Data Retention

| Data Type | Retention | Reason |
|-----------|-----------|--------|
| 原始数据 (Bronze) | 永久 | 审计需求 |
| 清洗数据 (Silver) | 3年 | 分析需求 |
| 聚合数据 (Gold) | 永久 | 业务价值 |
| 审计日志 | 1年 | 合规要求 |

---

## 10. Incident Response

### 10.1 Security Events

| Event | Severity | Response |
|-------|----------|----------|
| Invalid API Key | Low | 记录日志，禁用 key |
| Failed Login (3次) | Medium | 临时锁定 15 分钟 |
| Suspicious Query | Medium | 审查 + 管理员告警 |
| Data Breach | Critical | 立即禁用所有 key，通知用户 |

### 10.2 Emergency Access

```bash
# 紧急情况下禁用所有 API
curl -X POST http://localhost:8000/api/v1/admin/lockdown

# 恢复访问
curl -X POST http://localhost:8000/api/v1/admin/unlock
```

---

*Generated: 2025-06-07*
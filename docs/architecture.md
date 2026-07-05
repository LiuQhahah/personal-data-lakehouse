# Personal Data Lakehouse Architecture

## 1. Overview

**Project**: Personal Data Lakehouse - 构建个人数据的现代化数据平台

**Goal**: 将个人在互联网平台产生的数据（GitHub, YouTube, Chrome等）统一采集、存储、分析，形成个人数字画像

**Principles** (来自《Practical Lakehouse Architecture》):
- Single Source of Truth: 所有数据进入 Lakehouse，不再有数据孤岛
- Schema-on-read: 原始数据先入湖，schema 变化也能hold住
- ACID Transaction: 保证数据一致性
- Time Travel: 任意版本回溯

---

## 2. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            PERSONAL DATA LAKEHOUSE                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────┐     ┌────────────────────────────────────┐   │
│  │        DATA SOURCES         │     │         PROCESSING LAYER           │   │
│  │                             │     │                                    │   │
│  │  ┌─────────────────────┐    │     │  ┌──────────────┐ ┌─────────────┐  │   │
│  │  │ BATCH               │    │     │  │ Spark        │ │ Flink       │  │   │
│  │  │ ──────────────────  │    │     │  │ (Batch ETL)  │ │ (Stream)    │  │   │
│  │  │ • Google Takeout    │────┼────▶│  │              │ │             │  │   │
│  │  │   - YouTube History │    │     │  │              │ │             │  │   │
│  │  │   - Chrome History  │    │     │  └──────────────┘ └─────────────┘  │   │
│  │  │ • Local Files       │    │     │                                      │   │
│  │  └─────────────────────┘    │     │  ┌──────────────┐ ┌─────────────┐  │   │
│  │                             │     │  │ Python       │ │ Trino       │  │   │
│  │  ┌─────────────────────┐    │     │  │ (Scripts)    │ │ (SQL Query) │  │   │
│  │  │ STREAM              │    │     │  │              │ │             │  │   │
│  │  │ ──────────────────  │    │     │  └──────────────┘ └─────────────┘  │   │
│  │  │ • GitHub Webhook    │────┼────▶│                                      │   │
│  │  │ • (Future) RSS      │    │     │                                      │   │
│  │  │ • (Future) Twitter  │    │     │                                      │   │
│  │  └─────────────────────┘    │     │                                      │   │
│  └─────────────────────────────┘     └────────────────────────────────────┘   │
│                                        │                                        │
│                                        ▼                                        │
├─────────────────────────────────────────────────────────────────────────────────┤
│                              STORAGE LAYER (Iceberg)                            │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  warehouse/                                                              │   │
│  │  ├── bronze/          # Raw: 原始数据，未经清洗                          │   │
│  │  │   ├── youtube_watch_history/                                        │   │
│  │  │   │   ├── data_file_001.parquet                                     │   │
│  │  │   │   └── manifest...                                               │   │
│  │  │   ├── chrome_history/                                               │   │
│  │  │   └── github_events/                                                │   │
│  │  │                                                                     │   │
│  │  ├── silver/          # Cleaned: 清洗、结构化、已去重                   │   │
│  │  │   ├── youtube_watch_history_cleaned/                               │   │
│  │  │   ├── chrome_history_cleaned/                                       │   │
│  │  │   └── github_events_cleaned/                                        │   │
│  │  │                                                                     │   │
│  │  └── gold/            # Aggregated: 业务指标、报表                      │   │
│  │      ├── youtube_insights/        # 如：每月观看时长TOP10               │   │
│  │      ├── chrome_insights/         # 如：常访问网站统计                  │   │
│  │      ├── github_insights/         # 如：每月贡献统计                   │   │
│  │      └── personal_dashboard/      # 综合仪表盘                         │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  CATALOG (Gravitino)                                                  │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              CONSUMPTION LAYER                                  │
│                                                                                 │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐            │
│  │  Jupyter Notebook│  │  Trino/Presto    │  │  REST API        │            │
│  │  (EDA, Analysis) │  │  (SQL Query)     │  │  (App Backend)   │            │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘            │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Data Sources

### 3.1 Batch Data Sources

| Source | Data Type | Format | Frequency | Volume |
|--------|-----------|--------|-----------|--------|
| Google Takeout - YouTube | Watch History | JSON | Weekly | ~MB |
| Google Takeout - Chrome | Browsing History | JSON/HTML | Weekly | ~MB |
| Local Files | Backup, Exports | CSV/JSON | On-demand | - |

### 3.2 Stream Data Sources

| Source | Event Type | Transport | Latency |
|--------|------------|-----------|---------|
| GitHub | Push, PR, Issue, Star | Webhook → Kafka | ~seconds |
| (Future) RSS Feed | New Articles | Poller | ~minutes |
| (Future) Twitter | Tweets | API v2 | ~seconds |

---

## 4. Technology Stack

| Layer | Technology | Version | Justification |
|-------|------------|---------|---------------|
| **Compute** | Apache Spark | 3.5.x | 批处理 ETL 标准 |
| **Stream** | Apache Flink | 1.18.x | 流处理高性能 |
| **Table Format** | Apache Iceberg | 1.5.x | ACID, Time travel, Schema evolution |
| **Catalog** | Apache Gravitino | 1.2.x | 统一元数据平台，支持 Iceberg REST |
| **Storage** | MinIO (local S3) | latest | S3 协议兼容，Docker 部署 |
| **Message Queue** | Redpanda | 23.3.x | Kafka 兼容，更轻量 |
| **Query Engine** | Trino | 427.x | SQL on Lakehouse |
| **Orchestration** | Apache Airflow | 2.9.x | 批处理调度 |
| **Webhook Server** | Flask/FastAPI | - | GitHub Webhook 接收 |
| **Logging** | Loki + Promtail | 2.9.x | 日志收集，轻量替代 ELK |
| **Notebook** | JupyterLab | latest | 交互式分析 |
| **Visualization** | Apache Superset | latest | BI 仪表盘 |

---

## 5. Data Model

### 5.1 Bronze Layer (Raw)

保持原始数据格式，只做基本解析。

```python
# YouTube Watch History
bronze.youtube_watches:
  - header: str           # "YouTube"
  - title: str            # 视频标题
  - titleUrl: str         # 视频URL
  - time: str             # ISO 8601 时间
  - subtitles: list       # 频道信息
  - details: list         # 额外详情
  - imports: list         # 导入来源
  - ...                   # 原始字段全部保留

# Chrome History (从 JSON 导出)
bronze.chrome_history:
  - browser_name: str
  - datetime: str
  - url: str
  - title: str
  - ...

# GitHub Events (GitHub API)
bronze.github_events:
  - id: str               # Event ID
  - type: str             # PushEvent, PullRequestEvent...
  - actor: dict           # 用户信息
  - repo: dict            # 仓库信息
  - payload: dict         # 事件详情
  - created_at: str
  - ...
```

### 5.2 Silver Layer (Cleaned)

标准化、清洗、去重、分区。

```sql
-- Silver: YouTube Watches (清洗后)
CREATE TABLE silver.youtube_watches (
    video_id STRING,
    video_title STRING,
    channel_id STRING,
    channel_name STRING,
    watch_timestamp TIMESTAMP,
    watch_date DATE,
    watch_hour INT,
    watch_month STRING,
    watch_year INT,
    url STRING,
    _ingest_time TIMESTAMP,
    _source_file STRING,
    _batch_id STRING
) PARTITIONED BY (year(watch_timestamp), month(watch_timestamp));

-- Silver: Chrome History (清洗后)
CREATE TABLE silver.chrome_history (
    url STRING,
    domain STRING,
    title STRING,
    visit_time TIMESTAMP,
    visit_date DATE,
    visit_hour INT,
    visit_month STRING,
    visit_year INT,
    visit_count INT DEFAULT 1,
    _ingest_time TIMESTAMP,
    _source_file STRING,
    _batch_id STRING
) PARTITIONED BY (year(visit_time), month(visit_time));

-- Silver: GitHub Events (清洗后)
CREATE TABLE silver.github_events (
    event_id STRING,
    event_type STRING,
    actor_login STRING,
    actor_id BIGINT,
    repo_name STRING,
    repo_id BIGINT,
    action STRING,           -- created, opened, closed, etc.
    created_at TIMESTAMP,
    created_date DATE,
    payload_json STRING,
    _ingest_time TIMESTAMP,
    _batch_id STRING
) PARTITIONED BY (year(created_at), month(created_at));
```

### 5.3 Gold Layer (Aggregated)

业务指标层。

```sql
-- Gold: YouTube 每月观看统计
CREATE TABLE gold.youtube_monthly_stats (
    year_month STRING,
    total_watches INT,
    unique_videos INT,
    unique_channels INT,
    top_10_channels ARRAY<STRUCT<channel: STRING, views: INT>>,
    total_watch_hours DOUBLE,
    _computed_at TIMESTAMP
);

-- Gold: Chrome 每月网站统计
CREATE TABLE gold.chrome_monthly_stats (
    year_month STRING,
    total_visits INT,
    unique_domains INT,
    top_20_domains ARRAY<STRUCT<domain: STRING, visits: INT>>,
    most_active_hour INT,
    _computed_at TIMESTAMP
);

-- Gold: GitHub 每月贡献统计
CREATE TABLE gold.github_monthly_stats (
    year_month STRING,
    total_commits INT,
    total_prs INT,
    total_issues INT,
    repos_contributed ARRAY<STRING>,
    active_days INT,
    _computed_at TIMESTAMP
);
```

---

## 6. Pipeline Design

### 6.1 Batch Pipeline

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ 1. Download │───▶│ 2. Extract  │───▶│ 3. Transform│───▶│ 4. Load     │
│ Takeout     │    │ Parse JSON  │    │ Clean/Dedup │    │ to Iceberg  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
      │                                      │                   │
      ▼                                      ▼                   ▼
┌─────────────┐                       ┌───────────┐      ┌─────────────┐
│ Manual/     │                       │ Quality   │      │ Time Travel│
│ Cron Job    │                       │ Checks    │      │ Enabled    │
└─────────────┘                       └───────────┘      └─────────────┘
     │                                        │                   │
     └────────────────────────────────────────┴───────────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │   Airflow DAG Schedule  │
                    │   - Weekly: Takeout     │
                    │   - Daily: Silver→Gold  │
                    └─────────────────────────┘
```

### 6.2 Stream Pipeline

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ GitHub      │───▶│ Webhook     │───▶│  Kafka      │
│ Events      │    │ Server      │    │  Topic      │
└─────────────┘    └─────────────┘    └─────────────┘
                                               │
                                               ▼
                    ┌─────────────────────────────────────────┐
                    │  Flink (Streaming ETL)                  │
                    │  - Parse JSON                           │
                    │  - Deduplicate by event_id              │
                    │  - Enrich (lookup actor info)           │
                    │  - Write to Iceberg (append mode)       │
                    └─────────────────────────────────────────┘
                                               │
                                               ▼
                    ┌─────────────────────────────────────────┐
                    │  Iceberg Table (Streaming)              │
                    │  - Near real-time data                  │
                    │  - Also readable via Trino              │
                    └─────────────────────────────────────────┘
```

### 6.2.1 Flink Checkpoint Configuration

```java
// Flink Job 配置
StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
env.enableCheckpointing(30 * 1000);  // 每 30 秒 checkpoint
env.getCheckpointConfig().setMinPauseBetweenCheckpoints(10 * 1000);
env.getCheckpointConfig().setCheckpointTimeout(60 * 1000);
env.getCheckpointConfig().setTolerableCheckpointFailureNumber(3);

// Iceberg Sink 配置
FlinkSink.forBulkFormat(
        bufferedOutput, 
        ParquetAvroWriters.forClass(GitHubEvent.class)
    .withCheckpointInterval(30 * 1000)
    .build();
```

### 6.2.2 GitHub Webhook Security

```python
# src/webhook_server/verify_signature.py
import hmac
import hashlib

def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    if not signature:
        return False
    expected = hmac.new(
        secret.encode(), 
        payload, 
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)

# Flask 端点示例
@app.route("/webhook", methods=["POST"])
def handle_github_webhook():
    signature = request.headers.get("X-Hub-Signature-256")
    if not verify_signature(request.data, signature, os.getenv("GITHUB_WEBHOOK_SECRET")):
        return "Invalid signature", 401
    
    event_type = request.headers.get("X-GitHub-Event")
    payload = request.json
    # 处理事件...
```

---

## 7. Deployment

### 7.1 Docker Compose

```yaml
# docker/docker-compose.yml
services:
  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    volumes:
      - minio_data:/data

  gravitino:
    image: apache/gravitino:1.2.1
    ...

  spark:
    image: bitnami/spark
    ...

  trino:
    image: trinodb/trino
    ...

  redpanda:
    image: redpanda/redpanda
    ...
```

### 7.2 Directory Structure

```
personal-lakehouse/
├── docs/
│   ├── architecture.md          # 本文档
│   ├── data-dictionary.md       # 数据字典
│   └── pipeline-spec.md         # Pipeline 详细设计
├── notebooks/
│   ├── 01_eda_youtube.ipynb     # YouTube 数据探索
│   ├── 02_eda_chrome.ipynb      # Chrome 数据探索
│   └── 03_eda_github.ipynb      # GitHub 数据探索
├── scripts/
│   ├── etl/
│   │   ├── extract_takeout.py   # 解析 Takeout
│   │   ├── youtube_to_iceberg.py
│   │   ├── chrome_to_iceberg.py
│   │   └── github_to_iceberg.py
│   ├── dags/
│   │   ├── weekly_takeout_ingest.py
│   │   └── daily_silver_to_gold.py
│   └── utils/
├── src/
│   ├── webhook_server/          # GitHub Webhook 接收服务
│   └── flink_jobs/              # Flink 流处理代码
├── docker/
│   ├── docker-compose.yml
│   └── Dockerfile.*
└── data/
    └── sample/                  # 示例数据
```

---

## 8. Implementation Phases

| Phase | Content | Priority |
|-------|---------|----------|
| **Phase 1** | 本地 Docker + MinIO + Spark + Iceberg | P0 |
| **Phase 2** | 手动下载 Takeout，写入 Bronze + Silver | P0 |
| **Phase 3** | GitHub Webhook → Kafka → Flink → Iceberg | P1 |
| **Phase 4** | Gold 层聚合指标 | P1 |
| **Phase 5** | Trino SQL 查询层 | P2 |
| **Phase 6** | Airflow 调度 | P2 |
| **Phase 7** | Superset 可视化 | P2 |

---

## 9. Data Quality Framework

### 9.1 Overview

采用 Great Expectations 作为数据质量框架，在数据入场时进行校验。

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        DATA QUALITY PIPELINE                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   Data Ingestion ──▶ Validate ──▶ Pass? ──▶ Write to                  │
│                          │                │      Iceberg                │
│                          │                │                              │
│                          ▼                ▼                              │
│                    ┌──────────┐     ┌──────────┐                       │
│                    │ Generate │     │ Alert    │                       │
│                    │ Report   │     │ (Slack/  │                       │
│                    └──────────┘     │  Email)  │                       │
│                                     └──────────┘                       │
└─────────────────────────────────────────────────────────────────────────┘
```

### 9.2 Validation Rules

| Table | Rules |
|-------|-------|
| **Bronze Layer** | • File exists check<br>• Schema match (允许额外字段)<br>• Not all null check |
| **Silver Layer** | • Primary key uniqueness<br>• No null in required fields<br>• Data type validation<br>• Date range validation |
| **Gold Layer** | • Aggregated values sanity check<br>• Row count > 0<br>• Timestamp freshness |

### 9.3 Implementation

```python
# src/data_quality/expectations.py
import great_expectations as gx

def validate_silver_youtube():
    context = gx.get_context()
    datasource = context.sources.add_spark("spark_files")
    
    asset = datasource.add_parquet_files(
        name="youtube_silver",
        path="s3://warehouse/silver/youtube_watches/"
    )
    
    # 定义期望
    expectations = [
        gx.expectations.ExpectColumnValuesToNotBeNull(
            column="video_id"
        ),
        gx.expectations.ExpectColumnValuesToBeUnique(
            column="video_id"
        ),
        gx.expectations.ExpectColumnValuesToBeOfType(
            column="watch_timestamp",
            type_="TimestampType"
        ),
    ]
    
    result = asset.validate(expectations=expectations)
    
    if not result.success:
        send_alert(result)
    
    return result
```

### 9.4 Integration with Airflow

```python
# dags/data_quality_dag.py
from great_expectations.operators.validations_operator import ValidationsOperator

validate_bronze = ValidationsOperator(
    task_id='validate_bronze',
    expectation_suite_name='bronze_suite',
    validation_operator='action_operator_operator',
    dag=dag,
)

validate_silver = ValidationsOperator(
    task_id='validate_silver',
    expectation_suite_name='silver_suite',
    validation_operator='action_operator_operator',
    dag=dag,
)

# 校验失败时发送告警
validate_silver >> send_slack_alert
```

---

## 10. Monitoring & Alerting

### 10.1 Overview

采用 Prometheus + Grafana 监控整个 Lakehouse 系统。

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         MONITORING STACK                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐             │
│  │  Prometheus  │◀───│  Exporters   │◀───│  Services    │             │
│  │              │    │              │    │              │             │
│  │  • Metrics   │    │  • Node      │    │  • Airflow   │             │
│  │    Collection│    │  • Spark     │    │  • Trino     │             │
│  └──────┬───────┘    │  • Flink     │    │  • Spark     │             │
│         │            │  • Redpanda  │    │  • Iceberg   │             │
│         ▼            └──────────────┘    └──────────────┘             │
│  ┌──────────────┐                                                  │
│  │  Grafana     │                                                  │
│  │              │                                                  │
│  │  • Dashboards│                                                  │
│  │  • Alerts    │                                                  │
│  └──────────────┘                                                  │
└─────────────────────────────────────────────────────────────────────────┘
```

### 10.2 Metrics Collection

| Category | Metrics | Source |
|----------|---------|--------|
| **Pipeline** | DAG 运行状态、耗时、成功率 | Airflow Prometheus Exporter |
| **Data** | Row count, file size, delay | Spark/Flink metrics |
| **Storage** | Iceberg snapshot count, manifest size | Gravitino |
| **System** | CPU, Memory, Disk, Network | Node Exporter |
| **Query** | Trino query latency, failed queries | Trino Prometheus Exporter |

### 10.3 Alert Rules

```yaml
# prometheus/alerts.yml
groups:
- name: lakehouse
  interval: 30s
  rules:
  - alert: DagFailure
    expr: airflow_dag_status{status="failed"} > 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "DAG {{ $labels.dag_id }} failed"

  - alert: DataDelay
    expr: time() - max(iceberg_latest_partition_timestamp) > 86400
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "数据延迟超过24小时"

  - alert: DiskSpaceLow
    expr: (node_filesystem_avail_bytes / node_filesystem_size_bytes) < 0.1
    for: 5m
    labels:
      severity: warning

  - alert: QueryFailure
    expr: trino_failed_queries_total > 0
    for: 1m
    labels:
      severity: warning
```

### 10.4 Grafana Dashboards

| Dashboard | Content |
|-----------|---------|
| **Pipeline Overview** | DAG 运行状态、成功率、延迟趋势 |
| **Data Freshness** | 各表最新数据时间、延迟 |
| **Storage Usage** | S3 存储使用量、Iceberg 元数据大小 |
| **Query Performance** | Trino 查询延迟、并发数 |
| **System Health** | CPU/Memory/Disk 使用率 |

---

## 11. Data Catalog

### 11.1 Overview

使用 **Gravitino 内置的 Web UI** 作为数据目录，解决"有什么数据、在哪里、如何使用"的问题。

> 注：Gravitino 整合了元数据管理和数据发现功能，无需额外部署 Amundsen。

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         DATA CATALOG FEATURES                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                    │
│  │ Data        │  │ Data        │  │ Data        │                    │
│  │ Discovery   │  │ Lineage     │  │ Ownership   │                    │
│  │ ─────────   │  │ ─────────   │  │ ─────────   │                    │
│  │ • 关键字    │  │ • 上游到    │  │ • 责任人    │                    │
│  │   搜索      │  │   下游      │  │ • 维护者    │                    │
│  │ • 预览数据  │  │ • 可视化    │  │ • 联系方式  │                    │
│  │ • 相似的表  │  │ • 追溯      │  │ • 更新频率  │                    │
│  └─────────────┘  └─────────────┘  └─────────────┘                    │
│                                                                         │


│                                                                         │
│  数据源: 统一管理 Hive, MySQL, Iceberg, PostgreSQL 等多种数据源        │
│  Metalake: 按业务域分组管理（如 lakehouse, production, analytics）     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 11.2 Metadata Model

| Entity | Attributes |
|--------|------------|
| **Table** | Name, Description, Owner, Tags, Schema, Partition info |
| **Column** | Name, Type, Description, Is primary key, Is nullable |
| **Pipeline** | DAG name, Schedule, Source, Target, Code location |
| **Query** | SQL text, Author, Last run, Frequency |

### 11.3 Catalog Integration

Gravitino 自动管理 Iceberg 表的元数据，无需手动推送。通过 REST API 或 Web UI 管理。

```bash
# 通过 REST API 创建 Metalake
curl -X POST http://localhost:8090/api/metalakes \
  -H "Content-Type: application/json" \
  -d '{"name": "lakehouse", "comment": "Personal data lakehouse"}'

# 创建 Iceberg Catalog
curl -X POST http://localhost:8090/api/metalakes/lakehouse/catalogs \
  -H "Content-Type: application/json" \
  -d '{
    "name": "warehouse",
    "type": "iceberg",
    "comment": "Iceberg catalog for lakehouse",
    "properties": {
      "catalog-backend": "iceberg",
      "uri": "http://gravitino:8401",
      "warehouse": "s3://warehouse/"
    }
  }'
```

通过 Gravitino Web UI (http://localhost:8090) 可视化管理：
- 查看所有表元数据
- 管理 Schema 和 Table
- 设置访问权限
- 查看数据血缘

### 11.4 Data Lineage

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         DATA LINEAGE EXAMPLE                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌─────────────┐         ┌─────────────┐         ┌─────────────┐     │
│   │  Takeout    │         │   Bronze    │         │   Silver    │     │
│   │  JSON       │ ──────▶ │   Parquet   │ ──────▶ │   Parquet   │     │
│   │  (Raw)      │         │             │         │             │     │
│   └─────────────┘         └─────────────┘         └─────────────┘     │
│                                  │                      │              │
│                                  │                      ▼              │
│                                  │               ┌─────────────┐     │
│                                  │               │   Gold      │     │
│                                  └──────────────▶│   Views     │     │
│                                                 │             │     │
│                                                 └─────────────┘     │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 12. Logging

### 12.1 Overview

采用 **ELK Stack** (Elasticsearch + Logstash + Kibana) 或 **Loki** 进行日志收集。

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         LOGGING ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   Services              Collect                  Store        Query    │
│   ────────              ──────                  ──────       ─────    │
│                                                                         │
│   ┌─────────┐           ┌─────────┐          ┌───────────┐  ┌──────┐ │
│   │ Airflow │──────────▶│         │          │           │  │      │ │
│   ├─────────┤           │ Fluentd │─────────▶│Elasticsearch│▶│Kibana│ │
│   │ Spark   │──────────▶│  (Agent)│          │  / Loki   │  │      │ │
│   ├─────────┤           │         │          │           │  │      │ │
│   │ Flink   │──────────▶│         │          │           │  │      │ │
│   ├─────────┤           └─────────┘          └───────────┘  └──────┘ │
│   │ Trino   │                                                       │
│   └─────────┘                                                       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 12.2 Log Categories

| Service | Log Type | Key Fields |
|---------|----------|------------|
| Airflow | DAG run, Task | dag_id, task_id, status, duration |
| Spark | Job, Stage | app_id, executor_id, stage_id |
| Flink | Job, Operator | job_id, operator_name, checkpoint |
| Iceberg | Commit, Manifest | table, snapshot_id, operation |

---

## 13. Deployment (Docker Compose)

### 13.1 Services

```yaml
# docker/docker-compose.yml
version: '3.8'

services:
  # ============= STORAGE =============
  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: ${MINIO_USER}
      MINIO_ROOT_PASSWORD: ${MINIO_PASSWORD}
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio_data:/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s

  # ============= CATALOG =============
  gravitino:
    image: apache/gravitino:1.2.1
    environment:
      GRAVITINO_METASTORE: lakehouse-iceberg
      GRAVITINO_S3_ACCESS_KEY_ID: ${MINIO_USER}
      GRAVITINO_S3_SECRET_ACCESS_KEY: ${MINIO_PASSWORD}
      GRAVITINO_S3_ENDPOINT: http://minio:9000
      GRAVITINO_S3_PATH_STYLE_ACCESS: "true"
    ports:
      - "8090:8090"
      - "8401:8401"  # Iceberg REST API

  # ============= COMPUTE =============
  spark-master:
    image: bitnami/spark:3.5.0
    environment:
      SPARK_MODE: master
      SPARK_RPC_AUTHENTICATION_ENABLED: "no"
      SPARK_RPC_ENCRYPTION_ENABLED: "no"
      SPARK_LOCAL_STORAGE_ENCRYPTION_ENABLED: "no"
      SPARK_SSL_ENABLED: "no"
    ports:
      - "8080:8080"

  spark-worker:
    image: bitnami/spark:3.5.0
    environment:
      SPARK_MODE: worker
      SPARK_MASTER_URL: spark://spark-master:7077
      SPARK_WORKER_MEMORY: 4G
      SPARK_WORKER_CORES: 2
    depends_on:
      - spark-master

  trino:
    image: trinodb/trino:427
    ports:
      - "8081:8080"
    volumes:
      - ./trino/etc:/etc/trino

  # ============= STREAM =============
  redpanda:
    image: redpanda/redpanda:v23.3.9
    command: redpanda start --kafka-addr INTERNAL://0.0.0.0:9092 --advertise-kafka-addr localhost:9092 --pandaproxy-addr 0.0.0.0:8082
    ports:
      - "9092:9092"
      - "8081:8081"

  # ============= ORCHESTRATION =============
  airflow-webserver:
    image: apache/airflow:2.9.2
    environment:
      AIRFLOW__CORE__EXECUTOR: LocalExecutor
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow
    ports:
      - "8080:8080"
    volumes:
      - ./dags:/opt/airflow/dags
    depends_on:
      - postgres

  # ============= MONITORING =============
  prometheus:
    image: prom/prometheus:v2.48.0
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana:10.2.0
    ports:
      - "3000:3000"
    volumes:
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards

  # ============= CATALOG TOOLS =============
# 统一由 Gravitino 提供，无需额外部署

  # ============= QUERY =============
  jupyter:
    image: jupyter/pyspark-notebook:latest
    ports:
      - "8888:8888"
    volumes:
      - ./notebooks:/home/jovyan/work

  # ============= BI =============
  superset:
    image: apache/superset:3.1.0
    ports:
      - "8088:8088"

  # ============= DB =============
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
      POSTGRES_DB: airflow
    volumes:
      - postgres_data:/var/lib/postgresql/data

# ============= LOGGING =============
  loki:
    image: grafana/loki:2.9.0
    ports:
      - "3100:3100"
    volumes:
      - loki_data:/loki

  promtail:
    image: grafana/promtail:2.9.0
    volumes:
      - ./promtail/promtail.yml:/etc/promtail/promtail.yml
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
    depends_on:
      - loki
    command: -config.file=/etc/promtail/promtail.yml

  # ============= STREAM COMPUTE =============
  flink-jobmanager:
    image: flink:1.18.1-scala_2.12-java11
    container_name: flink-jobmanager
    ports:
      - "8083:8081"
    environment:
      - |
        FLINK_PROPERTIES=
        jobmanager.rpc.address: flink-jobmanager
        state.backend: filesystem
        state.checkpoints.dir: s3://warehouse/flink/checkpoints
        state.savepoints.dir: s3://warehouse/flink/savepoints

  flink-taskmanager:
    image: flink:1.18.1-scala_2.12-java11
    container_name: flink-taskmanager
    depends_on:
      - flink-jobmanager
    environment:
      - |
        FLINK_PROPERTIES=
        jobmanager.rpc.address: flink-jobmanager
        taskmanager.numberOfTaskSlots: 2

  # ============= WEBHOOK SERVER =============
  webhook-server:
    build:
      context: ../src/webhook_server
      dockerfile: Dockerfile
    container_name: webhook-server
    ports:
      - "8084:8084"
    environment:
      - GITHUB_WEBHOOK_SECRET=${GITHUB_WEBHOOK_SECRET}
      - REDPANDA_BROKER=redpanda:9092
      - FLINK_JOB_MANAGER=http://flink-jobmanager:8081
    depends_on:
      - redpanda

volumes:
  minio_data:
  postgres_data:
  loki_data:
```

### 13.2 Environment Variables

```bash
# docker/.env
MINIO_USER=minioadmin
MINIO_PASSWORD=minioadmin

# GitHub Webhook Secret (HMAC-SHA256)
GITHUB_WEBHOOK_SECRET=your_secret_here

# Gravitino
GRAVITINO_HOST=gravitino
GRAVITINO_PORT=8090
```

### 13.3 Startup

```bash
cd ~/workspace/personal-lakehouse/docker
docker-compose up -d

# 检查服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

---

## 14. Appendix

### 14.1 Iceberg Table Properties

```sql
-- 所有表统一配置
TBLPROPERTIES (
    'format-version' = '2',
    'write.distribution-mode' = 'hash',
    'write.metadata.delete-after-commit.enabled' = 'true',
    'write.metadata.previous-versions-max' = '100',
    'history.expire.max-snapshots-keep' = '100',
    'commit.retry.num-retries' = '4'
);
```

### 14.2 Time Travel Example

```sql
-- 查看 3 天前的数据
SELECT * FROM silver.youtube_watches
TIMESTAMP AS OF current_timestamp - INTERVAL '3' DAY;

-- 查看特定快照
SELECT * FROM silver.youtube_watches
SNAPSHOT 1234567890000;
```

---

### 14.3 Backup Strategy (MinIO Lifecycle)

```yaml
# docker/minio-bucket-policy.json
{
  "Rules": [
    {
      "ID": "expire-old-snapshots",
      "Status": "Enabled",
      "Filter": {
        "Prefix": "warehouse/"
      },
      "Expiration": {
        "Days": 90
      }
    },
    {
      "ID": "archive-gold-tier",
      "Status": "Enabled",
      "Filter": {
        "Prefix": "warehouse/gold/"
      },
      "Transitions": {
        "Days": 30,
        "StorageClass": "STANDARD"
      }
    }
  ]
}
```

```bash
# MinIO 生命周期规则
mc ilm import minio/warehouse < minio-bucket-policy.json

# 或通过 mc 命令设置
mc ilm rule add minio/warehouse --prefix "warehouse/bronze/" --expire-days 30
mc ilm rule add minio/warehouse --prefix "warehouse/silver/" --expire-days 90
mc ilm rule add minio/warehouse --prefix "warehouse/gold/" --expire-days 365
```

### 14.4 Promtail Configuration

```yaml
# docker/promtail/promtail.yml
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: docker
    static_configs:
      - targets:
          - localhost
        labels:
          job: containerlogs
          __path__: /var/lib/docker/containers/*/*log

  - job_name: airflow
    static_configs:
      - targets:
          - airflow-webserver:8080
        labels:
          service: airflow

  - job_name: spark
    static_configs:
      - targets:
          - spark-master:8080
        labels:
          service: spark
```

### 14.5 Webhook Server Dockerfile

```dockerfile
# src/webhook_server/Dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN pip install flask hmac hashlib kafka-python

COPY app.py verify_signature.py ./

EXPOSE 8084

CMD ["python", "app.py"]
```

### 14.6 Webhook Server Application

```python
# src/webhook_server/app.py
from flask import Flask, request, jsonify
from verify_signature import verify_signature
from kafka import KafkaProducer
import json
import os

app = Flask(__name__)
producer = KafkaProducer(
    bootstrap_servers=os.getenv("REDPANDA_BROKER", "redpanda:9092"),
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

@app.route("/webhook", methods=["POST"])
def handle_github_webhook():
    signature = request.headers.get("X-Hub-Signature-256")
    if not verify_signature(request.data, signature, os.getenv("GITHUB_WEBHOOK_SECRET")):
        return "Invalid signature", 401
    
    event_type = request.headers.get("X-GitHub-Event")
    payload = request.json
    
    if event_type == "push":
        producer.send("github-events", value={
            "event_type": "push",
            "ref": payload.get("ref"),
            "commits": payload.get("commits", []),
            "repository": payload.get("repository", {}).get("full_name")
        })
    
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8084)
```

---

*Generated: 2025-06-07*
*Based on: Practical Lakehouse Architecture Chapter 1*
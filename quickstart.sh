#!/bin/bash
# 快速开始脚本 - 一键运行整个 pipeline

echo "🚀 Personal Data Lakehouse - Quick Start"
echo "=========================================="

# 检查 Docker 服务
echo "1. Checking Docker services..."
docker ps --format "{{.Names}}: {{.Status}}" | grep -E "minio|redpanda" || echo "  Warning: Some services may not be running"

# 采集数据
echo ""
echo "2. Collecting data..."
python3 scripts/collectors/fetch_github_trending.py
python3 scripts/collectors/fetch_bilibili_trending.py

# 运行 ETL
echo ""
echo "3. Running ETL..."
python3 src/etl/run_pipeline.py

# 验证数据
echo ""
echo "4. Validating data quality..."
python3 src/data_quality/validate_data.py

# 发送到流
echo ""
echo "5. Streaming to Redpanda..."
python3 src/streaming/stream_manager.py send

echo ""
echo "=========================================="
echo "✅ Quick start complete!"
echo ""
echo "Query data:"
echo "  python3 src/etl/query_data.py --source github"
echo "  python3 src/etl/query_data.py --source bilibili"
echo ""
echo "Stream consume:"
echo "  docker exec lakehouse-redpanda rpk topic consume github-trending"

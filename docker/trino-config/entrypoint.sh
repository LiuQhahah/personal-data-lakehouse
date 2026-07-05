#!/bin/bash
set -e

# 创建数据目录
mkdir -p /data/trino

# 根据环境变量动态生成配置
if [ "$TRINO_COORDINATOR" = "false" ]; then
    # Worker模式
    cat > /etc/trino/config.properties << EOF
coordinator=false
discovery.uri=http://lakehouse-trino-coordinator:8080
http-server.http.port=8080
query.max-memory=2GB
EOF
    
    # Worker使用不同的node id
    echo "node.environment=lakehouse
node.data-dir=/data/trino
node.id=trino-worker" > /etc/trino/node.properties
    
    echo "Starting Trino Worker..."
else
    # Coordinator模式
    cat > /etc/trino/config.properties << EOF
coordinator=true
node-scheduler.include-coordinator=false
discovery.uri=http://lakehouse-trino-coordinator:8080
http-server.http.port=8080
query.max-memory=2GB
EOF
    
    echo "node.environment=lakehouse
node.data-dir=/data/trino
node.id=trino-coordinator" > /etc/trino/node.properties
    
    echo "Starting Trino Coordinator..."
fi

# JVM配置
echo "-server
-Xmx2g
-XX:+UseG1GC
-XX:+ExplicitGCInvokesConcurrent" > /etc/trino/jvm.config

# 启动Trino
exec /usr/lib/trino/bin/launcher run --etc-dir /etc/trino
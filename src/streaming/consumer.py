#!/usr/bin/env python3
"""
流数据消费者 - 从 Redpanda 读取并处理数据
"""
import sys
import time
from redpanda import RedpandaClient

# 简单的控制台消费者
def consume(topic: str, max_messages: int = 10):
    client = RedpandaClient(bootstrap_servers="localhost:9092")
    
    print(f"📥 Listening to topic: {topic}")
    
    # 由于没有 redpanda-python 库，用命令行工具代替
    import subprocess
    result = subprocess.run(
        ["docker", "exec", "lakehouse-redpanda", "rpk", "topic", "consume", topic, "--num", str(max_messages)],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(result.stdout)
    else:
        print(f"Error: {result.stderr}")

if __name__ == "__main__":
    topic = sys.argv[1] if len(sys.argv) > 1 else "github-trending"
    max_msgs = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    consume(topic, max_msgs)

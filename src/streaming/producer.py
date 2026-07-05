#!/usr/bin/env python3
"""
流数据生产者 - 将采集的数据发送到 Redpanda
"""
import json
import time
import sys
import os
import random

# 读取数据并发送到 Redpanda
def produce_github():
    """模拟实时 GitHub 数据流"""
    with open(os.path.expanduser('~/workspace/personal-lakehouse/data/github_trending.json')) as f:
        data = json.load(f)
    
    for item in data['data']:
        # 每条记录模拟一条消息
        event = {
            "event_type": "github_trending",
            "data": item,
            "timestamp": time.time()
        }
        print(json.dumps(event))
        time.sleep(0.5)  # 模拟实时到达

def produce_bilibili():
    """模拟实时 B站 数据流"""
    with open(os.path.expanduser('~/workspace/personal-lakehouse/data/bilibili_trending.json')) as f:
        data = json.load(f)
    
    for item in data:
        event = {
            "event_type": "bilibili_trending",
            "data": item,
            "timestamp": time.time()
        }
        print(json.dumps(event))
        time.sleep(0.3)

if __name__ == "__main__":
    source = sys.argv[1] if len(sys.argv) > 1 else "github"
    
    if source == "github":
        produce_github()
    elif source == "bilibili":
        produce_bilibili()
    else:
        print("Usage: producer.py [github|bilibili]")

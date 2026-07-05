#!/usr/bin/env python3
"""
流处理管理器 - 发送采集数据到 Redpanda
"""
import json
import subprocess
import sys
import os
from datetime import datetime

class StreamManager:
    def __init__(self):
        self.rpk = ["docker", "exec", "lakehouse-redpanda", "rpk"]
    
    def produce_to_topic(self, topic: str, data: dict):
        """发送数据到 topic"""
        cmd = self.rpk + ["topic", "produce", topic]
        result = subprocess.run(
            cmd,
            input=json.dumps(data),
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    
    def send_github(self, filepath: str):
        """发送 GitHub 数据"""
        with open(filepath) as f:
            data = json.load(f)
        
        for item in data.get('data', []):
            event = {
                "event_type": "github_trending",
                "source": "github_api",
                "timestamp": datetime.now().isoformat(),
                "data": item
            }
            self.produce_to_topic("github-trending", event)
        
        print(f"✅ Sent {len(data.get('data', []))} events to github-trending")
    
    def send_bilibili(self, filepath: str):
        """发送 B站 数据"""
        with open(filepath) as f:
            data = json.load(f)
        
        for item in data:
            event = {
                "event_type": "bilibili_trending",
                "source": "bilibili_api",
                "timestamp": datetime.now().isoformat(),
                "data": item
            }
            self.produce_to_topic("bilibili-trending", event)
        
        print(f"✅ Sent {len(data)} events to bilibili-trending")
    
    def consume(self, topic: str, num: int = 5):
        """消费消息"""
        cmd = self.rpk + ["topic", "consume", topic, "--num", str(num)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout


def main():
    manager = StreamManager()
    
    if len(sys.argv) < 2:
        print("Usage: stream_manager.py [send|consume] [topic]")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "send":
        # 发送数据到 topics
        github_file = os.path.expanduser("~/workspace/personal-lakehouse/data/github_trending.json")
        bilibili_file = os.path.expanduser("~/workspace/personal-lakehouse/data/bilibili_trending.json")
        
        if os.path.exists(github_file):
            manager.send_github(github_file)
        if os.path.exists(bilibili_file):
            manager.send_bilibili(bilibili_file)
    
    elif action == "consume":
        topic = sys.argv[2] if len(sys.argv) > 2 else "github-trending"
        print(f"📥 Consuming from {topic}:")
        print(manager.consume(topic, 3))
    
    else:
        print("Unknown action")


if __name__ == "__main__":
    main()

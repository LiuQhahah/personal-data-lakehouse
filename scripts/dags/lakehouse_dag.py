#!/usr/bin/env python3
"""
Lakehouse 数据采集 DAG - 每天自动采集数据
"""
import subprocess, sys, os
from datetime import datetime

WORKDIR = os.path.expanduser("~/workspace/personal-lakehouse")

def run(cmd):
    result = subprocess.run(cmd, shell=True, cwd=WORKDIR, capture_output=True, text=True)
    return result.returncode == 0

def main():
    print(f"🚀 DAG Start - {datetime.now()}")
    
    collectors = [
        "python3 scripts/collectors/fetch_github_trending.py",
        "python3 scripts/collectors/fetch_bilibili_trending.py",
    ]
    
    for cmd in collectors:
        print(f"Running: {cmd}")
        if not run(cmd):
            print(f"❌ Failed: {cmd}")
    
    # 复制Bronze层数据
    print("Copying Bronze layer...")
    run("cp data/github_trending.json data/warehouse/bronze/")
    run("cp data/bilibili_trending.json data/warehouse/bronze/")
    
    # ETL: Silver → Gold
    print("Running ETL (Silver → Gold)...")
    run("python3 src/etl/run_pipeline.py")
    
    # 复制web目录
    print("Copying to web...")
    run("cp data/github_trending.json web/")
    run("cp data/bilibili_trending.json web/")
    
    print(f"✅ DAG End - {datetime.now()}")

if __name__ == "__main__":
    main()

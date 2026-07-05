#!/usr/bin/env python3
"""
查询 MinIO 中的数据
"""
from minio import Minio
import pandas as pd
import io
import sys

def query_github(limit: int = 10):
    """查询 GitHub Trending"""
    client = Minio("localhost:9000", "minioadmin", "minioadmin", secure=False)
    
    # 获取最新的 Parquet 文件
    objects = list(client.list_objects("data", prefix="bronze/github_trending/"))
    if not objects:
        print("No GitHub data found")
        return
    
    latest = objects[-1].object_name
    response = client.get_object("data", latest)
    df = pd.read_parquet(io.BytesIO(response.read()))
    
    print(f"=== GitHub Trending (Top {limit} by stars) ===")
    top = df.nlargest(limit, 'stars')[['repo_name', 'stars', 'language', 'fetch_date']]
    print(top.to_string(index=False))
    print(f"\nTotal: {len(df)} repos | Avg stars: {df['stars'].mean():,.0f}")

def query_bilibili(limit: int = 10):
    """查询 B站热搜"""
    client = Minio("localhost:9000", "minioadmin", "minioadmin", secure=False)
    
    objects = list(client.list_objects("data", prefix="bronze/bilibili_trending/"))
    if not objects:
        print("No Bilibili data found")
        return
    
    latest = objects[-1].object_name
    response = client.get_object("data", latest)
    df = pd.read_parquet(io.BytesIO(response.read()))
    
    print(f"=== Bilibili Trending (Top {limit}) ===")
    top = df.head(limit)[['rank', 'title', 'hot_words']]
    print(top.to_string(index=False))
    print(f"\nTotal: {len(df)} items")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Query Lakehouse data')
    parser.add_argument('--source', choices=['github', 'bilibili', 'all'], default='all')
    parser.add_argument('--limit', type=int, default=10)
    args = parser.parse_args()
    
    if args.source in ('github', 'all'):
        query_github(args.limit)
        if args.source == 'all':
            print()
    
    if args.source in ('bilibili', 'all'):
        query_bilibili(args.limit)

if __name__ == "__main__":
    main()

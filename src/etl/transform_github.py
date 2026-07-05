#!/usr/bin/env python3
"""
转换 GitHub Trending 数据到 Parquet 格式并上传 MinIO
"""
import os
import sys
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etl.etl_utils import MinIOClient, load_json_data

# 字段映射：JSON -> Parquet
FIELD_MAPPING = {
    'repo_name': 'repo_name',
    'description': 'description', 
    'language': 'language',
    'stars': 'stars',
    'forks': 'forks',
    'today_stars': 'today_stars',
    'contributors': 'contributors',
    'url': 'url',
    'fetch_date': 'fetch_date',
    'created_at': 'created_at',
}

def transform_github(data: list) -> dict:
    """转换 GitHub 数据"""
    rows = []
    for item in data:
        # 解析日期
        fetch_date = item.get('fetch_date', datetime.now().strftime('%Y-%m-%d'))
        
        # 转换 created_at
        created_at = item.get('created_at')
        if created_at:
            try:
                created_at = datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%SZ')
            except:
                created_at = None
        
        row = {
            'repo_name': item.get('repo_name', ''),
            'description': (item.get('description') or '')[:500],
            'language': item.get('language') or '',
            'stars': item.get('stars', 0) or 0,
            'forks': item.get('forks', 0) or 0,
            'today_stars': item.get('today_stars', 0) or 0,
            'contributors': item.get('contributors', 0) or 0,
            'url': item.get('url', ''),
            'fetch_date': fetch_date,
            'created_at': created_at,
            '_raw_json': str(item)[:2000],
            '_ingest_time': datetime.now(),
            '_batch_id': f"batch_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        }
        rows.append(row)
    
    return rows

def main():
    # 读取原始数据
    input_file = os.path.expanduser('~/workspace/personal-lakehouse/data/github_trending.json')
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found")
        return
    
    # 转换
    data = load_json_data(input_file)
    rows = transform_github(data)
    
    import pandas as pd
    df = pd.DataFrame(rows)
    
    print(f"✅ Transformed {len(df)} rows")
    print(df.head(3))
    
    # 上传到 MinIO (Parquet)
    minio_client = MinIOClient()
    minio_client.upload_parquet(df, "github_trending", layer="bronze")
    
    # 也上传原始 JSON
    minio_client.upload_json(data, "github_trending")
    
    print("\n🎉 GitHub data pipeline complete!")

if __name__ == "__main__":
    main()

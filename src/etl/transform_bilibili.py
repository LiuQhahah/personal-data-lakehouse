#!/usr/bin/env python3
"""
转换 B站热搜 数据到 Parquet 格式并上传 MinIO
"""
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etl.etl_utils import MinIOClient, load_json_data

def transform_bilibili(data: list) -> list:
    """转换 B站 数据"""
    rows = []
    for item in data:
        row = {
            'rank': item.get('rank', 0),
            'title': item.get('title', ''),
            'url': item.get('url', ''),
            'hot_words': item.get('hot_words', ''),
            'fetch_date': item.get('fetch_date', datetime.now().strftime('%Y-%m-%d')),
            '_raw_json': str(item)[:2000],
            '_ingest_time': datetime.now(),
            '_batch_id': f"batch_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        }
        rows.append(row)
    
    return rows

def main():
    input_file = os.path.expanduser('~/workspace/personal-lakehouse/data/bilibili_trending.json')
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found")
        return
    
    data = load_json_data(input_file)
    rows = transform_bilibili(data)
    
    import pandas as pd
    df = pd.DataFrame(rows)
    
    print(f"✅ Transformed {len(df)} rows")
    print(df.head(3))
    
    minio_client = MinIOClient()
    minio_client.upload_parquet(df, "bilibili_trending", layer="bronze")
    minio_client.upload_json(data, "bilibili_trending")
    
    print("\n🎉 Bilibili data pipeline complete!")

if __name__ == "__main__":
    main()

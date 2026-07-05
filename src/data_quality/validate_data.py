#!/usr/bin/env python3
"""
数据质量验证脚本
检查 MinIO 中的数据是否符合预期
"""
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from minio import Minio
import pandas as pd
import io


class DataValidator:
    def __init__(self):
        self.client = Minio("localhost:9000", "minioadmin", "minioadmin", secure=False)
        self.results = []
    
    def validate_github(self):
        """验证 GitHub 数据"""
        print("\n=== Validating GitHub Trending ===")
        
        objects = list(self.client.list_objects("data", prefix="bronze/github_trending/"))
        if not objects:
            print("❌ No data found")
            return False
        
        latest = objects[-1].object_name
        response = self.client.get_object("data", latest)
        df = pd.read_parquet(io.BytesIO(response.read()))
        
        checks = []
        
        # 1. 检查行数
        if len(df) >= 20:
            checks.append(("Row count >= 20", True, f"{len(df)} rows"))
        else:
            checks.append(("Row count >= 20", False, f"{len(df)} rows"))
        
        # 2. 检查必需列
        required_cols = ['repo_name', 'stars', 'url', 'fetch_date']
        missing = set(required_cols) - set(df.columns)
        if not missing:
            checks.append(("Required columns exist", True, "All present"))
        else:
            checks.append(("Required columns exist", False, f"Missing: {missing}"))
        
        # 3. 检查 stars > 0
        if df['stars'].notna().sum() == len(df):
            checks.append(("All stars not null", True, f"{df['stars'].notna().sum()}/{len(df)}"))
        else:
            checks.append(("All stars not null", False, f"{df['stars'].isna().sum()} nulls"))
        
        # 4. 检查 URL 格式
        valid_urls = df['url'].str.startswith('https://github.com/', na=False)
        if valid_urls.sum() >= len(df) * 0.9:
            checks.append(("URLs valid", True, f"{valid_urls.sum()}/{len(df)}"))
        else:
            checks.append(("URLs valid", False, f"Only {valid_urls.sum()}/{len(df)}"))
        
        # 输出结果
        for name, passed, detail in checks:
            status = "✅" if passed else "❌"
            print(f"  {status} {name}: {detail}")
        
        return all(c[1] for c in checks)
    
    def validate_bilibili(self):
        """验证 B站 数据"""
        print("\n=== Validating Bilibili Trending ===")
        
        objects = list(self.client.list_objects("data", prefix="bronze/bilibili_trending/"))
        if not objects:
            print("❌ No data found")
            return False
        
        latest = objects[-1].object_name
        response = self.client.get_object("data", latest)
        df = pd.read_parquet(io.BytesIO(response.read()))
        
        checks = []
        
        # 1. 检查行数
        if len(df) >= 50:
            checks.append(("Row count >= 50", True, f"{len(df)} rows"))
        else:
            checks.append(("Row count >= 50", False, f"{len(df)} rows"))
        
        # 2. 检查必需列
        required_cols = ['title', 'url', 'rank']
        missing = set(required_cols) - set(df.columns)
        if not missing:
            checks.append(("Required columns exist", True, "All present"))
        else:
            checks.append(("Required columns exist", False, f"Missing: {missing}"))
        
        # 3. 检查 rank 连续
        expected_ranks = list(range(1, len(df) + 1))
        actual_ranks = df['rank'].tolist()
        if expected_ranks == actual_ranks:
            checks.append(("Rank sequential", True, "1 to N"))
        else:
            checks.append(("Rank sequential", False, "Not sequential"))
        
        # 4. 检查无空标题
        if df['title'].notna().sum() == len(df):
            checks.append(("No null titles", True, f"{len(df)} titles"))
        else:
            checks.append(("No null titles", False, f"{df['title'].isna().sum()} nulls"))
        
        # 输出结果
        for name, passed, detail in checks:
            status = "✅" if passed else "❌"
            print(f"  {status} {name}: {detail}")
        
        return all(c[1] for c in checks)
    
    def run_all(self):
        """运行所有验证"""
        print(f"\n🔍 Data Quality Validation - {datetime.now()}")
        print("="*50)
        
        results = []
        results.append(("GitHub", self.validate_github()))
        results.append(("Bilibili", self.validate_bilibili()))
        
        print("\n" + "="*50)
        print("Summary:")
        for name, passed in results:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {name}: {status}")
        
        all_passed = all(r[1] for r in results)
        print(f"\n{'✅ All validations passed' if all_passed else '❌ Some validations failed'}")
        return all_passed


if __name__ == "__main__":
    validator = DataValidator()
    success = validator.run_all()
    sys.exit(0 if success else 1)

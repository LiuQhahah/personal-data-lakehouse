#!/usr/bin/env python3
"""
使用 Gravitino REST API 创建 Lakehouse 表

Usage:
    python create_tables.py --create-all          # 创建所有表
    python create_tables.py --create bronze       # 创建 Bronze 层
    python create_tables.py --list-tables         # 列出已创建的表
"""

import os
import sys
import json
import argparse
import urllib.request
import ssl
from datetime import datetime
from typing import Dict, List, Any, Optional

# 导入表定义
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from table_definitions import BRONZE_TABLES, SILVER_TABLES, GOLD_TABLES, ALL_TABLES

# 配置
DEFAULT_GRAVITINO_HOST = os.environ.get("GRAVITINO_HOST", "localhost")
DEFAULT_GRAVITINO_PORT = os.environ.get("GRAVITINO_PORT", "8090")

# 禁用 SSL 警告
ssl._create_default_https_context = ssl._create_unverified_context


class GravitinoTableManager:
    """Gravitino 表管理器"""
    
    def __init__(self, host: str = None, port: int = None):
        self.base_url = os.environ.get(
            "GRAVITINO_URL", 
            f"http://{host or DEFAULT_GRAVITINO_HOST}:{port or DEFAULT_GRAVITINO_PORT}"
        )
        self.metalake = "lakehouse"
        self.catalog = "iceberg-catalog"
        print(f"[Gravitino] Manager initialized: {self.base_url}")
    
    def _request(self, method: str, path: str, data: dict = None) -> Optional[Dict]:
        """发起 API 请求"""
        url = f"{self.base_url}/api/{path.lstrip('/')}"
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        try:
            body = json.dumps(data).encode('utf-8') if data else None
            req = urllib.request.Request(url, data=body, headers=headers, method=method)
            
            with urllib.request.urlopen(req, timeout=30) as response:
                content = response.read().decode('utf-8')
                if response.status < 400:
                    return json.loads(content) if content else {}
                else:
                    print(f"[Gravitino] HTTP {response.status}: {content[:200]}")
                    return None
                    
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if e.fp else ""
            print(f"[Gravitino] HTTP Error {e.code}: {error_body[:200]}")
            return None
        except Exception as e:
            print(f"[Gravitino] Error: {e}")
            return None
    
    def _build_iceberg_table(self, table_def: dict) -> dict:
        """构建 Iceberg 表定义"""
        
        # 构建列定义
        columns = []
        for col in table_def.get("columns", []):
            column = {
                "name": col["name"],
                "type": col["type"].upper(),
                "nullable": col.get("nullable", True),
                "comment": col.get("comment", ""),
            }
            columns.append(column)
        
        # 构建分区
        partitioning = []
        for part in table_def.get("partitioning", []):
            transform = part.get("transform", "identity")
            field = part.get("field")
            
            if transform == "day":
                partitioning.append({
                    "fieldName": [field],
                    "transform": "day"
                })
            elif transform == "month":
                partitioning.append({
                    "fieldName": [field],
                    "transform": "month"
                })
            elif transform == "year":
                partitioning.append({
                    "fieldName": [field],
                    "transform": "year"
                })
            elif transform == "hour":
                partitioning.append({
                    "fieldName": [field],
                    "transform": "hour"
                })
        
        # 构建完整表定义
        table = {
            "name": "",  # 会在创建时设置
            "comment": table_def.get("comment", ""),
            "columns": columns,
            "partitioning": partitioning,
            "properties": table_def.get("properties", {})
        }
        
        return table
    
    def create_table(self, schema: str, table_name: str, table_def: dict) -> bool:
        """创建单个表"""
        
        # 处理表名 (可能带 schema 前缀)
        full_table_name = f"{schema}.{table_name}" if "." not in table_name else table_name
        
        print(f"  创建表: {full_table_name}")
        
        # 构建 Iceberg 表定义
        iceberg_table = self._build_iceberg_table(table_def)
        iceberg_table["name"] = full_table_name
        
        # 构建 Gravitino 请求
        gravitino_table = {
            "name": full_table_name,
            "comment": table_def.get("comment", ""),
            "columns": iceberg_table["columns"],
            "partitioning": iceberg_table["partitioning"],
            "properties": {
                "table-type": "EXTERNAL",
                "format-version": "2",
                **iceberg_table.get("properties", {})
            }
        }
        
        # 发送创建请求
        path = f"/metalakes/{self.metalake}/catalogs/{self.catalog}/schemas/{schema}/tables"
        result = self._request("POST", path, gravitino_table)
        
        if result:
            print(f"    ✓ 创建成功")
            return True
        else:
            print(f"    ✗ 创建失败")
            return False
    
    def list_tables(self, schema: str) -> List[str]:
        """列出 schema 下的表"""
        path = f"/metalakes/{self.metalake}/catalogs/{self.catalog}/schemas/{schema}/tables"
        result = self._request("GET", path)
        
        if result:
            return [t.get("name", "").split(".")[-1] for t in result.get("tables", [])]
        return []
    
    def create_layer(self, layer: str, tables: dict) -> Dict[str, bool]:
        """创建整个层的表"""
        
        results = {}
        
        # 映射层到 schema
        schema_map = {
            "bronze": "bronze",
            "silver": "silver", 
            "gold": "gold"
        }
        
        schema = schema_map.get(layer, layer)
        
        print(f"\n{'='*50}")
        print(f"创建 {layer.upper()} 层: {len(tables)} 张表")
        print(f"{'='*50}")
        
        for table_name, table_def in tables.items():
            success = self.create_table(schema, table_name, table_def)
            results[table_name] = success
        
        return results


def main():
    parser = argparse.ArgumentParser(description='Gravitino 表管理工具')
    parser.add_argument('--host', default=DEFAULT_GRAVITINO_HOST)
    parser.add_argument('--port', type=int, default=DEFAULT_GRAVITINO_PORT)
    parser.add_argument('--create-all', action='store_true', help='创建所有表')
    parser.add_argument('--create', choices=['bronze', 'silver', 'gold', 'all'], 
                        help='创建指定层')
    parser.add_argument('--list-tables', action='store_true', help='列出表')
    parser.add_argument('--dry-run', action='store_true', help='只显示不创建')
    
    args = parser.parse_args()
    
    manager = GravitinoTableManager(host=args.host, port=args.port)
    
    if args.list_tables:
        for layer, tables in [("bronze", BRONZE_TABLES), 
                               ("silver", SILVER_TABLES), 
                               ("gold", GOLD_TABLES)]:
            schema = {"bronze": "bronze", "silver": "silver", "gold": "gold"}[layer]
            table_list = manager.list_tables(schema)
            print(f"\n{layer.upper()} ({len(table_list)} 张):")
            for t in table_list:
                print(f"  - {t}")
    
    elif args.create_all or args.create:
        layers_to_create = []
        
        if args.create == "all":
            layers_to_create = [
                ("bronze", BRONZE_TABLES),
                ("silver", SILVER_TABLES),
                ("gold", GOLD_TABLES)
            ]
        elif args.create == "bronze":
            layers_to_create = [("bronze", BRONZE_TABLES)]
        elif args.create == "silver":
            layers_to_create = [("silver", SILVER_TABLES)]
        elif args.create == "gold":
            layers_to_create = [("gold", GOLD_TABLES)]
        
        for layer, tables in layers_to_create:
            results = manager.create_layer(layer, tables)
            
            success = sum(1 for v in results.values() if v)
            failed = sum(1 for v in results.values() if not v)
            
            print(f"\n{layer.upper()} 层: {success} 成功, {failed} 失败")
    
    else:
        print("用法:")
        print("  python create_tables.py --create-all          # 创建所有表")
        print("  python create_tables.py --create bronze       # 只创建 Bronze")
        print("  python create_tables.py --list-tables         # 列出表")


if __name__ == '__main__':
    main()
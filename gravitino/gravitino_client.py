#!/usr/bin/env python3
"""
Gravitino Schema Registry 初始化脚本
使用 Gravitino REST API 管理 Lakehouse 的元数据

Usage:
    python gravitino_init.py [--create-metalake] [--create-catalogs] [--list]
"""

import os
import sys
import json
import argparse
import urllib.request
import ssl
from datetime import datetime
from typing import Dict, List, Any, Optional

# 配置
DEFAULT_GRAVITINO_HOST = os.environ.get("GRAVITINO_HOST", "localhost")
DEFAULT_GRAVITINO_PORT = os.environ.get("GRAVITINO_PORT", "8090")
GRAVITINO_BASE_URL = f"http://{DEFAULT_GRAVITINO_HOST}:{DEFAULT_GRAVITINO_PORT}"

# 禁用 SSL 警告
ssl._create_default_https_context = ssl._create_unverified_context


class GravitinoClient:
    """Gravitino REST API 客户端"""
    
    def __init__(self, host: str = None, port: int = None):
        self.base_url = host or DEFAULT_GRAVITINO_HOST
        if port:
            self.base_url = f"http://{host}:{port}"
        self.base_url = os.environ.get("GRAVITINO_URL", self.base_url)
        
        print(f"[Gravitino] Client initialized: {self.base_url}")
    
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
                if response.status < 400:
                    result = response.read().decode('utf-8')
                    return json.loads(result) if result else {}
                else:
                    print(f"[Gravitino] HTTP {response.status}")
                    return None
                    
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if e.fp else ""
            print(f"[Gravitino] HTTP Error {e.code}: {error_body[:200]}")
            return None
        except Exception as e:
            print(f"[Gravitino] Error: {e}")
            return None
    
    # ========== Metalake 操作 ==========
    
    def list_metalakes(self) -> List[Dict]:
        """列出所有 Metalakes"""
        result = self._request("GET", "/metalakes")
        return result.get("metalakes", []) if result else []
    
    def create_metalake(self, name: str, comment: str = "") -> Optional[Dict]:
        """创建 Metalake"""
        data = {
            "name": name,
            "comment": comment,
        }
        return self._request("POST", "/metalakes", data)
    
    def get_metalake(self, name: str) -> Optional[Dict]:
        """获取 Metalake 详情"""
        return self._request("GET", f"/metalakes/{name}")
    
    def delete_metalake(self, name: str) -> bool:
        """删除 Metalake"""
        result = self._request("DELETE", f"/metalakes/{name}")
        return result is not None
    
    # ========== Catalog 操作 ==========
    
    def list_catalogs(self, metalake: str) -> List[Dict]:
        """列出 Catalog"""
        result = self._request("GET", f"/metalakes/{metalake}/catalogs")
        return result.get("catalogs", []) if result else []
    
    def create_catalog(self, metalake: str, catalog: Dict) -> Optional[Dict]:
        """创建 Catalog"""
        return self._request("POST", f"/metalakes/{metalake}/catalogs", catalog)
    
    def get_catalog(self, metalake: str, catalog: str) -> Optional[Dict]:
        """获取 Catalog 详情"""
        return self._request("GET", f"/metalakes/{metalake}/catalogs/{catalog}")
    
    def delete_catalog(self, metalake: str, catalog: str) -> bool:
        """删除 Catalog"""
        result = self._request("DELETE", f"/metalakes/{metalake}/catalogs/{catalog}")
        return result is not None
    
    # ========== Schema 操作 ==========
    
    def list_schemas(self, metalake: str, catalog: str) -> List[Dict]:
        """列出 Schema"""
        result = self._request("GET", f"/metalakes/{metalake}/catalogs/{catalog}/schemas")
        return result.get("schemas", []) if result else []
    
    def create_schema(self, metalake: str, catalog: str, schema: Dict) -> Optional[Dict]:
        """创建 Schema"""
        return self._request("POST", f"/metalakes/{metalake}/catalogs/{catalog}/schemas", schema)
    
    # ========== Table 操作 ==========
    
    def list_tables(self, metalake: str, catalog: str, schema: str) -> List[Dict]:
        """列出 Table"""
        result = self._request("GET", f"/metalakes/{metalake}/catalogs/{catalog}/schemas/{schema}/tables")
        return result.get("tables", []) if result else []
    
    def create_table(self, metalake: str, catalog: str, schema: str, table: Dict) -> Optional[Dict]:
        """创建 Table"""
        path = f"/metalakes/{metalake}/catalogs/{catalog}/schemas/{schema}/tables"
        return self._request("POST", path, table)
    
    def get_table(self, metalake: str, catalog: str, schema: str, table: str) -> Optional[Dict]:
        """获取 Table 详情"""
        path = f"/metalakes/{metalake}/catalogs/{catalog}/schemas/{schema}/tables/{table}"
        return self._request("GET", path)


# ============================================================
# 预定义的 Metalake 和 Catalog 配置
# ============================================================

METALAKE_CONFIG = {
    "name": "lakehouse",
    "comment": "Personal Data Lakehouse - 所有数据表的元数据管理"
}

CATALOG_CONFIGS = [
    {
        "name": "iceberg-catalog",
        "type": "lakehouse-iceberg",
        "provider": "iceberg",
        "comment": "Iceberg 表存储",
        "properties": {
            "uri": " thrift://hive-metastore:9083",
            "warehouse": "s3://lakehouse-warehouse/",
            "s3.endpoint": "http://minio:9000",
            "s3.access-key": "minioadmin",
            "s3.secret-key": "minioadmin",
        }
    },
    {
        "name": "lakeform-catalog", 
        "type": "relational",
        "provider": "mysql",
        "comment": "关系型数据存储",
        "properties": {
            "uri": "mysql://mysql:3306/lakehouse",
            "user": "lakehouse",
            "password": "lakehouse123",
        }
    }
]

# Schema 定义 (对应 SQL 中的 Bronze/Silver/Gold)
SCHEMA_CONFIGS = [
    {
        "name": "bronze",
        "comment": "Bronze 层 - 原始数据"
    },
    {
        "name": "silver", 
        "comment": "Silver 层 - 清洗后数据"
    },
    {
        "name": "gold",
        "comment": "Gold 层 - 聚合统计"
    }
]


def init_lakehouse(client: GravitinoClient):
    """初始化 Lakehouse 元数据"""
    
    print("\n" + "=" * 60)
    print("初始化 Personal Data Lakehouse 元数据")
    print("=" * 60)
    
    # 1. 创建 Metalake
    print("\n[1] 创建 Metalake: lakehouse")
    metalake = client.get_metalake("lakehouse")
    if metalake:
        print("  -> Metalake 已存在")
    else:
        result = client.create_metalake("lakehouse", "Personal Data Lakehouse")
        if result:
            print("  -> Metalake 创建成功 ✓")
        else:
            print("  -> Metalake 创建失败 ✗")
            return
    
    # 2. 创建 Catalogs
    print("\n[2] 创建 Catalogs")
    for cat_config in CATALOG_CONFIGS:
        name = cat_config["name"]
        print(f"  - {name}")
        
        existing = client.get_catalog("lakehouse", name)
        if existing:
            print(f"    -> 已存在，跳过")
            continue
        
        result = client.create_catalog("lakehouse", cat_config)
        if result:
            print(f"    -> 创建成功 ✓")
        else:
            print(f"    -> 创建失败 ✗")
    
    # 3. 创建 Schemas
    print("\n[3] 创建 Schemas")
    for schema_config in SCHEMA_CONFIGS:
        name = schema_config["name"]
        print(f"  - {name}")
        
        schemas = client.list_schemas("lakehouse", "iceberg-catalog")
        if any(s.get("name") == name for s in schemas):
            print(f"    -> 已存在，跳过")
            continue
        
        result = client.create_schema("lakehouse", "iceberg-catalog", {
            "name": name,
            "comment": schema_config["comment"],
            "properties": {}
        })
        if result:
            print(f"    -> 创建成功 ✓")
        else:
            print(f"    -> 创建失败 ✗")
    
    print("\n" + "=" * 60)
    print("初始化完成!")
    print("=" * 60)


def list_metadata(client: GravitinoClient):
    """列出所有元数据"""
    
    print("\n" + "=" * 60)
    print("Lakehouse 元数据")
    print("=" * 60)
    
    # Metalakes
    print("\n[Metalakes]")
    metalakes = client.list_metalakes()
    for m in metalakes:
        print(f"  - {m.get('name')}: {m.get('comment', '')}")
    
    # Catalogs
    print("\n[Catalogs]")
    catalogs = client.list_catalogs("lakehouse")
    for c in catalogs:
        print(f"  - {c.get('name')} ({c.get('type')})")
    
    # Schemas
    print("\n[Schemas]")
    try:
        schemas = client.list_schemas("lakehouse", "iceberg-catalog")
        for s in schemas:
            print(f"  - {s.get('name')}: {s.get('comment', '')}")
    except:
        print("  (无法获取，请确认服务运行)")
    
    # Tables
    print("\n[Tables]")
    try:
        for schema in ["bronze", "silver", "gold"]:
            tables = client.list_tables("lakehouse", "iceberg-catalog", schema)
            if tables:
                print(f"  {schema}:")
                for t in tables:
                    print(f"    - {t.get('name')}")
    except:
        print("  (无法获取，请确认服务运行)")


def main():
    parser = argparse.ArgumentParser(description='Gravitino Schema Registry Tool')
    parser.add_argument('--host', default=DEFAULT_GRAVITINO_HOST)
    parser.add_argument('--port', type=int, default=DEFAULT_GRAVITINO_PORT)
    parser.add_argument('--init', action='store_true', help='初始化元数据')
    parser.add_argument('--list', action='store_true', help='列出所有元数据')
    
    args = parser.parse_args()
    
    client = GravitinoClient(host=args.host, port=args.port)
    
    if args.init:
        init_lakehouse(client)
    elif args.list:
        list_metadata(client)
    else:
        print("使用 --init 初始化 或 --list 查看")
        print("示例: python gravitino_init.py --init")


if __name__ == '__main__':
    main()
"""Trino Client Service - 使用原生HTTP API"""
import requests
from typing import List, Dict, Any, Optional
from config import TRINO_HOST, TRINO_PORT, TRINO_USER, TRINO_CATALOG
import logging
import time

logger = logging.getLogger(__name__)


class TrinoClient:
    """Trino数据库客户端 - 直接使用REST API"""
    
    def __init__(self):
        self.base_url = f"http://{TRINO_HOST}:{TRINO_PORT}"
        self.headers = {
            "X-Trino-User": TRINO_USER,
            "X-Trino-Catalog": TRINO_CATALOG,
        }
    
    def _execute_query(self, sql: str, max_retries=3) -> requests.Response:
        """执行SQL查询 - 轮询直到完成"""
        # 发起查询
        response = requests.post(
            f"{self.base_url}/v1/statement",
            headers=self.headers,
            data=sql,
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"Query failed: {response.status_code} {response.text}")
        
        data = response.json()
        query_id = data.get("id")
        
        # 轮询直到查询完成
        while True:
            if "nextUri" in data:
                # 继续获取结果
                next_uri = data["nextUri"]
                response = requests.get(next_uri, timeout=30)
                data = response.json()
            elif "data" in data:
                # 有数据了，返回data
                return data
            elif data.get("stats", {}).get("state") == "FINISHED":
                # 查询完成
                return data
            else:
                break
        
        return data
    
    def execute(self, sql: str) -> List[Dict[str, Any]]:
        """执行SQL查询"""
        try:
            data = self._execute_query(sql)
            
            if "data" not in data:
                return []
            
            # 获取列名
            columns = data.get("columns", [])
            if not columns:
                return []
            
            col_names = [c["name"] for c in columns]
            
            # 转换为字典列表
            results = []
            for row in data["data"]:
                results.append({col: val for col, val in zip(col_names, row)})
            
            return results
        except Exception as e:
            logger.error(f"Query error: {e}")
            raise
    
    def get_schemas(self) -> List[str]:
        """获取所有schema"""
        result = self.execute(f"SHOW SCHEMAS FROM {TRINO_CATALOG}")
        return [r['Schema'] for r in result]
    
    def get_tables(self, schema: str = "default") -> List[str]:
        """获取指定schema的所有表"""
        result = self.execute(f"SHOW TABLES FROM {schema}")
        return [r['Table'] for r in result]
    
    def get_table_schema(self, schema: str, table: str) -> List[Dict[str, str]]:
        """获取表的列信息"""
        result = self.execute(f"DESCRIBE {schema}.{table}")
        return [
            {
                'Column': r.get('Column', ''),
                'Type': r.get('Type', ''),
                'Comment': r.get('Comment'),
                'Nullable': r.get('Nullable', 'YES')
            }
            for r in result
        ]
    
    def get_table_metadata(self, schema: str, table: str) -> Dict[str, Any]:
        """获取表的基本信息"""
        sql = f"""
            SELECT 
                table_name,
                table_type,
                table_owner as owner
            FROM information_schema.tables 
            WHERE table_schema = '{schema}' AND table_name = '{table}'
        """
        results = self.execute(sql)
        return results[0] if results else {}
    
    def get_partitions(self, schema: str, table: str) -> List[Dict[str, Any]]:
        """获取表的分区信息"""
        return []
    
    def get_table_stats(self, schema: str, table: str) -> Dict[str, Any]:
        """获取表的统计信息"""
        sql = f"SELECT count(*) as row_count FROM {schema}.{table}"
        try:
            results = self.execute(sql)
            return results[0] if results else {'row_count': 0}
        except Exception:
            return {'row_count': 0}


# 全局客户端实例
_client: Optional[TrinoClient] = None


def get_trino_client() -> TrinoClient:
    """获取Trino客户端单例"""
    global _client
    if _client is None:
        _client = TrinoClient()
    return _client
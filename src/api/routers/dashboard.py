"""Dashboard Endpoints - Summary statistics"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Dict, Any
from auth import api_key_auth
from services.trino_client import get_trino_client

router = APIRouter()


class DashboardStats(BaseModel):
    """仪表盘统计"""
    total_schemas: int
    total_tables: int
    tables_by_schema: Dict[str, int]


@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(api_key: str = Depends(api_key_auth)):
    """获取仪表盘统计信息"""
    client = get_trino_client()
    
    # 获取所有schema
    schemas = client.get_schemas()
    
    # 统计每个schema的表数量
    tables_by_schema = {}
    total_tables = 0
    
    for schema in schemas:
        try:
            tables = client.get_tables(schema)
            tables_by_schema[schema] = len(tables)
            total_tables += len(tables)
        except Exception:
            tables_by_schema[schema] = 0
    
    return DashboardStats(
        total_schemas=len(schemas),
        total_tables=total_tables,
        tables_by_schema=tables_by_schema
    )


@router.get("/dashboard/recent-tables")
async def get_recent_tables(
    limit: int = 10,
    api_key: str = Depends(api_key_auth)
):
    """获取最近的表（按schema分组）"""
    client = get_trino_client()
    schemas = client.get_schemas()
    
    all_tables = []
    for schema in schemas:
        try:
            tables = client.get_tables(schema)
            for t in tables:
                all_tables.append({
                    "schema": schema,
                    "table": t
                })
        except Exception:
            pass
    
    # 返回前N个
    return all_tables[:limit]


@router.get("/dashboard/table-counts")
async def get_table_counts(api_key: str = Depends(api_key_auth)):
    """获取每个schema的表数量"""
    client = get_trino_client()
    schemas = client.get_schemas()
    
    counts = []
    for schema in schemas:
        try:
            tables = client.get_tables(schema)
            counts.append({
                "schema": schema,
                "count": len(tables)
            })
        except Exception:
            counts.append({
                "schema": schema,
                "count": 0
            })
    
    return {"schemas": counts}
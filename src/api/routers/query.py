"""Query Endpoints - Data query"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from auth import api_key_auth
from services.trino_client import get_trino_client
from config import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE

router = APIRouter()


class QueryRequest(BaseModel):
    """查询请求"""
    sql: str
    limit: Optional[int] = DEFAULT_PAGE_SIZE


class QueryResponse(BaseModel):
    """查询响应"""
    columns: List[str]
    rows: List[Dict[str, Any]]
    total_rows: int
    execution_time_ms: float


@router.post("/query", response_model=QueryResponse)
async def execute_query(
    request: QueryRequest,
    api_key: str = Depends(api_key_auth)
):
    """执行SQL查询"""
    import time
    client = get_trino_client()
    
    start_time = time.time()
    try:
        # 添加LIMIT如果沒有
        sql = request.sql.strip()
        if "limit" not in sql.lower():
            sql = f"{sql} LIMIT {request.limit}"
        
        results = client.execute(sql)
        execution_time = (time.time() - start_time) * 1000
        
        columns = list(results[0].keys()) if results else []
        
        return QueryResponse(
            columns=columns,
            rows=results,
            total_rows=len(results),
            execution_time_ms=round(execution_time, 2)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Query failed: {str(e)}")


@router.get("/query/table/{schema}/{table}")
async def query_table(
    schema: str,
    table: str,
    columns: Optional[str] = Query(None, description="逗号分隔的列名"),
    where: Optional[str] = Query(None, description="WHERE条件"),
    order_by: Optional[str] = Query(None, description="排序字段"),
    limit: int = Query(DEFAULT_PAGE_SIZE, le=MAX_PAGE_SIZE),
    offset: int = Query(0, ge=0),
    api_key: str = Depends(api_key_auth)
):
    """查询表数据"""
    client = get_trino_client()
    
    try:
        # 构建SELECT语句
        col_list = columns if columns else "*"
        sql = f"SELECT {col_list} FROM {schema}.{table}"
        
        if where:
            sql += f" WHERE {where}"
        
        if order_by:
            sql += f" ORDER BY {order_by}"
        
        sql += f" LIMIT {limit} OFFSET {offset}"
        
        results = client.execute(sql)
        columns_list = list(results[0].keys()) if results else []
        
        return QueryResponse(
            columns=columns_list,
            rows=results,
            total_rows=len(results),
            execution_time_ms=0
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Query failed: {str(e)}")


@router.get("/query/sql-history")
async def get_query_history(api_key: str = Depends(api_key_auth)):
    """获取查询历史（简化版，当前返回空）"""
    return {"history": []}
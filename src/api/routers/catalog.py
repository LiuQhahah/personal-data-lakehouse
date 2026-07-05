"""Catalog Endpoints - Schema/Table metadata"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from auth import api_key_auth
from services.trino_client import get_trino_client

router = APIRouter()


class SchemaInfo(BaseModel):
    """Schema信息"""
    name: str


class TableInfo(BaseModel):
    """表信息"""
    name: str
    type: Optional[str] = None
    owner: Optional[str] = None


class ColumnInfo(BaseModel):
    """列信息"""
    name: str
    type: str
    comment: Optional[str] = None
    nullable: bool = True


@router.get("/schemas", response_model=List[SchemaInfo])
async def list_schemas(api_key: str = Depends(api_key_auth)):
    """获取所有Schema"""
    client = get_trino_client()
    schemas = client.get_schemas()
    return [SchemaInfo(name=s) for s in schemas]


@router.get("/schemas/{schema}/tables", response_model=List[TableInfo])
async def list_tables(schema: str, api_key: str = Depends(api_key_auth)):
    """获取指定Schema的所有表"""
    client = get_trino_client()
    try:
        tables = client.get_tables(schema)
        return [TableInfo(name=t) for t in tables]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")


@router.get("/schemas/{schema}/tables/{table}/schema", response_model=List[ColumnInfo])
async def get_table_schema(schema: str, table: str, api_key: str = Depends(api_key_auth)):
    """获取表的列信息"""
    client = get_trino_client()
    try:
        columns = client.get_table_schema(schema, table)
        return [
            ColumnInfo(
                name=c['Column'],
                type=c['Type'],
                comment=c.get('Comment'),
                nullable=c.get('Nullable', 'YES') == 'YES'
            )
            for c in columns
        ]
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Table not found: {str(e)}")


@router.get("/schemas/{schema}/tables/{table}/metadata")
async def get_table_metadata(schema: str, table: str, api_key: str = Depends(api_key_auth)):
    """获取表的元数据信息"""
    client = get_trino_client()
    try:
        metadata = client.get_table_metadata(schema, table)
        stats = client.get_table_stats(schema, table)
        partitions = client.get_partitions(schema, table)
        
        return {
            "table_name": table,
            "schema": schema,
            **metadata,
            **stats,
            "partitions": partitions[:10] if partitions else []  # 限制返回数量
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Error: {str(e)}")
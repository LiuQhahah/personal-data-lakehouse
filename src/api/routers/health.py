"""Health Check Endpoints"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    version: str = "1.0.0"


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """服务健康检查"""
    return HealthResponse(status="healthy")


@router.get("/health/ready", response_model=HealthResponse)
async def readiness_check():
    """就绪检查"""
    return HealthResponse(status="ready")


@router.get("/health/live", response_model=HealthResponse)
async def liveness_check():
    """存活检查"""
    return HealthResponse(status="alive")
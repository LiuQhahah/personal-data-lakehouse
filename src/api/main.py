"""Personal Lakehouse API - Main Entry"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import API_HOST, API_PORT, CORS_ORIGINS
from routers import health, catalog, query, dashboard

app = FastAPI(
    title="Personal Lakehouse API",
    version="1.0.0",
    description="REST API for Personal Data Lakehouse - Query and manage your data"
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(catalog.router, prefix="/api/v1", tags=["Catalog"])
app.include_router(query.router, prefix="/api/v1", tags=["Query"])
app.include_router(dashboard.router, prefix="/api/v1", tags=["Dashboard"])


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "Personal Lakehouse API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "health": "/api/v1/health",
            "schemas": "/api/v1/schemas",
            "query": "/api/v1/query"
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=API_HOST,
        port=API_PORT,
        reload=True
    )
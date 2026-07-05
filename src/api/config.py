"""Configuration for Lakehouse API"""
import os

# Trino配置
TRINO_HOST = os.getenv("TRINO_HOST", "localhost")
TRINO_PORT = os.getenv("TRINO_PORT", "8085")
TRINO_USER = os.getenv("TRINO_USER", "lakehouse")
TRINO_CATALOG = os.getenv("TRINO_CATALOG", "memory")

# Gravitino配置
GRAVITINO_HOST = os.getenv("GRAVITINO_HOST", "localhost")
GRAVITINO_PORT = os.getenv("GRAVITINO_PORT", "8090")

# API配置
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_KEY = os.getenv("API_KEY", "lakehouse-secret-key-change-in-production")

# CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# 默认分页
DEFAULT_PAGE_SIZE = 100
MAX_PAGE_SIZE = 10000
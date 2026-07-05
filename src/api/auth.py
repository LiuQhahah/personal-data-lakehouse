"""Authentication - API Key"""
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from config import API_KEY

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def api_key_auth(api_key: str = Depends(api_key_header)):
    """验证API密钥"""
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key. Add 'X-API-Key' header."
        )
    
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key"
        )
    
    return api_key
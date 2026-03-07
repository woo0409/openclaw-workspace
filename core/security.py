"""
安全认证模块

提供 API Key 验证功能，用于保护 API 的写操作。
"""
from fastapi import Header, HTTPException, status

from core.config import settings


async def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")):
    """
    验证 API Key

    Args:
        x_api_key: API Key（从 Header 中获取）

    Returns:
        验证通过返回 API Key

    Raises:
        HTTPException: API Key 无效或缺失
    """
    # 检查 API Key 是否存在
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key is required. Please provide X-API-Key header."
        )

    # 验证 API Key
    if x_api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key. Access denied."
        )

    return x_api_key

from typing import Optional

from fastapi import Depends, HTTPException, Request, status  # Added Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from scheduler_service.models import User

# 创建Bearer认证方案
security = HTTPBearer(auto_error=False)


async def login_require(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> User:
    """获取当前认证用户"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = credentials.credentials
    secret_key = request.app.config.get("SECRET_KEY") # Retrieve secret_key
    print(f"DEBUG: get_current_user using secret_key: {secret_key}") # Temporary print for debugging

    # 从token中验证用户
    # 这里需要调整User.verify_auth_token方法以适应FastAPI
    user = await User.verify_auth_token(token, secret_key) # Pass secret_key

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user

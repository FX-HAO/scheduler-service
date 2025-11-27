from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr
from tortoise.exceptions import DoesNotExist, IntegrityError

from scheduler_service.api.decorators import login_require
from scheduler_service.models import User


# Pydantic模型
def to_camel(string: str) -> str:
    """将snake_case转换为camelCase"""
    components = string.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


class UserCreate(BaseModel):
    """用户创建模型"""
    name: str
    password: str
    email: EmailStr


class UserUpdate(BaseModel):
    """用户更新模型"""
    name: str | None = None
    email: EmailStr | None = None
    password: str | None = None


class UserResponse(BaseModel):
    """用户响应模型"""
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True


class TokenRequest(BaseModel):
    """Token请求模型"""
    name: str | None = None
    email: str | None = None
    password: str


class TokenResponse(BaseModel):
    """Token响应模型"""
    token: str


async def create_user(user_data: UserCreate):
    """创建新用户"""
    try:
        # 创建用户
        password_hash = User.hash_password(user_data.password)
        user = await User.create(
            name=user_data.name,
            password_hash=password_hash,
            email=user_data.email
        )
        return {'uid': user.id}
    except IntegrityError as e:
        if "name" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        elif "email" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已存在"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="创建用户失败"
            )


async def get_current_user_info(current_user: User = Depends(login_require)):
    """获取当前用户信息"""
    return current_user.to_dict()


async def update_user(user_data: UserUpdate, current_user: User = Depends(login_require)):
    """更新用户信息"""
    update_data = {}

    # 处理密码更新
    if user_data.password:
        update_data['password_hash'] = User.hash_password(user_data.password)

    # 处理其他字段更新
    if user_data.name:
        update_data['name'] = user_data.name
    if user_data.email:
        update_data['email'] = user_data.email

    # 执行更新
    if update_data:
        await User.filter(id=current_user.id).update(**update_data)
        # 重新获取更新后的用户信息
        updated_user = await User.get(id=current_user.id)
        return updated_user.to_dict()

    return current_user.to_dict()


async def delete_user(current_user: User = Depends(login_require)):
    """删除当前用户"""
    await current_user.delete()
    return {"message": "用户已删除"}


async def get_token(token_data: TokenRequest, request: Request):
    """获取认证token"""
    # 验证请求参数
    if not token_data.name and not token_data.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请输入用户名或邮箱"
        )

    try:
        # 根据用户名或邮箱查找用户
        if token_data.name:
            user = await User.get(name=token_data.name)
        else:
            user = await User.get(email=token_data.email)
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 验证密码
    if not user.verify_password(token_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 更新登录时间
    await user.ping()

    # 生成token
    secret_key = request.app.config.get("SECRET_KEY")
    token = user.generate_auth_token(secret_key)

    return {"token": token}

router = APIRouter()

# 用户管理
router.add_api_route("", create_user, methods=["POST"])
router.add_api_route("/me", get_current_user_info, methods=["GET"])
router.add_api_route("/me", update_user, methods=["PUT"])
router.add_api_route("/me", delete_user, methods=["DELETE"])

# Token
router.add_api_route("/token", get_token, methods=["POST"])

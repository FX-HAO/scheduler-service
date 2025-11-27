from scheduler_service.models import User
from tests import const


class TestUserModel:
    """测试User模型"""

    async def test_create_user(self, app):
        """测试创建用户"""
        password_hash = User.hash_password("password")
        user = await User.create(
            name="test_user",
            password_hash=password_hash,
            email="test_user@test.com",
            verify=True
        )

        assert user.name == "test_user"
        assert user.email == "test_user@test.com"
        assert user.verify is True
        assert user.register_time is not None

        # 清理
        await user.delete()

    async def test_password_hashing(self, app):
        """测试密码哈希"""
        password = "test_password"
        password_hash = User.hash_password(password)

        # 确保哈希不等于原始密码
        assert password_hash != password

        # 验证密码
        user = await User.create(
            name="hash_test",
            password_hash=password_hash,
            email="hash_test@test.com"
        )

        assert user.verify_password(password) is True
        assert user.verify_password("wrong_password") is False

        # 清理
        await user.delete()

    async def test_ping(self, app):
        """测试更新登录时间"""
        user = await User.create(
            name="ping_test",
            password_hash=User.hash_password("password"),
            email="ping_test@test.com"
        )

        original_login_time = user.login_time
        await user.ping()

        # 重新获取用户以检查更新
        updated_user = await User.get(id=user.id)
        assert updated_user.login_time != original_login_time

        # 清理
        await updated_user.delete()

    async def test_generate_auth_token(self, app):
        """测试生成认证令牌"""
        user = await User.create(
            name="token_test",
            password_hash=User.hash_password("password"),
            email="token_test@test.com"
        )

        token = user.generate_auth_token(app.config["SECRET_KEY"])
        assert isinstance(token, str)
        assert len(token) > 0

        # 清理
        await user.delete()

    async def test_verify_auth_token(self, app):
        """测试验证认证令牌"""
        user = await User.create(
            name="verify_test",
            password_hash=User.hash_password("password"),
            email="verify_test@test.com"
        )

        # 生成令牌
        token = user.generate_auth_token(app.config["SECRET_KEY"])

        # 验证令牌
        verified_user = await User.verify_auth_token(token, app.config["SECRET_KEY"])
        assert verified_user.id == user.id
        assert verified_user.name == user.name

        # 测试无效令牌
        invalid_user = await User.verify_auth_token("invalid_token", app.config["SECRET_KEY"])
        assert invalid_user is False

        # 清理
        await user.delete()

    async def test_to_dict(self, app):
        """测试转换为字典"""
        password_hash = User.hash_password("password")
        user = await User.create(
            name="dict_test",
            password_hash=password_hash,
            email="dict_test@test.com"
        )

        user_dict = user.to_dict()
        assert isinstance(user_dict, dict)
        assert user_dict["id"] == user.id
        assert user_dict["name"] == "dict_test"
        assert user_dict["email"] == "dict_test@test.com"

        # 清理
        await user.delete()


class TestUserAPI:
    """测试用户API端点"""

    async def test_create_user(self, client):
        """测试创建用户API"""
        user_data = {
            "name": "api_test_user",
            "password": "password",
            "email": "api_test@test.com"
        }

        resp = await client.post(const.USER_URL, json=user_data)
        assert resp.status_code == 200
        response_data = resp.json()
        assert "uid" in response_data

    async def test_create_duplicate_user(self, client):
        """测试创建重复用户"""
        user_data = {
            "name": "duplicate_user",
            "password": "password",
            "email": "duplicate@test.com"
        }

        # 创建第一个用户
        resp = await client.post(const.USER_URL, json=user_data)
        assert resp.status_code == 200

        # 尝试创建同名用户 (但邮箱不同)
        resp = await client.post(const.USER_URL, json={
            "name": "duplicate_user",
            "password": "password",
            "email": "dup_name_diff_email@test.com"
        })
        assert resp.status_code == 400
        assert "用户名已存在" in resp.json().get("detail", "")

        # 尝试创建同邮箱用户 (但用户名不同)
        resp = await client.post(const.USER_URL, json={
            "name": "different_name",
            "password": "password",
            "email": "duplicate@test.com"
        })
        assert resp.status_code == 400
        assert "邮箱已存在" in resp.json().get("detail", "")

    async def test_get_token_with_name(self, client):
        """测试使用用户名获取令牌"""
        # 创建用户
        user_data = {
            "name": "token_name_test",
            "password": "password",
            "email": "token_name@test.com"
        }
        resp = await client.post(const.USER_URL, json=user_data)
        assert resp.status_code == 200

        # 获取令牌
        resp = await client.post(const.AUTH_TOKEN_URL, json={
            "name": "token_name_test",
            "password": "password"
        })
        assert resp.status_code == 200
        response_data = resp.json()
        assert "token" in response_data

    async def test_get_token_with_email(self, client):
        """测试使用邮箱获取令牌"""
        # 创建用户
        user_data = {
            "name": "token_email_test",
            "password": "password",
            "email": "token_email@test.com"
        }
        resp = await client.post(const.USER_URL, json=user_data)
        assert resp.status_code == 200

        # 获取令牌
        resp = await client.post(const.AUTH_TOKEN_URL, json={
            "email": "token_email@test.com",
            "password": "password"
        })
        assert resp.status_code == 200
        response_data = resp.json()
        assert "token" in response_data

    async def test_get_token_invalid_credentials(self, client):
        """测试使用无效凭据获取令牌"""
        # 创建用户
        user_data = {
            "name": "invalid_test",
            "password": "password",
            "email": "invalid@test.com"
        }
        resp = await client.post(const.USER_URL, json=user_data)
        assert resp.status_code == 200

        # 使用错误密码
        resp = await client.post(const.AUTH_TOKEN_URL, json={
            "name": "invalid_test",
            "password": "wrong_password"
        })
        assert resp.status_code == 401

        # 使用不存在的用户
        resp = await client.post(const.AUTH_TOKEN_URL, json={
            "name": "nonexistent_user",
            "password": "password"
        })
        assert resp.status_code == 401

    async def test_get_token_missing_credentials(self, client):
        """测试缺少凭据时获取令牌"""
        # 不提供用户名或邮箱
        resp = await client.post(const.AUTH_TOKEN_URL, json={
            "password": "password"
        })
        assert resp.status_code == 400
        assert "请输入用户名或邮箱" in resp.json().get("detail", "")

    async def test_get_current_user_info(self, client):
        """测试获取当前用户信息"""
        # 创建用户
        user_data = {
            "name": "current_user_test",
            "password": "password",
            "email": "current_user@test.com"
        }
        resp = await client.post(const.USER_URL, json=user_data)
        assert resp.status_code == 200

        # 获取令牌
        resp = await client.post(const.AUTH_TOKEN_URL, json={
            "name": "current_user_test",
            "password": "password"
        })
        assert resp.status_code == 200
        token = resp.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 获取用户信息
        resp = await client.get(f"{const.USER_URL}/me", headers=headers)
        assert resp.status_code == 200
        response_data = resp.json()
        assert response_data["name"] == "current_user_test"
        assert response_data["email"] == "current_user@test.com"
        assert "password_hash" not in response_data

    async def test_update_user(self, client):
        """测试更新用户信息"""
        # 创建用户
        user_data = {
            "name": "update_test",
            "password": "password",
            "email": "update@test.com"
        }
        resp = await client.post(const.USER_URL, json=user_data)
        assert resp.status_code == 200

        # 获取令牌
        resp = await client.post(const.AUTH_TOKEN_URL, json={
            "name": "update_test",
            "password": "password"
        })
        assert resp.status_code == 200
        token = resp.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 更新用户信息
        update_data = {
            "name": "updated_name",
            "email": "updated@test.com"
        }
        resp = await client.put(f"{const.USER_URL}/me", headers=headers, json=update_data)
        assert resp.status_code == 200
        response_data = resp.json()
        assert response_data["name"] == "updated_name"
        assert response_data["email"] == "updated@test.com"

        # 更新密码
        password_data = {
            "password": "new_password"
        }
        resp = await client.put(f"{const.USER_URL}/me", headers=headers, json=password_data)
        assert resp.status_code == 200

        # 验证新密码
        resp = await client.post(const.AUTH_TOKEN_URL, json={
            "name": "updated_name",
            "password": "new_password"
        })
        assert resp.status_code == 200

        # 验证旧密码不再有效
        resp = await client.post(const.AUTH_TOKEN_URL, json={
            "name": "updated_name",
            "password": "password"
        })
        assert resp.status_code == 401

    async def test_delete_user(self, client):
        """测试删除用户"""
        # 创建用户
        user_data = {
            "name": "delete_test",
            "password": "password",
            "email": "delete@test.com"
        }
        resp = await client.post(const.USER_URL, json=user_data)
        assert resp.status_code == 200

        # 获取令牌
        resp = await client.post(const.AUTH_TOKEN_URL, json={
            "name": "delete_test",
            "password": "password"
        })
        assert resp.status_code == 200
        token = resp.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 删除用户
        resp = await client.delete(f"{const.USER_URL}/me", headers=headers)
        assert resp.status_code == 200
        response_data = resp.json()
        assert "用户已删除" in response_data.get("message", "")

        # 验证用户已被删除
        resp = await client.post(const.AUTH_TOKEN_URL, json={
            "name": "delete_test",
            "password": "password"
        })
        assert resp.status_code == 401

    async def test_unauthorized_access(self, client):
        """测试未授权访问"""
        # 不带认证头访问
        resp = await client.get(f"{const.USER_URL}/me")
        assert resp.status_code == 401

        resp = await client.put(f"{const.USER_URL}/me", json={"name": "test"})
        assert resp.status_code == 401

        resp = await client.delete(f"{const.USER_URL}/me")
        assert resp.status_code == 401

    async def test_invalid_token(self, client):
        """测试无效令牌"""
        # 使用无效令牌
        headers = {"Authorization": "invalid_token"}

        resp = await client.get(f"{const.USER_URL}/me", headers=headers)
        assert resp.status_code == 401

        resp = await client.put(f"{const.USER_URL}/me", headers=headers, json={"name": "test"})
        assert resp.status_code == 401

        resp = await client.delete(f"{const.USER_URL}/me", headers=headers)
        assert resp.status_code == 401

    async def test_invalid_user_data(self, client):
        """测试无效的用户数据"""
        # 缺少必需字段
        resp = await client.post(const.USER_URL, json={})
        assert resp.status_code == 422

        # 无效邮箱
        resp = await client.post(const.USER_URL, json={
            "name": "test",
            "password": "password",
            "email": "invalid_email"
        })
        assert resp.status_code == 422

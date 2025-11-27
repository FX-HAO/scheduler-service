# 测试覆盖率指南

本项目使用pytest进行测试，并配置了测试覆盖率报告。

## 安装依赖

首先安装项目依赖和测试依赖：

```bash
pip install -e .
pip install -e ".[dev]"
```

或者使用poetry：

```bash
poetry install --with dev
```

## 运行测试

### 基本测试

运行所有测试：

```bash
python -m pytest
```

运行特定测试文件：

```bash
python -m pytest tests/test_user.py
```

运行特定测试类：

```bash
python -m pytest tests/test_user.py::TestUserModel
```

运行特定测试方法：

```bash
python -m pytest tests/test_user.py::TestUserModel::test_create_user
```

### 使用测试脚本

我们提供了一个便捷的测试脚本 `run_tests.py`：

```bash
# 运行所有测试
python run_tests.py

# 运行测试并生成覆盖率报告
python run_tests.py --coverage

# 运行测试并生成覆盖率报告，设置覆盖率为90%
python run_tests.py --coverage --coverage-threshold 90

# 运行特定路径的测试
python run_tests.py --path tests/test_user.py

# 并行运行测试
python run_tests.py --parallel 4

# 显示详细输出
python run_tests.py --verbose
```

## 测试覆盖率

### 生成覆盖率报告

```bash
# 生成终端和HTML覆盖率报告
python -m pytest --cov=scheduler_service --cov-report=html:htmlcov --cov-report=term-missing

# 或者使用测试脚本
python run_tests.py --coverage
```

### 查看覆盖率报告

- 终端报告会直接显示在终端中
- HTML报告会生成在 `htmlcov/index.html` 文件中，可以在浏览器中打开查看

### 覆盖率配置

覆盖率配置在 `pytest.ini` 文件中：

```ini
[tool:pytest]
addopts = 
    --cov=scheduler_service
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-report=xml
    --cov-fail-under=80
```

默认覆盖率阈值为80%，可以在运行时通过 `--cov-fail-under` 参数覆盖：

```bash
python -m pytest --cov=scheduler_service --cov-fail-under=90
```

## 测试结构

测试文件位于 `tests/` 目录下：

- `test_user.py` - 用户模型和API测试
- `test_task.py` - 任务模型和API测试
- `conftest.py` - 测试配置和fixtures
- `const.py` - 测试常量

每个测试文件包含两个主要测试类：

1. 模型测试类 (如 `TestUserModel`) - 测试模型方法
2. API测试类 (如 `TestUserAPI`) - 测试API端点

## 编写新测试

### 添加模型测试

```python
class TestYourModel:
    async def test_model_method(self):
        # 创建模型实例
        instance = await YourModel.objects.create(...)
        
        # 断言
        assert instance.field == expected_value
        
        # 清理
        await instance.delete()
```

### 添加API测试

```python
class TestYourAPI:
    async def test_api_endpoint(self, client, headers):
        # 发送请求
        response = await client.get("/api/v1/endpoint", headers=headers)
        
        # 断言状态码
        assert response.status_code == 200
        
        # 断言响应内容
        data = response.json()
        assert data["field"] == expected_value
```

## 持续集成

测试覆盖率报告已集成到CI/CD流程中，每次提交都会运行测试并生成覆盖率报告。如果覆盖率低于配置的阈值，构建将失败。

## 常见问题

### 测试数据库连接问题

如果遇到数据库连接问题，请检查 `tests/conftest.py` 中的数据库配置。

### 异步测试问题

确保异步测试函数使用 `async def` 定义，并使用 `await` 调用异步方法。

### 测试隔离问题

每个测试应该独立运行，不依赖其他测试的状态。使用fixtures来设置测试数据和清理。
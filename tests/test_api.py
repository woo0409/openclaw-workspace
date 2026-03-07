"""
后端 API 测试示例

运行测试：
    pytest tests/ -v
    pytest tests/ --cov=.
"""
import pytest
from httpx import AsyncClient
from main import app


@pytest.fixture
async def client():
    """测试客户端"""
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        yield ac


class TestHealthCheck:
    """健康检查测试"""

    @pytest.mark.asyncio
    async def test_health_endpoint(self, client):
        """测试健康检查端点"""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "app" in data
        assert "version" in data


class TestRoot:
    """根路径测试"""

    @pytest.mark.asyncio
    async def test_root_endpoint(self, client):
        """测试根路径"""
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert data["status"] == "running"


# TODO: 添加更多测试用例
# - 测试供应商 API
# - 测试搜索 API
# - 测试数据库操作

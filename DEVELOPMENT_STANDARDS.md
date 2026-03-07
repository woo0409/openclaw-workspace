# 后端开发规范

本文档定义了后端项目的开发规范和最佳实践。所有贡献者应遵循这些规范以确保代码质量和一致性。

## 目录

1. [代码风格](#代码风格)
2. [项目结构](#项目结构)
3. [命名规范](#命名规范)
4. [文档规范](#文档规范)
5. [错误处理](#错误处理)
6. [日志规范](#日志规范)
7. [配置管理](#配置管理)
8. [测试规范](#测试规范)
9. [安全规范](#安全规范)
10. [Git工作流](#git工作流)

## 代码风格

### Python 代码规范

遵循 **PEP 8** 标准，使用以下工具确保代码质量：

```bash
# 代码格式化
pip install black
black backend/

# 类型检查
pip install mypy
mypy backend/

# 代码检查
pip install flake8
flake8 backend/
```

### 基本规则

1. **缩进**：使用 4 个空格
2. **行长度**：最大 120 字符
3. **导入顺序**：标准库 → 第三方库 → 本地模块
4. **空行**：函数间 2 行，类内方法间 1 行

### 示例

```python
# ✅ 正确的导入顺序
import os
from typing import List, Optional

from fastapi import FastAPI
from pydantic import BaseModel

from core.config import settings
from api.models import Supplier

# ✅ 正确的函数定义
def get_suppliers(
    db: Session,
    skip: int = 0,
    limit: int = 50
) -> List[Supplier]:
    """获取供应商列表"""
    return db.query(Supplier).offset(skip).limit(limit).all()
```

## 项目结构

### 目录组织

```
backend/
├── api/                    # API 层
│   ├── routes.py          # 路由定义
│   ├── models.py          # 数据模型
│   └── schemas.py         # Pydantic 模型
├── core/                  # 核心模块
│   ├── config.py          # 配置管理
│   ├── database.py        # 数据库连接
│   ├── security.py        # 安全认证
│   └── logger.py          # 日志配置
├── services/              # 业务服务层
│   ├── search.py          # 搜索服务
│   ├── supplier.py        # 供应商服务
│   └── dedupe.py          # 去重服务
├── scripts/               # 工具脚本
│   └── setup_env.py       # 环境配置工具
├── tests/                 # 测试目录
├── main.py               # 应用入口
├── .env.example          # 配置示例
└── requirements.txt      # 依赖列表
```

### 分层架构

1. **API 层** (`api/`)：处理 HTTP 请求和响应
2. **服务层** (`services/`)：业务逻辑实现
3. **核心层** (`core/`)：基础设施和配置
4. **数据层** (`api/models.py`)：数据库模型

## 命名规范

### 变量和函数

```python
# ✅ 函数名：小写，下划线分隔
def get_supplier_by_id(supplier_id: int):
    pass

# ✅ 变量名：小写，下划线分隔
user_name = "张三"
max_count = 100

# ❌ 避免
def getSupplierByID(supplierId):  # 驼峰命名
    pass
```

### 类和常量

```python
# ✅ 类名：大驼峰
class SupplierService:
    pass

# ✅ 常量：大写，下划线分隔
MAX_RESULTS = 100
DEFAULT_TIMEOUT = 30

# ❌ 避免
class supplierService:  # 小驼峰
    pass
```

### 私有成员

```python
# ✅ 私有方法/变量：前缀下划线
def _internal_method(self):
    pass

_private_var = "内部变量"
```

## 文档规范

### 模块文档

每个模块应包含描述性的文档字符串：

```python
"""
搜索服务模块

提供供应商搜索功能，集成 Tavily API。
支持多种搜索策略和结果去重。
"""
```

### 类文档

```python
class SearchService:
    """
    搜索服务类

    负责调用外部搜索 API 并处理返回结果。
    支持去重、验证和格式化功能。

    Attributes:
        tavily: Tavily API 客户端
        logger: 日志记录器
    """
```

### 函数文档

使用 Google 风格的文档字符串：

```python
def create_supplier(
    db: Session,
    supplier_data: SupplierCreate
) -> Optional[Supplier]:
    """
    创建新供应商

    Args:
        db: 数据库会话
        supplier_data: 供应商创建数据

    Returns:
        创建的供应商对象，失败返回 None

    Raises:
        ValueError: 当数据验证失败时
        DatabaseError: 当数据库操作失败时

    Example:
        >>> supplier = create_supplier(db, SupplierCreate(...))
        >>> print(supplier.id)
    """
```

## 错误处理

### 基本原则

1. **具体异常**：使用具体的异常类型
2. **适当处理**：不要捕获所有异常
3. **记录日志**：记录错误上下文
4. **清理资源**：使用 try-finally 或上下文管理器

### 示例

```python
# ✅ 正确的错误处理
def create_supplier(db: Session, data: SupplierCreate):
    try:
        supplier = Supplier(**data.model_dump())
        db.add(supplier)
        db.commit()
        return supplier
    except IntegrityError as e:
        db.rollback()
        logger.error(f"数据完整性错误: {e}")
        raise ValueError("供应商已存在")
    except Exception as e:
        db.rollback()
        logger.error(f"创建供应商失败: {e}")
        raise

# ❌ 避免
def create_supplier(db: Session, data: SupplierCreate):
    try:
        # ... 操作
        pass
    except:  # 捕获所有异常
        pass
```

### 自定义异常

```python
class SupplierNotFoundError(Exception):
    """供应商未找到异常"""
    pass

class InvalidSupplierDataError(Exception):
    """无效的供应商数据异常"""
    pass
```

## 日志规范

### 日志级别使用

```python
# DEBUG：详细的调试信息
logger.debug(f"处理供应商数据: {supplier_data}")

# INFO：重要的业务流程
logger.info(f"开始搜索供应商，查询: {query}")

# WARNING：异常但可恢复的情况
logger.warning(f"供应商已存在，跳过: {url}")

# ERROR：错误但不影响系统继续运行
logger.error(f"搜索失败: {e}")

# CRITICAL：严重错误，系统可能无法继续
logger.critical(f"数据库连接失败: {e}")
```

### 日志格式

系统已配置统一的日志格式：

```
时间 | 级别 | 模块:函数:行号 | 消息
```

### 最佳实践

1. **不要使用 print**：统一使用 logger
2. **记录关键信息**：包含上下文信息
3. **避免敏感信息**：不要记录密码、密钥等
4. **合理使用级别**：选择合适的日志级别

## 配置管理

### 配置原则

1. **敏感信息不硬编码**：使用环境变量
2. **分层配置**：环境变量 > .env > 默认值
3. **配置验证**：启动时验证必需配置
4. **配置文档**：提供配置示例和说明

### 使用配置

```python
from core.config import settings

# ✅ 使用配置
api_key = settings.TAVILY_API_KEY
if settings.DEBUG:
    logger.debug("调试模式")

# ❌ 避免
api_key = "tvly-dev-xxxxx"  # 硬编码
```

### 新增配置项

```python
class Settings(BaseSettings):
    # 新增配置项
    NEW_FEATURE_ENABLED: bool = True

    # 配置验证
    @field_validator('NEW_FEATURE_ENABLED')
    @classmethod
    def validate_feature_flag(cls, v: bool) -> bool:
        return v
```

## 测试规范

### 测试结构

```
tests/
├── __init__.py
├── conftest.py           # pytest 配置
├── test_api/            # API 测试
├── test_services/       # 服务测试
└── test_utils/          # 工具测试
```

### 编写测试

```python
# tests/test_services/test_supplier.py
import pytest
from services.supplier import SupplierService

def test_create_supplier(db_session):
    """测试创建供应商"""
    data = SupplierCreate(
        title="测试供应商",
        url="https://example.com",
        domain="example.com"
    )

    supplier = SupplierService.create(db_session, data)

    assert supplier is not None
    assert supplier.title == "测试供应商"
    assert supplier.id > 0

def test_create_duplicate_supplier(db_session):
    """测试创建重复供应商"""
    # ... 测试逻辑
```

### 测试原则

1. **独立测试**：每个测试独立运行
2. **清晰命名**：测试名称描述测试内容
3. **适当断言**：验证关键行为
4. **测试覆盖**：覆盖主要业务逻辑

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定文件
pytest tests/test_services/test_supplier.py

# 查看覆盖率
pytest --cov=backend --cov-report=html
```

## 安全规范

### 认证和授权

```python
# ✅ 使用依赖注入进行认证
@router.post("/suppliers", dependencies=[Depends(verify_api_key)])
async def create_supplier(data: SupplierCreate):
    pass

# ✅ 在服务层检查权限
def delete_supplier(user: User, supplier_id: int):
    if not user.is_admin:
        raise PermissionError("无权限删除")
```

### 数据验证

```python
# ✅ 使用 Pydantic 验证输入
class SupplierCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    url: HttpUrl
    emails: List[EmailStr] = []

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('标题不能为空')
        return v.strip()
```

### SQL 注入防护

```python
# ✅ 使用 ORM 参数化查询
suppliers = db.query(Supplier).filter(
    Supplier.title.like(f"%{keyword}%")
).all()

# ❌ 避免
query = f"SELECT * FROM suppliers WHERE title LIKE '%{keyword}%'"
```

### 敏感信息处理

```python
# ✅ 不记录敏感信息
logger.info(f"用户登录: {user.username}")  # ✅
logger.info(f"用户登录: {user.username}, 密码: {password}")  # ❌

# ✅ 使用环境变量
api_key = os.getenv('API_KEY')  # ✅
api_key = "sk-xxxxx"  # ❌
```

## Git 工作流

### 分支命名

```
main/master     # 主分支，生产环境
develop         # 开发分支
feature/xxx     # 功能分支
bugfix/xxx      # 修复分支
hotfix/xxx      # 紧急修复分支
```

### 提交信息

使用约定式提交格式：

```
<type>(<scope>): <subject>

<body>

<footer>
```

**类型 (type)**：
- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具

**示例**：

```bash
# 新功能
git commit -m "feat(supplier): 添加批量导入功能"

# 修复 bug
git commit -m "fix(search): 修复搜索结果去重问题"

# 文档更新
git commit -m "docs(readme): 更新部署说明"
```

### Pull Request

1. **标题清晰**：描述变更内容
2. **描述详细**：说明变更原因和影响
3. **关联 Issue**：使用 `#123` 引用 Issue
4. **小步提交**：保持 PR 范围适中

### 代码审查清单

- [ ] 代码符合规范
- [ ] 有适当的测试
- [ ] 文档已更新
- [ ] 无安全漏洞
- [ ] 日志记录完善
- [ ] 错误处理正确

## 开发工作流

### 开发新功能

1. 创建功能分支：`git checkout -b feature/xxx`
2. 编写代码和测试
3. 运行测试：`pytest`
4. 代码格式化：`black .`
5. 提交代码：`git commit -m "feat: xxx"`
6. 推送分支：`git push origin feature/xxx`
7. 创建 PR
8. 代码审查
9. 合并到主分支

### Bug 修复

1. 创建修复分支：`git checkout -b bugfix/xxx`
2. 编写复现测试
3. 修复代码
4. 验证修复
5. 提交 PR

## 工具和依赖

### 必需工具

```bash
# 安装开发依赖
pip install -r requirements.txt

# 代码格式化
pip install black

# 类型检查
pip install mypy

# 代码检查
pip install flake8

# 测试
pip install pytest pytest-cov
```

### 配置文件

项目包含以下配置文件：
- `.env.example`：环境变量示例
- `pyproject.toml`：项目配置
- `.gitignore`：Git 忽略规则

## 性能优化

### 数据库查询

```python
# ✅ 使用索引
db.query(Supplier).filter(Supplier.domain == domain).first()

# ✅ 批量操作
db.bulk_insert_mappings(Supplier, supplier_list)

# ❌ 避免 N+1 查询
suppliers = db.query(Supplier).all()
for supplier in suppliers:  # N+1 问题
    emails = supplier.emails
```

### 缓存策略

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_supplier_type(title: str) -> str:
    """缓存供应商类型判断结果"""
    # ... 复杂计算
    return result
```

## 监控和调试

### 健康检查

系统提供健康检查端点：

```bash
GET /health
```

### 日志查看

```bash
# 查看应用日志
docker compose logs -f backend

# 查看特定级别日志
docker compose logs backend | grep ERROR
```

### 性能分析

```python
import time
import logging

logger = logging.getLogger(__name__)

def slow_operation():
    start = time.time()
    # ... 操作
    duration = time.time() - start
    logger.info(f"操作耗时: {duration:.2f}s")
```

## 资源链接

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Pydantic 文档](https://docs.pydantic.dev/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
- [PEP 8 风格指南](https://pep8.org/)
- [Python 最佳实践](https://docs.python-guide.org/)

## 变更日志

本文档会随项目演进持续更新。重大变更将在 `CHANGELOG.md` 中记录。

---

**最后更新**: 2026-03-04
**维护者**: 开发团队

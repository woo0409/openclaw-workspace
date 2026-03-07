# 俄罗斯纽扣供应商数据库 - 后端项目

## 📖 项目简介

这是俄罗斯纽扣供应商数据库的后端项目，提供RESTful API来管理俄罗斯地区的纽扣及服装配件供应商信息。

## 🚀 技术栈

- **框架**: FastAPI
- **数据库**: MySQL
- **ORM**: SQLAlchemy
- **搜索引擎**: Tavily AI
- **验证**: Pydantic
- **日志**: Python logging

## 📦 安装依赖

```bash
pip install -r requirements.txt
```

## 🏃 运行项目

### 开发模式
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 生产模式
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 🌐 环境配置

复制 `.env.example` 为 `.env` 并配置：

```env
# 数据库配置
DATABASE_URL=mysql+pymysql://user:password@host:port/database

# API密钥
TAVILY_API_KEY=your_tavily_api_key_here
API_KEY=your_api_key_here

# 应用配置
DEBUG=false
TZ=Asia/Shanghai
```

## 📁 项目结构

```
backend/
├── api/
│   ├── models/        # 数据库模型
│   ├── routes/        # API 路由
│   └── schemas/       # Pydantic 模式
├── core/
│   ├── config.py      # 配置管理
│   ├── database.py    # 数据库连接
│   ├── logger.py      # 日志配置
│   └── security.py   # 安全认证
├── services/
│   └── tavily.py     # Tavily 搜索服务
├── scripts/          # 工具脚本
└── main.py           # 应用入口
```

## 🔧 API 文档

启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📝 主要接口

### 供应商管理
- `GET /api/suppliers` - 获取供应商列表
- `GET /api/suppliers/{id}` - 获取单个供应商详情
- `POST /api/suppliers` - 添加供应商（需要API Key）
- `PUT /api/suppliers/{id}` - 更新供应商（需要API Key）
- `DELETE /api/suppliers/{id}` - 删除供应商（需要API Key）

### 搜索功能
- `GET /api/search` - 搜索新供应商
- `POST /api/export` - 导出供应商数据为Excel

### 统计信息
- `GET /api/stats` - 获取统计数据
- `GET /api/cities` - 获取城市列表
- `GET /api/types` - 获取供应商类型列表

## 🔐 安全认证

写操作接口（POST、PUT、DELETE）需要在请求头中提供API Key：

```
X-API-Key: your_api_key_here
```

## 📄 License

MIT

## 🔧 CI/CD

测试 GitHub Actions 权限配置

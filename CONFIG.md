# 后端配置管理系统

## 概述

本项目采用企业级分层配置管理方案，确保敏感信息安全并提供灵活的配置选项。

## 配置加载优先级

1. **环境变量**（最高优先级）
2. **.env 文件**
3. **代码默认值**（仅限非敏感配置）

## 快速开始

### 1. 创建配置文件

```bash
# 复制示例配置文件
cp backend/.env.example backend/.env

# 或使用配置工具
python backend/scripts/setup_env.py
```

### 2. 填写必需配置

编辑 `backend/.env` 文件，填写以下必需配置项：

```bash
# 数据库连接
DATABASE_URL=mysql+pymysql://user:password@host:port/database

# Tavily API 密钥
TAVILY_API_KEY=your_tavily_api_key

# API 认证密钥
API_KEY=your_secure_api_key
```

### 3. 生成安全密钥

使用配置工具生成安全的 API 密钥和密码：

```bash
python backend/scripts/setup_env.py
```

## 配置项说明

### 必需配置

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `DATABASE_URL` | 数据库连接字符串 | `mysql+pymysql://user:pass@localhost:3306/db` |
| `TAVILY_API_KEY` | Tavily 搜索 API 密钥 | 从 https://tavily.com 获取 |
| `API_KEY` | API 认证密钥 | 使用 `setup_env.py` 生成 |

### 可选配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `DEBUG` | `false` | 开发模式开关 |
| `LOG_LEVEL` | `INFO` | 日志级别 |
| `LOG_FILE` | `""` | 日志文件路径（为空则仅控制台输出） |
| `ALLOWED_ORIGINS` | `http://localhost:5173` | CORS 允许的源 |

### 业务配置

以下配置有合理的默认值，通常不需要修改：

- `MAX_RESULTS_PER_QUERY`: 每次查询最大结果数（默认：5）
- `MAX_NEW_SUPPLIERS`: 单次搜索最大新增供应商数（默认：6）
- `DEFAULT_PAGE_SIZE`: 默认分页大小（默认：50）
- `MAX_PAGE_SIZE`: 最大分页大小（默认：200）

## 配置验证

系统会在启动时自动验证以下内容：

1. ✅ 必需配置项已填写
2. ✅ 日志级别有效
3. ✅ CORS 配置合理

如果验证失败，系统会显示详细的错误信息。

## 安全最佳实践

### 开发环境

1. ✅ 使用 `.env` 文件存储配置
2. ✅ 不要将 `.env` 提交到 Git（已在 `.gitignore` 中）
3. ✅ 使用强密码和随机 API 密钥

### 生产环境

1. ✅ 使用环境变量或密钥管理服务
2. ✅ 设置 `DEBUG=false`
3. ✅ 设置 `LOG_LEVEL=INFO` 或 `WARNING`
4. ✅ 配置 `ALLOWED_ORIGINS` 为实际域名
5. ✅ 定期轮换密钥
6. ✅ 使用数据库连接池优化性能

## 配置工具使用

### 生成 API 密钥

```bash
python backend/scripts/setup_env.py
# 选择选项 1
```

### 生成强密码

```bash
python backend/scripts/setup_env.py
# 选择选项 2
```

### 验证当前配置

```bash
python backend/scripts/setup_env.py
# 选择选项 4
```

## 常见问题

### 1. 如何重置 API 密钥？

编辑 `.env` 文件，修改 `API_KEY` 配置项，或使用配置工具生成新密钥。

### 2. 如何切换到生产环境？

设置以下环境变量：
```bash
DEBUG=false
LOG_LEVEL=INFO
ALLOWED_ORIGINS=https://yourdomain.com
```

### 3. 如何启用日志文件？

在 `.env` 文件中设置：
```bash
LOG_FILE=logs/backend.log
```

### 4. 如何配置 Docker 环境？

在 `docker-compose.yml` 中使用环境变量：
```yaml
services:
  backend:
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - TAVILY_API_KEY=${TAVILY_API_KEY}
      - API_KEY=${API_KEY}
```

## 配置示例

### 开发环境 (.env)

```bash
DEBUG=true
LOG_LEVEL=DEBUG
DATABASE_URL=mysql+pymysql://dev:dev123@localhost:3306/russia_buttons_dev
TAVILY_API_KEY=tvly-dev-xxxxx
API_KEY=dev-key-xxxxx
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

### 生产环境 (环境变量)

```bash
export DEBUG=false
export LOG_LEVEL=INFO
export DATABASE_URL=mysql+pymysql://prod:secure_pass@prod-db:3306/russia_buttons
export TAVILY_API_KEY=tvly-prod-xxxxx
export API_KEY=prod-key-xxxxx
export ALLOWED_ORIGINS=https://yourdomain.com
```

## 故障排查

### 配置加载失败

如果看到配置错误信息：

1. 检查 `.env` 文件是否存在
2. 确认必需配置项已填写
3. 检查配置格式是否正确
4. 查看详细错误信息

### 日志级别不生效

1. 确认 `LOG_LEVEL` 值为大写（如 `INFO`）
2. 重启应用使配置生效

### CORS 错误

1. 检查 `ALLOWED_ORIGINS` 配置
2. 确认前端地址在允许列表中
3. 注意：生产环境不要使用 `*`

## 技术实现

- 使用 `pydantic-settings` 进行配置管理
- 支持环境变量和 .env 文件
- 配置验证和类型检查
- 分层配置加载机制

更多信息请参考：
- [pydantic-settings 文档](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [Python 最佳实践 - 配置管理](https://docs.python.org/3/library/configparser.html)

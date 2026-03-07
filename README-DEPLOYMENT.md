# 后端部署文档

## 📋 部署前准备

### 1. GitHub Secrets 配置

在仓库 `woo0409/russia-buttons-backend` 的 Settings → Secrets and variables → Actions 中配置以下 Secrets：

| Secret名称 | 值 | 说明 |
|-----------|-----|------|
| `GH_TOKEN` | GitHub Personal Access Token | 用于GHCR登录 |
| `SSH_PRIVATE_KEY` | 服务器SSH私钥内容 | 连接到生产服务器 |
| `SSH_HOST` | 124.220.216.98 | 服务器IP地址 |
| `SSH_USER` | ubuntu | SSH用户名 |

### 2. 服务器准备

#### 安装Docker和Docker Compose

```bash
# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 启动Docker服务
sudo systemctl start docker
sudo systemctl enable docker

# 将当前用户添加到docker组
sudo usermod -aG docker $USER

# 安装Docker Compose
sudo apt-get update
sudo apt-get install -y docker-compose-plugin

# 或使用新版本
sudo apt-get install -y docker-compose
```

#### 创建项目目录

```bash
mkdir -p ~/russia-buttons/{logs,backups}
cd ~/russia-buttons
```

#### 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，填入实际值
nano .env
```

需要配置：
- `TAVILY_API_KEY`: Tavily API密钥
- `API_KEY`: API认证密钥

### 3. MySQL服务配置

确保MySQL容器已经运行，并创建数据库和用户：

```bash
# 连接到MySQL容器
docker exec -it russia-buttons-mysql mysql -uroot -prussia123

# 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS russia_buttons;

# 创建用户（如果不存在）
CREATE USER IF NOT EXISTS 'russia_user'@'%' IDENTIFIED BY 'russia_pass';

# 授予权限
GRANT ALL PRIVILEGES ON russia_buttons.* TO 'russia_user'@'%';
FLUSH PRIVILEGES;

# 退出MySQL
EXIT;
```

### 4. 网络配置

确保Docker网络存在：

```bash
# 创建网络（如果不存在）
docker network create russia-network 2>/dev/null || true

# 将MySQL容器连接到网络
docker network connect russia-network russia-buttons-mysql
```

## 🚀 部署流程

### 自动部署（推荐）

推送代码到 `master` 分支，GitHub Actions会自动执行：

1. ✅ 代码检查和测试
2. ✅ 构建Docker镜像
3. ✅ 推送到GHCR
4. ✅ 备份数据库（保留5天）
5. ✅ 部署到服务器
6. ✅ 健康检查

### 手动部署

如果需要手动部署：

```bash
# SSH到服务器
ssh ubuntu@124.220.216.98

# 进入项目目录
cd ~/russia-buttons

# 拉取最新镜像
docker compose pull backend

# 重启服务
docker compose up -d backend

# 查看日志
docker compose logs -f backend
```

## 🔧 维护操作

### 查看日志

```bash
# 应用日志
docker logs -f russia-buttons-backend

# Docker Compose日志
docker compose logs -f backend
```

### 重启服务

```bash
cd ~/russia-buttons
docker compose restart backend
```

### 手动备份数据库

```bash
# 执行备份脚本
bash ~/russia-buttons/.github/workflows/backup.sh

# 查看备份文件
ls -lh ~/russia-buttons/backups/
```

### 恢复数据库

```bash
# 恢复指定的备份文件
docker exec -i russia-buttons-mysql mysql -uroot -prussia123 russia_buttons < ~/russia-buttons/backups/russia_buttons_20260307_200000.sql
```

### 查看容器状态

```bash
# 查看所有容器
docker ps -a

# 查看backend容器详情
docker inspect russia-buttons-backend

# 查看资源使用情况
docker stats russia-buttons-backend
```

## 🐛 故障排查

### 服务无法启动

```bash
# 查看容器日志
docker logs russia-buttons-backend

# 检查容器状态
docker ps -a | grep russia-buttons-backend

# 检查网络连接
docker network inspect russia-network
```

### 数据库连接失败

```bash
# 检查MySQL容器是否运行
docker ps | grep russia-buttons-mysql

# 测试数据库连接
docker exec russia-buttons-mysql mysql -urussia_user -prussia_pass -e "SELECT 1"

# 检查网络连接
docker exec russia-buttons-backend ping -c 3 mysql
```

### 健康检查失败

```bash
# 手动测试健康检查端点
curl http://localhost:8000/health

# 检查容器健康状态
docker inspect russia-buttons-backend | grep -A 10 Health
```

### 清理旧镜像

```bash
# 清理未使用的镜像
docker image prune -af

# 清理所有未使用的资源
docker system prune -af --volumes
```

## 📊 监控

### 监控资源使用

```bash
# 实时监控
docker stats

# 查看容器详情
docker inspect russia-buttons-backend
```

### 日志监控

```bash
# 持续查看日志
docker logs -f --tail 100 russia-buttons-backend

# 导出日志
docker logs russia-buttons-backend > backend.log
```

## 🔐 安全建议

1. **定期更新依赖**: 定期运行 `pip install --upgrade -r requirements.txt`
2. **备份策略**: 确保数据库备份正常运行，定期检查备份文件
3. **访问控制**: 不要将 .env 文件提交到Git仓库
4. **日志监控**: 定期检查应用日志，及时发现异常

## 📝 更新记录

- 2026-03-07: 初始版本
  - 配置CI/CD流程
  - 配置自动备份
  - 配置健康检查

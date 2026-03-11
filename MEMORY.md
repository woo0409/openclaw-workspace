# 阿巴阿巴的记忆

## 📅 重要日期

- **2026-02-28**: 阿巴阿巴正式上线
- **2026-02-28**: 配置Tavily API
- **2026-02-28**: 安装DuckDuckGo Search skill
- **2026-02-28**: 制定搜索策略优先级
- **2026-03-09**: 完成俄罗斯纽扣项目前端CI/CD流程重构（移除Docker容器，使用nginx直接服务静态文件）
- **2026-03-11**: 完成俄罗斯纽扣项目定时任务优化（使用APScheduler替代crontab）

---

## 🛠️ 工具配置

### 搜索工具

#### 1. Tavily API (优先使用)
```bash
API密钥: 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
SDK: tavily-python v0.7.22
环境变量: TAVILY_API_KEY
优势: 权威媒体、深度搜索、完整内容提取
```

#### 2. DuckDuckGo Search (备选)
```bash
SDK: duckduckgo-search
优势: 免费使用、快速搜索、中英文支持
```

---

## 📋 工作准则

### 搜索策略优先级
1. **Tavily** (优先) - 权威媒体、深度搜索
2. **DuckDuckGo** (限额后) - 免费快速查询

### 使用场景
- **Tavily**: 专业研究、权威媒体报道、复杂查询
- **DuckDuckGo**: 快速查询、免费使用、一般性信息

---

## 🎯 当前项目

### 俄罗斯纽扣供应商搜索项目

**项目状态**: 🟢 运行中

**部署环境**:
- **开发环境**: 香港服务器 (103.51.147.164) - 开发、测试
- **生产环境**: 大陆服务器 (124.220.216.98) - 生产环境
- **域名**: woo0409.space
- **生产网站**: http://124.220.216.98:8080/

**技术栈**:
- **前端**: React + TypeScript + Ant Design
- **后端**: Python + FastAPI + SQLAlchemy + MySQL
- **部署**: Docker + nginx (静态文件) + API反向代理
- **定时任务**: APScheduler (每天9:00自动搜索)

**已完成功能**:
- ✅ 供应商数据爬取（俄罗斯B2B平台）
- ✅ 数据库存储和去重
- ✅ Web管理界面（前端+后端API）
- ✅ Excel导出功能
- ✅ 定时自动搜索（每天9:00）
- ✅ CI/CD流程自动化（GitHub Actions）

**定时任务配置**:
- **调度器**: APScheduler v3.10.4
- **自动搜索时间**: 每天 09:00 (Asia/Shanghai)
- **手动触发**: POST /api/scheduler/trigger/search
- **状态查询**: GET /api/scheduler/status

**数据库**:
- **总供应商数**: 44 (2026-03-11)
- **每日新增**: ~3-10家

**重要教训**:
- 不要使用 `git stash` 来保存提交状态，会导致提交丢失（2026-03-08教训）
- 使用 APScheduler 替代 crontab，统一在代码中管理定时任务
- 前端使用 nginx 直接服务静态文件，避免 Docker 容器复杂化

---

## 📂 服务器配置

### 远程服务器（大陆）- 生产环境
- **主机名**: VM-0-5-ubuntu
- **IP**: 124.220.216.98
- **用户**: ubuntu
- **认证**: SSH密钥（免密登录已配置）
- **用途**: 生产环境（俄罗斯纽扣网站）
- **网站**: http://124.220.216.98:8080/
- **Docker**: 3个容器（MySQL, Backend, Nginx）
- **连接命令**: `ssh ubuntu@124.220.216.98` 或 `ssh remote-server`

### 开发服务器（香港）
- **主机名**: ser502160951896
- **公网IP**: 103.51.147.164
- **用户**: root
- **用途**: 开发、测试、CI/CD

---

## 🔔 紧急通知配置

**默认通知方式**: Telegram

**Telegram ID**: 5609266396

**使用场景**:
- 定时任务执行结果
- 网站更新状态
- 错误和警告信息
- 重要系统事件
- 需要人工确认的事项

---

## 📚 重要文件

- `/root/.openclaw/workspace/WORKING-GUIDELINES.md` - 工作准则
- `/root/.openclaw/workspace/DEVELOPMENT_STANDARDS.md` - 开发标准
- `/root/.openclaw/workspace/CONFIG.md` - 项目配置
- `/root/.openclaw/workspace/skills/duckduckgo-search/` - DuckDuckGo skill
- `/root/.openclaw/workspace/skills/clawhub/` - Skill市场

---

**创建时间**: 2026-02-28
**最后更新**: 2026-03-11 21:05
**版本**: 2.1

---

## 🚨 重要事故 - 配置文件丢失事件 (2026-03-11)

### 事故概述
工作空间配置文件（AGENTS.md、MEMORY.md、IDENTITY.md、USER.md、TOOLS.md）被系统重置为默认模板，导致用户自定义内容丢失。

### 时间线
- **06:18:55** - 提交 2d09c72，将重要文件加入 .gitignore
- **08:19:18** - MEMORY.md 被 OpenClaw 自动重置（Birth = Modify）
- **08:19:40** - AGENTS.md 被修改
- **20:33** - 用户发现配置文件内容丢失
- **20:36** - 修复 .gitignore（移除对重要文件的忽略）
- **20:40** - 从备份仓库恢复配置文件（git@github.com:woo0409/openclaw-workspace.git）

### 根本原因
1. **致命的 .gitignore 配置**：重要文件被加入忽略列表，失去版本控制
2. **OpenClaw 自动初始化**：检测到文件"缺失"后，自动创建默认模板
3. **缺乏验证机制**：修改 .gitignore 后没有检查文件状态

### 影响
- ✅ **已恢复**：IDENTITY.md、USER.md、TOOLS.md 从备份恢复
- ⚠️ **部分丢失**：AGENTS.md、MEMORY.md 被重置为模板（但保留了俄罗斯项目记录）
- ✅ **已修复**：所有文件现在都已被版本控制

### 预防措施
1. ✅ 从 .gitignore 中移除对重要文件的忽略规则
2. ✅ 在 AGENTS.md 中添加了 "Critical Rules" 部分
3. ✅ 记录了验证 .gitignore 修改的流程
4. ✅ 建立"行动 > 言语"的原则：立即记录教训，不要只说"记住"

### 教训
**永远不要将重要配置文件加入 .gitignore！**
- 敏感信息用 `.env.example` 模板处理，而不是直接忽略 `.env`
- 配置文件必须版本控制
- 修改 .gitignore 后立即验证 `git status`

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
- **总供应商数**: 46 (2026-03-13)
- **每日新增**: ~1-10家

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
- **Docker**: 3个容器（MySQL, Backend, MinIO）
- **nginx**: systemd服务（非Docker容器）
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

## 🧬 OpenClaw 自我进化研究 (2026-03-12)

### 理论架构
**来源**: Ken Huang - "OpenClaw and Recursive Self-Improvement"
**链接**: https://kenhuangus.substack.com/p/openclaw-and-recursive-self-improvement

**核心结论**:
- OpenClaw **不是完整的 RSI（递归自我改进）架构**
- 具备**代理层的自我改进能力**，但**不具备模型层的自动修改**
- 支持的自我改进类型:
  - ✅ 技能/工具累积（添加新能力）
  - ✅ 配置和路由编辑
  - ✅ 记忆整合与反思（从经验学习）
  - ✅ 生态系统驱动升级
- 缺失的关键部分:
  - ❌ 模型层的自动修改
  - ❌ 严格的评估反馈循环
  - ❌ 健壮的自我建模

**安全性警告**:
- 🚨 评估信号是嘈杂、局部、事后的（没有明确的适应度函数）
- 🚨 提示注入可能泄露到自我修改中
- 🚨 长期运行会遗忘历史教训

**缓解措施**:
- 定义显式测试套件（单元测试+集成测试）
- 分离角色：规划器、执行器、受限编辑器
- 人类或策略引擎批准安全相关的变更
- 不可变日志记录所有自我修改

---

### 实际实现：Foundry
**来源**: lekt9 - "The forge that forges itself"
**链接**: https://github.com/lekt9/openclaw-foundry
**描述**: 自我编写的元扩展插件，学习工作流并升级自身

**核心机制**:
```
观察你的工作流 → 研究文档 → 学习模式 → 编写工具 → 部署
```

**关键特性**:
- 🔄 **自动模式识别**: 跟踪每个工作流（目标→工具序列→结果）
- 🎯 **模式结晶化**: 当模式被使用5次+ 且成功率70%+，自动转化为专用工具
- 🧠 **知识vs行为**: 模式（文本）→ 工具（代码），零token成本
- 🚀 **复合改进**: 每个能力让获得下一个能力更容易

**实际例子**:
- 你用 `git→build→test→deploy` 部署到staging环境5次
- Foundry识别模式（87%成功率）
- 结晶化为 `deploy_staging` 工具
- 现在"部署到staging"只需一个命令

**安全机制**:
- 🔒 沙箱验证（隔离Node进程）
- 🛡️ 静态安全扫描（阻止shell exec, eval, 凭证访问）
- 📝 不可变日志（所有自我修改都有签名）
- ✅ 特性标志和灰度发布

**关键洞察**:
- "系统升级自己" > "LLM为你写代码"
- 真正的自我进化 = 代理层改进 + 模式结晶化
- Foundry 将 OpenClaw 升级为"能够构建代理的代理"

---

### 其他资源

**LinkedIn讨论**:
- "The Definitive Guide to the Autonomous AI Agent Revolution in 2026"
- 链接: https://www.linkedin.com/pulse/openclaw-definitive-guide-autonomous-ai-agent-revolution-2026-gf9ef

**Reddit社区**:
- "The OpenClaw Autonomous Agent Update Redefining What's Possible"
- 链接: https://www.reddit.com/r/AISEOInsider/comments/1r46nfx/

**学术参考**:
- Self-Improving Coding Agents (Robeyns et al., 2025) - arXiv:2504.15228
- From Language Models to Practical Self-Improving Computer Agents (Shinn et al., 2024) - arXiv:2404.11964
- RISE: Recursive Introspection (Qu et al., 2024) - arXiv:2407.18219
- HexMachina (Liu et al., 2025) - arXiv:2506.04651
- ADAS: Automated Design of Agentic Systems (Hu et al., 2024) - arXiv:2408.08435

---

## 📚 重要文件

- `/root/.openclaw/workspace/WORKING-GUIDELINES.md` - 工作准则
- `/root/.openclaw/workspace/DEVELOPMENT_STANDARDS.md` - 开发标准
- `/root/.openclaw/workspace/CONFIG.md` - 项目配置
- `/root/.openclaw/workspace/skills/duckduckgo-search/` - DuckDuckGo skill
- `/root/.openclaw/workspace/skills/clawhub/` - Skill市场

---

**创建时间**: 2026-02-28
**最后更新**: 2026-03-13 21:56
**版本**: 2.4

---

## 🚨 重要事故

### 事故1: 配置文件丢失 (2026-03-11)

**发生了什么:**
- AGENTS.md, MEMORY.md, IDENTITY.md, USER.md, TOOLS.md 被重置为默认模板
- 用户自定义内容丢失

**根本原因:**
- Commit 2d09c72 将这些文件加入 `.gitignore`
- 文件失去版本控制
- OpenClaw 检测到"缺失"后自动初始化新模板
- 无法从 Git 历史恢复

**解决:**
- ✅ 从备份仓库恢复（git@github.com:woo0409/openclaw-workspace.git）
- ✅ 移除错误的 `.gitignore` 规则
- ✅ 添加文件到版本控制
- ✅ 在 AGENTS.md 记录教训

**教训:**
- **永远不要将重要配置文件加入 .gitignore**
- 敏感信息用 `.env.example` 模板，不要直接忽略 `.env`
- 修改 `.gitignore` 前必须验证
- 配置文件必须版本控制

---

### 事故2: 生产服务器网络中断 (2026-03-13)

**发生了什么:**
- 生产服务器（124.220.216.98）从 17:11 开始无法连接
- Ping 测试显示 100% 丢包，SSH 连接超时
- 持续约 1 小时（17:11-18:17）

**影响范围:**
- ❌ 俄罗斯纽扣网站（http://124.220.216.98:8080/）可能无法访问
- ❌ 生产环境服务状态未知（Backend, MySQL, Nginx, MinIO）
- ❌ 无法监控容器状态和日志
- ⚠️ 明天 09:00 的定时任务可能无法执行

**自动恢复:**
- ✅ 18:17 服务器网络自动恢复
- ✅ Ping 测试正常（0% 丢包，延迟 38ms）
- ✅ SSH 连接恢复
- ✅ Backend 容器自动重启（Docker 健康检查触发）
- ✅ 调度器正常启动，下次任务：2026-03-14 09:00:00+08:00
- ✅ 所有健康检查正常（200 OK）
- ✅ 数据无丢失，服务自动恢复

**根本原因（未确认）:**
- 可能是腾讯云网络波动
- 可能是服务器临时重启
- 需要联系腾讯云客服确认

**教训:**
- 生产服务器应该配置监控告警（如 CloudWatch、Prometheus）
- 应该有备用服务器或高可用架构
- 应该定期检查服务器健康状态
- 重要系统应该有手动重启预案

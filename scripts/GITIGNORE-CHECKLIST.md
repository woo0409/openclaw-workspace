# .gitignore 修改检查清单

## ⚠️ 危险操作警告

修改 .gitignore 可能导致文件丢失！在提交任何 .gitignore 更改前，必须完成以下检查。

---

## ✅ 强制检查（每次修改 .gitignore 前）

### 1. 查看当前被追踪的文件
```bash
git status
```
确认重要文件的状态（是否为 tracked）。

### 2. 查看被追踪的关键文件
```bash
git ls-files | grep -E "AGENTS|MEMORY|IDENTITY|USER|SOUL|TOOLS|HEARTBEAT"
```
确认这些文件都在列表中。

### 3. 运行验证脚本
```bash
/root/.openclaw/workspace/scripts/verify-critical-files.sh
```
确保返回 "✅ 所有关键文件都已被 Git 追踪"。

### 4. 检查新添加的 .gitignore 规则
仔细阅读新规则，确认：
- ❌ 没有添加: AGENTS.md, MEMORY.md, IDENTITY.md, USER.md, SOUL.md, TOOLS.md, HEARTBEAT.md
- ❌ 没有添加: memory/ 目录
- ❌ 没有添加其他重要的配置文件

---

## 🚫 禁止添加到 .gitignore 的文件/目录

### 绝对禁止
```
AGENTS.md          # 工作空间管理指南
MEMORY.md          # 长期记忆
IDENTITY.md        # 身份信息
USER.md           # 用户信息
SOUL.md           # 灵魂文件
TOOLS.md          # 工具配置
HEARTBEAT.md      # 任务清单
memory/           # 每日记录目录
```

### 处理敏感信息的正确方式

**错误做法：**
```gitignore
.env        # ❌ 完全忽略
config/      # ❌ 整个目录忽略
```

**正确做法：**
```gitignore
.env        # ❌ 忽略实际文件
.env.example # ✅ 保留模板文件（可追踪）
```

**创建示例模板：**
```bash
# 创建模板
cp .env .env.example
# 编辑 .env.example，将敏感信息替换为占位符
echo "API_KEY=your_api_key_here" > .env.example
```

---

## 🔄 修改 .gitignore 的正确流程

### Step 1: 编辑 .gitignore
```bash
vim .gitignore
# 或使用其他编辑器
```

### Step 2: 验证重要文件仍被追踪
```bash
/root/.openclaw/workspace/scripts/verify-critical-files.sh
```

### Step 3: 检查 Git 状态
```bash
git status
```
确认重要文件不是 "untracked"。

### Step 4: 提交更改
```bash
git add .gitignore
git commit -m "chore: 更新 .gitignore - 添加 X 规则"
```

### Step 5: 验证提交
```bash
git show HEAD:.gitignore
```
确认提交的内容符合预期。

---

## 🚨 如果发现文件未被追踪

立即停止！不要提交！

### 检查原因
```bash
cat .gitignore | grep <文件名>
```

### 解决方法

**方法 1: 从 .gitignore 中移除规则**
```bash
# 编辑 .gitignore，删除相关规则
vim .gitignore

# 验证文件是否被追踪
git ls-files <文件名>
```

**方法 2: 强制添加文件（如果应该被追踪）**
```bash
git add -f <文件名>
git commit -m "fix: 强制添加关键配置文件"
```

**方法 3: 恢复丢失的文件（如果文件已被删除）**
```bash
# 从备份恢复
git checkout HEAD -- <文件名>

# 或从远程备份恢复
git show backup/master:<文件名> > <文件名>
```

---

## 📋 事故回顾 (2026-03-11)

### 发生了什么
- 在 06:18:55 提交了错误的 .gitignore（将重要文件加入忽略）
- 在 08:19:18 文件被 OpenClaw 自动重置
- 用户自定义内容丢失

### 错误操作
```gitignore
# ❌ 错误配置
memory/
AGENTS.md
MEMORY.md
IDENTITY.md
USER.md
SOUL.md
TOOLS.md
HEARTBEAT.md
```

### 正确配置
```gitignore
# ✅ 正确配置 - 不要忽略这些文件！
# 这些文件必须被版本控制
```

### 预防措施
1. 修改 .gitignore 前运行验证脚本
2. 检查 `git ls-files` 输出
3. 提交前确认 `git status`
4. 记录任何重大更改到 AGENTS.md 和 MEMORY.md

---

**记住：做比说重要！每次修改 .gitignore 前，完成以上检查！**

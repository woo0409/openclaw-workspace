# HEARTBEAT.md

## 🔴 高优先级任务（每次心跳必查，并自主完成任务，完成后打勾，仅保留三项）
- [ ] 优化俄罗斯项目定时任务逻辑 - 实现 APScheduler 方案
  - [x] 安装 APScheduler 依赖
  - [x] 创建 services/scheduler.py（统一定时任务管理）
  - [x] 集成到 main.py 启动流程
  - [x] 移除外部 crontab 依赖（代码中已集成）
  - [x] 提交代码到 Git（workspace 和 backend 项目）
  - [x] 推送到远程仓库
  - [x] 验证定时任务正常执行（手动触发成功，找到 1 家新公司）
  - [⏳] 部署修复后的代码（修复 last_run_time 和统计总数错误）
  - [ ] 移除旧 shell 脚本和 crontab

**进度更新**（2026-03-11 01:20）：
- ✅ 调度器已启动，配置定时任务：供应商搜索（每天 9:00）
- ✅ 手动触发成功，执行搜索并保存数据
- ⚠️ CI/CD 部署失败（GHCR 网络连接超时）
- 📊 测试结果：找到 1 家新公司，成功保存到数据库

**已修复的问题**：
1. 移除 scheduler.py 中未使用的 db 变量
2. 移除 scheduler.py 中未使用的 SearchRequest 导入
3. 修复 /api/scheduler/status 端点 500 错误（移除不兼容的 last_run_time 属性）
4. 修复定时任务统计总数错误（Supplier.__class__ → Supplier）

## 🟡 中优先级任务
- [x] 完成 Excel 文件导出功能 - ✅ 完成（2026-03-09 04:07）
  - ✅ openpyxl 已安装（v3.1.2）
  - ✅ pymysql 已安装
  - ✅ 创建 ExportService 服务类（services/export.py）
  - ✅ 添加 /api/export/suppliers 端点
  - ✅ 支持日期、关键词、公司类型、城市、标签筛选
  - ✅ 生成带样式的Excel文件（表头、边框、冻结首行、筛选器）
  - ✅ 在服务器容器中安装 openpyxl

## 🟢 低优先级任务
*（无待处理的低优先级任务）*

## 注意
1. 在任务执行过程中，在对工作空间结构进行修改时，要反思：是否值得这样修改，这样修改后对未来的收益有多少，该如何保持工作空间结构的整洁。
2. 在没有任务的情况下，回顾工作空间openclaw相关的配置如AGENT.md,MEMORY.md等，查看是否有过期内容进行修改，并回顾memory文件夹下近三天的内容，是否有有价值内容可以进行自我迭代

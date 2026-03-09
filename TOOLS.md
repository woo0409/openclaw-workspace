# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## 📧 紧急通知方式

**默认通知方式**: Telegram

**Telegram ID**: 5609266396

**使用场景**: 以后有任何紧急需要我来确认的，就用 Telegram 方式通知你。

**通知类型**:
- 定时任务执行结果
- 网站更新状态
- 错误和警告信息
- 重要系统事件
- 需要人工确认的事项

---

## SSH 服务器

### 当前服务器（香港）- 开发环境
- **主机名**: ser502160951896
- **公网IP**: 103.51.147.164
- **用户**: root
- **用途**: 开发、测试、CI/CD
- **网站**: http://103.51.147.164:8080/（已停止，专注开发）

### 远程服务器（大陆）- 生产环境
- **主机名**: VM-0-5-ubuntu
- **IP**: 124.220.216.98
- **用户**: ubuntu
- **认证**: SSH密钥（免密登录已配置）
- **用途**: 生产环境（俄罗斯纽扣网站）
- **网站**: http://124.220.216.98:8080/
- **Docker**: 4个容器（MySQL, Backend, Frontend, Nginx）
- **连接命令**: `ssh ubuntu@124.220.216.98` 或 `ssh remote-server`

### SSH 配置建议（可选）
可以在 `~/.ssh/config` 中添加配置：
```
Host remote-server
    HostName 124.220.216.98
    User ubuntu
    IdentityFile ~/.ssh/id_rsa
```
这样可以用 `ssh remote-server` 快速连接。

---

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

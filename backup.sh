#!/bin/bash
#
# 数据库备份脚本
# 功能：备份MySQL数据库并清理旧备份
#

set -e

# ==================== 配置 ====================
BACKUP_DIR="${HOME}/russia-buttons/backups"
BACKUP_FILE="russia_buttons_$(date +%Y%m%d_%H%M%S).sql"
KEEP_DAYS=5
MYSQL_CONTAINER="russia-buttons-mysql"
MYSQL_USER="root"
MYSQL_PASSWORD="russia123"
DATABASE="russia_buttons"

# ==================== 创建备份目录 ====================
echo "📁 Creating backup directory..."
mkdir -p "${BACKUP_DIR}"

# ==================== 执行备份 ====================
echo "💾 Backing up database: ${DATABASE}"
docker exec "${MYSQL_CONTAINER}" mysqldump \
  -u"${MYSQL_USER}" \
  -p"${MYSQL_PASSWORD}" \
  "${DATABASE}" > "${BACKUP_DIR}/${BACKUP_FILE}"

# 检查备份是否成功
if [ $? -eq 0 ] && [ -f "${BACKUP_DIR}/${BACKUP_FILE}" ]; then
  BACKUP_SIZE=$(du -h "${BACKUP_DIR}/${BACKUP_FILE}" | cut -f1)
  echo "✅ Backup created successfully: ${BACKUP_FILE} (${BACKUP_SIZE})"
else
  echo "❌ Backup failed!"
  exit 1
fi

# ==================== 清理旧备份 ====================
echo "🧹 Cleaning up backups older than ${KEEP_DAYS} days..."
DELETED_COUNT=$(find "${BACKUP_DIR}" -name "russia_buttons_*.sql" -type f -mtime +${KEEP_DAYS} -delete -print | wc -l)

if [ "${DELETED_COUNT}" -gt 0 ]; then
  echo "✅ Deleted ${DELETED_COUNT} old backup(s)"
else
  echo "ℹ️  No old backups to delete"
fi

# ==================== 列出当前备份 ====================
echo ""
echo "📋 Current backups:"
ls -lh "${BACKUP_DIR}" | grep "russia_buttons_.*\.sql" || echo "No backups found"

echo ""
echo "✅ Backup process completed!"

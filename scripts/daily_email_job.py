"""
每日邮件通知定时任务

可以通过以下方式运行：
1. 直接运行: python scripts/daily_email_job.py
2. 通过 cron 定时运行: 0 8 * * * python scripts/daily_email_job.py
"""
import sys
import os
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import SessionLocal
from services.email_service import email_service
from core.logger import get_logger

logger = get_logger(__name__)


def main():
    """
    执行每日邮件通知任务
    """
    logger.info("=" * 60)
    logger.info("开始执行每日邮件通知任务")
    logger.info("=" * 60)

    try:
        # 创建数据库会话
        db = SessionLocal()

        try:
            # 获取通知邮箱配置
            notification_email = os.getenv("NOTIFICATION_EMAIL")
            enabled = os.getenv("NOTIFICATION_ENABLED", "true").lower() == "true"

            logger.info(f"通知邮箱: {notification_email}")
            logger.info(f"通知启用状态: {enabled}")

            if not notification_email:
                logger.warning("未配置通知邮箱，跳过发送")
                return

            if not enabled:
                logger.info("邮件通知已禁用，跳过发送")
                return

            # 发送每日通知
            logger.info("开始发送每日通知...")
            success = email_service.send_daily_notification(db, notification_email)

            if success:
                logger.info("✅ 每日通知发送成功！")
            else:
                logger.error("❌ 每日通知发送失败！")

        finally:
            db.close()

    except Exception as e:
        logger.error(f"❌ 每日邮件通知任务执行失败: {e}")
        raise


if __name__ == "__main__":
    main()

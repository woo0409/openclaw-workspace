"""
邮件服务 - 处理邮件发送和定时通知
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session

from core.logger import get_logger
from api.models import Supplier

logger = get_logger(__name__)


class EmailService:
    """邮件服务"""

    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.qq.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL")
        self.from_name = os.getenv("FROM_NAME", "俄罗斯纽扣供应商数据库")

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        plain_text: str = None
    ) -> bool:
        """
        发送邮件

        Args:
            to_email: 收件人邮箱
            subject: 邮件主题
            html_content: HTML 内容
            plain_text: 纯文本内容（可选）

        Returns:
            bool: 是否发送成功
        """
        try:
            # 创建邮件对象
            msg = MIMEMultipart('alternative')
            msg['From'] = formataddr((self.from_name, self.from_email))
            msg['To'] = to_email
            msg['Subject'] = subject

            # 添加 HTML 内容
            msg.attach(MIMEText(html_content, 'html', 'utf-8'))

            # 添加纯文本内容（备用）
            if plain_text:
                msg.attach(MIMEText(plain_text, 'plain', 'utf-8'))

            # 发送邮件
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg, self.from_email, [to_email])

            logger.info(f"邮件发送成功: {to_email}")
            return True

        except Exception as e:
            logger.error(f"邮件发送失败: {e}")
            return False

    def send_test_email(self, to_email: str) -> bool:
        """
        发送测试邮件

        Args:
            to_email: 收件人邮箱

        Returns:
            bool: 是否发送成功
        """
        html_content = """
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    background-color: #f5f5f5;
                    padding: 20px;
                    margin: 0;
                }
                .container {
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: #ffffff;
                    border-radius: 12px;
                    padding: 40px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }
                .header {
                    text-align: center;
                    margin-bottom: 30px;
                }
                .logo {
                    font-size: 24px;
                    font-weight: bold;
                    color: #3b82f6;
                    margin-bottom: 10px;
                }
                .success-icon {
                    font-size: 48px;
                    color: #10b981;
                    margin-bottom: 20px;
                }
                .content {
                    text-align: center;
                    color: #333333;
                }
                .info-box {
                    background-color: #f0f9ff;
                    border-left: 4px solid #3b82f6;
                    padding: 15px 20px;
                    margin: 20px 0;
                    border-radius: 8px;
                    text-align: left;
                }
                .info-box p {
                    margin: 5px 0;
                    color: #1e40af;
                }
                .footer {
                    text-align: center;
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #e5e7eb;
                    color: #6b7280;
                    font-size: 14px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">🔘 俄罗斯纽扣供应商数据库</div>
                    <div class="success-icon">✅</div>
                </div>

                <div class="content">
                    <h1 style="font-size: 20px; margin-bottom: 15px;">测试邮件发送成功！</h1>
                    <p style="font-size: 16px; color: #666666; margin-bottom: 25px;">
                        您好！
                    </p>
                    <p style="font-size: 16px; color: #666666;">
                        这是一封测试邮件，用于验证您的邮箱配置是否正确。
                    </p>

                    <div class="info-box">
                        <p><strong>📧 邮箱地址:</strong> {to_email}</p>
                        <p><strong>⏰ 发送时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    </div>

                    <p style="font-size: 16px; color: #666666; margin-top: 25px;">
                        如果您收到此邮件，说明邮箱配置正确，每日定时通知功能已经可以正常使用。
                    </p>
                </div>

                <div class="footer">
                    <p>俄罗斯纽扣供应商数据库 · 实时更新</p>
                    <p style="margin-top: 10px;">此为系统自动发送的邮件，请勿直接回复</p>
                </div>
            </div>
        </body>
        </html>
        """

        return self.send_email(
            to_email=to_email,
            subject="✅ 测试邮件 - 俄罗斯纽扣供应商数据库",
            html_content=html_content,
            plain_text=f"这是一封测试邮件，发送时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

    def send_daily_notification(self, db: Session, to_email: str) -> bool:
        """
        发送每日通知邮件

        Args:
            db: 数据库会话
            to_email: 收件人邮箱

        Returns:
            bool: 是否发送成功
        """
        try:
            # 获取统计数据
            from api.models import Supplier
            total_count = db.query(Supplier).count()
            email_count = db.query(Supplier).filter(Supplier.emails != None).filter(Supplier.emails != []).count()
            phone_count = db.query(Supplier).filter(Supplier.phones != None).filter(Supplier.phones != []).count()

            # 获取今日新增
            today = datetime.now().strftime('%Y-%m-%d')
            today_new = db.query(Supplier).filter(Supplier.date_found == today).count()

            # 获取最近更新的供应商
            recent = db.query(Supplier).order_by(Supplier.created_at.desc()).limit(5).all()

            html_content = f"""
            <!DOCTYPE html>
            <html lang="zh-CN">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                        background-color: #f5f5f5;
                        padding: 20px;
                        margin: 0;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        background-color: #ffffff;
                        border-radius: 12px;
                        padding: 40px;
                        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    }}
                    .header {{
                        text-align: center;
                        margin-bottom: 30px;
                        padding-bottom: 20px;
                        border-bottom: 2px solid #3b82f6;
                    }}
                    .logo {{
                        font-size: 24px;
                        font-weight: bold;
                        color: #3b82f6;
                    }}
                    .date-badge {{
                        display: inline-block;
                        background-color: #3b82f6;
                        color: white;
                        padding: 6px 16px;
                        border-radius: 20px;
                        font-size: 14px;
                        margin-left: 10px;
                    }}
                    .stats-grid {{
                        display: grid;
                        grid-template-columns: repeat(2, 1fr);
                        gap: 15px;
                        margin: 25px 0;
                    }}
                    .stat-card {{
                        background-color: #f0f9ff;
                        border-radius: 8px;
                        padding: 20px;
                        text-align: center;
                    }}
                    .stat-number {{
                        font-size: 32px;
                        font-weight: bold;
                        color: #3b82f6;
                        margin-bottom: 5px;
                    }}
                    .stat-label {{
                        font-size: 14px;
                        color: #6b7280;
                    }}
                    .new-badge {{
                        background-color: #fef3c7;
                        color: #d97706;
                        padding: 4px 12px;
                        border-radius: 12px;
                        font-size: 12px;
                        font-weight: 600;
                        display: inline-block;
                        margin-left: 10px;
                    }}
                    .section {{
                        margin: 30px 0;
                    }}
                    .section-title {{
                        font-size: 18px;
                        font-weight: 600;
                        color: #1e40af;
                        margin-bottom: 15px;
                        display: flex;
                        align-items: center;
                    }}
                    .supplier-list {{
                        background-color: #f9fafb;
                        border-radius: 8px;
                        padding: 20px;
                    }}
                    .supplier-item {{
                        padding: 12px 0;
                        border-bottom: 1px solid #e5e7eb;
                    }}
                    .supplier-item:last-child {{
                        border-bottom: none;
                    }}
                    .supplier-name {{
                        font-weight: 600;
                        color: #1e40af;
                        margin-bottom: 4px;
                    }}
                    .supplier-info {{
                        font-size: 14px;
                        color: #6b7280;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 40px;
                        padding-top: 20px;
                        border-top: 1px solid #e5e7eb;
                        color: #6b7280;
                        font-size: 14px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div class="logo">🔘 俄罗斯纽扣供应商数据库</div>
                        <span class="date-badge">{datetime.now().strftime('%Y年%m月%d日')}</span>
                    </div>

                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-number">{total_count}</div>
                            <div class="stat-label">总供应商数</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">{email_count}</div>
                            <div class="stat-label">有邮箱</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">{phone_count}</div>
                            <div class="stat-label">有电话</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">{today_new} <span class="new-badge">今日新增</span></div>
                            <div class="stat-label">今日新增</div>
                        </div>
                    </div>

                    <div class="section">
                        <div class="section-title">
                            📋 最近更新的供应商
                        </div>
                        <div class="supplier-list">
            """

            # 添加最近更新的供应商
            for idx, supplier in enumerate(recent, 1):
                company_type = supplier.company_type or '未知'
                city = supplier.city or '未知'
                emails_text = ', '.join(supplier.emails[:2]) if supplier.emails else '无'
                html_content += f"""
                            <div class="supplier-item">
                                <div class="supplier-name">{idx}. {supplier.title[:50]}...</div>
                                <div class="supplier-info">
                                    类型: {company_type} | 城市: {city}<br>
                                    邮箱: {emails_text}
                                </div>
                            </div>
                """

            html_content += """
                        </div>
                    </div>

                    <div class="footer">
                        <p>俄罗斯纽扣供应商数据库 · 实时更新</p>
                        <p style="margin-top: 10px;">此为每日定时通知，如需取消请访问设置页面</p>
                    </div>
                </div>
            </body>
            </html>
            """

            return self.send_email(
                to_email=to_email,
                subject=f"📊 每日数据更新 · {datetime.now().strftime('%Y年%m月%d日')} · 俄罗斯纽扣供应商数据库",
                html_content=html_content,
                plain_text=f"今日供应商总数：{total_count}，今日新增：{today_new}"
            )

        except Exception as e:
            logger.error(f"发送每日通知失败: {e}")
            return False


# 全局实例
email_service = EmailService()

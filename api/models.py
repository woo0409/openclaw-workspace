"""
数据库模型
"""
from sqlalchemy import Column, Integer, String, Text, Date, JSON, TIMESTAMP
from sqlalchemy.sql import func
from core.database import Base


class Supplier(Base):
    """供应商模型"""

    __tablename__ = "suppliers"

    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增ID")

    # 基本信息
    title = Column(String(255), nullable=False, comment="公司标题")
    url = Column(String(500), nullable=False, unique=True, comment="公司网址")
    domain = Column(String(255), nullable=False, comment="域名")

    # 联系方式
    emails = Column(JSON, nullable=False, comment="邮箱列表")
    phones = Column(JSON, nullable=False, comment="电话列表")

    # 地址信息
    address = Column(Text, nullable=True, comment="详细地址")
    city = Column(String(100), nullable=True, comment="城市")
    country = Column(String(50), nullable=False, default="Russia", comment="国家")

    # 公司信息
    company_type = Column(String(50), nullable=False, default="供应商", comment="公司类型")
    description_cn = Column(Text, nullable=True, comment="中文描述")
    content = Column(Text, nullable=True, comment="原始网页内容摘要")

    # 分类标签
    tags = Column(JSON, nullable=True, comment="标签列表")

    # 来源标记
    source = Column(String(50), nullable=False, default="tavily", comment="搜索来源")

    # 时间戳
    date_found = Column(Date, nullable=False, comment="首次发现日期")
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), comment="记录创建时间")
    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        comment="记录更新时间"
    )

    def __repr__(self):
        return f"<Supplier(id={self.id}, title='{self.title}', url='{self.url}')>"

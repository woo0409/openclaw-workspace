"""
供应商服务 - CRUD 操作
"""
from typing import List, Optional, Dict, Any
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from api.models import Supplier
from api.schemas import SupplierCreate, SupplierUpdate
from core.logger import get_logger


class SupplierService:
    """供应商服务"""

    # 类级别的日志记录器
    logger = get_logger(__name__)

    @staticmethod
    def create(db: Session, supplier_data: SupplierCreate) -> Supplier:
        """
        创建供应商

        Args:
            db: 数据库会话
            supplier_data: 供应商数据

        Returns:
            创建的供应商
        """
        # 使用 INSERT IGNORE 避免重复
        try:
            supplier = Supplier(**supplier_data.model_dump())
            db.add(supplier)
            db.commit()
            db.refresh(supplier)
            return supplier
        except Exception as e:
            db.rollback()
            # 检查是否是重复键错误
            if 'Duplicate entry' in str(e) and 'url' in str(e):
                self.logger.debug(f"URL 已存在，跳过: {supplier_data.url}")
                return None
            raise e

    @staticmethod
    def create_batch(db: Session, suppliers_data: List[Dict[str, Any]]) -> int:
        """
        批量创建供应商（自动去重）

        Args:
            db: 数据库会话
            suppliers_data: 供应商数据列表

        Returns:
            成功创建的数量
        """
        created_count = 0

        for supplier_data in suppliers_data:
            try:
                supplier = Supplier(**supplier_data)
                db.add(supplier)
                db.commit()
                created_count += 1
            except Exception as e:
                db.rollback()
                # 检查是否是重复键错误
                if 'Duplicate entry' in str(e) and 'url' in str(e):
                    self.logger.debug(f"URL 已存在，跳过: {supplier_data.get('url')}")
                    continue
                self.logger.error(f"创建失败: {e}")
                continue

        return created_count

    @staticmethod
    def get_by_id(db: Session, supplier_id: int) -> Optional[Supplier]:
        """
        根据 ID 获取供应商

        Args:
            db: 数据库会话
            supplier_id: 供应商 ID

        Returns:
            供应商对象或 None
        """
        return db.query(Supplier).filter(Supplier.id == supplier_id).first()

    @staticmethod
    def get_by_url(db: Session, url: str) -> Optional[Supplier]:
        """
        根据 URL 获取供应商

        Args:
            db: 数据库会话
            url: 供应商 URL

        Returns:
            供应商对象或 None
        """
        return db.query(Supplier).filter(Supplier.url == url).first()

    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 50,
        date_filter: Optional[date] = None,
        keyword: Optional[str] = None,
        company_type: Optional[str] = None,
        city: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> tuple[List[Supplier], int]:
        """
        获取供应商列表（支持筛选和搜索）

        Args:
            db: 数据库会话
            skip: 跳过数量（分页）
            limit: 返回数量（分页）
            date_filter: 日期筛选
            keyword: 搜索关键词
            company_type: 公司类型筛选
            city: 城市筛选
            tags: 标签筛选

        Returns:
            (供应商列表, 总数)
        """
        query = db.query(Supplier)

        # 日期筛选
        if date_filter:
            query = query.filter(Supplier.date_found == date_filter)

        # 关键词搜索（全文搜索或模糊匹配）
        if keyword:
            keyword = f"%{keyword}%"
            query = query.filter(
                or_(
                    Supplier.title.like(keyword),
                    Supplier.description_cn.like(keyword),
                    Supplier.address.like(keyword)
                )
            )

        # 公司类型筛选
        if company_type:
            query = query.filter(Supplier.company_type == company_type)

        # 城市筛选
        if city:
            query = query.filter(Supplier.city == city)

        # 标签筛选（JSON 包含）
        if tags:
            for tag in tags:
                query = query.filter(Supplier.tags.contains(tag))

        # 获取总数
        total = query.count()

        # 分页
        suppliers = query.order_by(Supplier.date_found.desc()).offset(skip).limit(limit).all()

        return suppliers, total

    @staticmethod
    def get_all_dates(db: Session) -> List[date]:
        """
        获取所有有数据的日期

        Args:
            db: 数据库会话

        Returns:
            日期列表（降序）
        """
        dates = db.query(Supplier.date_found).distinct().order_by(Supplier.date_found.desc()).all()
        return [d[0] for d in dates]

    @staticmethod
    def get_stats(db: Session) -> Dict[str, Any]:
        """
        获取统计数据

        Args:
            db: 数据库会话

        Returns:
            统计数据
        """
        # 总数
        total_count = db.query(func.count(Supplier.id)).scalar()

        # 俄罗斯域名数量
        ru_domain_count = db.query(func.count(Supplier.id)).filter(
            Supplier.domain.like('%.ru%')
        ).scalar()

        # 有电话的数量
        phone_count = db.query(func.count(Supplier.id)).filter(
            Supplier.phones != '[]'
        ).scalar()

        # 有邮箱的数量
        email_count = db.query(func.count(Supplier.id)).filter(
            Supplier.emails != '[]'
        ).scalar()

        # 有地址的数量
        address_count = db.query(func.count(Supplier.id)).filter(
            Supplier.address.isnot(None)
        ).scalar()

        # 按类型分组
        type_stats = db.query(
            Supplier.company_type,
            func.count(Supplier.id)
        ).group_by(Supplier.company_type).all()

        # 按城市分组（Top 10）
        city_stats = db.query(
            Supplier.city,
            func.count(Supplier.id)
        ).filter(Supplier.city.isnot(None)).group_by(Supplier.city).order_by(
            func.count(Supplier.id).desc()
        ).limit(10).all()

        return {
            'total_count': total_count,
            'ru_domain_count': ru_domain_count,
            'phone_count': phone_count,
            'email_count': email_count,
            'address_count': address_count,
            'type_stats': {t[0]: t[1] for t in type_stats},
            'city_stats': {c[0]: c[1] for c in city_stats}
        }

    @staticmethod
    def update(db: Session, supplier_id: int, supplier_data: SupplierUpdate) -> Optional[Supplier]:
        """
        更新供应商

        Args:
            db: 数据库会话
            supplier_id: 供应商 ID
            supplier_data: 更新数据

        Returns:
            更新后的供应商或 None
        """
        supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()

        if not supplier:
            return None

        # 更新字段
        update_data = supplier_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(supplier, key, value)

        db.commit()
        db.refresh(supplier)
        return supplier

    @staticmethod
    def delete(db: Session, supplier_id: int) -> bool:
        """
        删除供应商

        Args:
            db: 数据库会话
            supplier_id: 供应商 ID

        Returns:
            是否成功
        """
        supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()

        if not supplier:
            return False

        db.delete(supplier)
        db.commit()
        return True

    @staticmethod
    def search_fulltext(db: Session, keyword: str, skip: int = 0, limit: int = 50) -> tuple[List[Supplier], int]:
        """
        全文搜索（使用 MySQL FULLTEXT 索引）

        Args:
            db: 数据库会话
            keyword: 搜索关键词
            skip: 跳过数量
            limit: 返回数量

        Returns:
            (供应商列表, 总数)
        """
        # 注意：MySQL FULLTEXT 需要正确的引擎和索引配置
        # 如果不支持，回退到模糊搜索

        try:
            # 尝试全文搜索
            query = db.query(Supplier).filter(
                or_(
                    Supplier.title.like(f'%{keyword}%'),
                    Supplier.description_cn.like(f'%{keyword}%'),
                    Supplier.address.like(f'%{keyword}%')
                )
            )

            total = query.count()
            suppliers = query.order_by(Supplier.date_found.desc()).offset(skip).limit(limit).all()

            return suppliers, total
        except Exception as e:
            self.logger.warning(f"全文搜索失败，使用模糊搜索: {e}")
            return SupplierService.get_all(db, skip, limit, keyword=keyword)

    @staticmethod
    def get_total_count(db: Session) -> int:
        """
        获取总数量

        Args:
            db: 数据库会话

        Returns:
            总数量
        """
        return db.query(func.count(Supplier.id)).scalar()

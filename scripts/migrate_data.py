#!/usr/bin/env python3
"""
数据迁移脚本 - 将 JSON 数据导入 MySQL
"""
import sys
import json
from pathlib import Path
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from api.models import Supplier  # noqa: E402
from core.config import settings  # noqa: E402
from core.logger import setup_logging, get_logger  # noqa: E402

# 初始化日志
setup_logging()
logger = get_logger(__name__)


def migrate_json_to_db():
    """迁移 JSON 数据到数据库"""

    logger.info("开始数据迁移...")

    # 创建数据库连接
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # 创建表
    logger.info("创建数据库表...")
    from core.database import Base
    Base.metadata.create_all(bind=engine)
    logger.info("数据库表创建完成")

    # 创建会话
    db = SessionLocal()

    try:
        # 读取 JSON 数据
        json_file = Path(__file__).parent.parent.parent / 'memory' / 'russia_button_suppliers_all.json'

        if not json_file.exists():
            logger.error(f"JSON 文件不存在: {json_file}")
            return

        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        companies = data.get('companies', [])
        logger.info(f"读取到 {len(companies)} 家公司")

        # 迁移数据
        success_count = 0
        duplicate_count = 0

        for company in companies:
            try:
                # 映射字段
                supplier_data = {
                    'title': company.get('title', '')[:255],
                    'url': company.get('url', '')[:500],
                    'domain': company.get('url', '').split('/')[2].replace('www.', '')[:255],
                    'emails': company.get('emails', []),
                    'phones': company.get('phones', []),
                    'address': None,
                    'city': None,
                    'country': 'Russia',
                    'company_type': company.get('company_type', '供应商'),
                    'description_cn': company.get('description_cn', ''),
                    'content': company.get('content', '')[:1000],
                    'tags': [],
                    'source': 'migration',
                    'date_found': company.get('date_found', datetime.now().strftime('%Y-%m-%d'))
                }

                # 创建供应商
                supplier = Supplier(**supplier_data)
                db.add(supplier)
                db.commit()
                success_count += 1
                logger.info(f"迁移成功: {supplier_data['title'][:50]}")

            except Exception as e:
                db.rollback()
                if 'Duplicate entry' in str(e) and 'url' in str(e):
                    duplicate_count += 1
                    logger.debug(f"跳过重复: {company.get('url', '')}")
                else:
                    logger.error(f"迁移失败: {e}")

        logger.info("迁移完成:")
        logger.info(f"成功: {success_count}")
        logger.info(f"重复: {duplicate_count}")
        logger.info(f"总数: {len(companies)}")

        # 验证数据
        from sqlalchemy import func
        total_count = db.query(func.count(Supplier.id)).scalar()
        logger.info(f"数据库中现有 {total_count} 家供应商")

    except Exception as e:
        logger.error(f"迁移失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        db.close()


if __name__ == '__main__':
    migrate_json_to_db()

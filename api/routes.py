"""
API 路由
"""
from io import BytesIO
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from core.database import get_db
from core.logger import get_logger
from api.models import Supplier
from api.schemas import (
    SupplierResponse,
    SupplierListResponse,
    SupplierCreate,
    SupplierUpdate,
    SearchRequest,
    SearchResponse,
    HealthResponse
)
from services.search import SearchService
from services.dedupe import DedupeService
from services.supplier import SupplierService
from core.security import verify_api_key


router = APIRouter()
logger = get_logger(__name__)


# ==================== 健康检查 ====================

@router.get("/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """
    健康检查
    """
    try:
        # 测试数据库连接
        db.execute("SELECT 1")

        return HealthResponse(
            status="healthy",
            database="connected",
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        )


# ==================== 搜索 ====================

@router.post("/search", response_model=SearchResponse, dependencies=[Depends(verify_api_key)])
async def search_suppliers(
    request: SearchRequest,
    db: Session = Depends(get_db)
):
    """
    执行搜索并更新数据库

    触发方式：
    - manual: 手动触发
    - cron: 定时任务触发
    """
    logger.info(f"开始搜索（触发方式: {request.trigger}）")

    try:
        search_service = SearchService()

        # 1. 获取已存在的域名
        existing_domains = DedupeService.get_existing_domains(db)
        logger.info(f"数据库中已存在 {len(existing_domains)} 个域名")

        # 2. 执行搜索
        results = search_service.search_by_tavily()
        logger.info(f"搜索到 {len(results)} 个结果")

        # 3. 处理搜索结果
        new_companies = search_service.process_search_results(results, existing_domains)

        if not new_companies:
            logger.info("搜索完成，没有找到新的供应商")
            return SearchResponse(
                success=True,
                message="搜索完成，没有找到新的供应商",
                new_companies=0,
                total_count=SupplierService.get_total_count(db),
                search_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )

        # 4. 批量插入数据库
        logger.info(f"开始插入 {len(new_companies)} 家公司到数据库...")
        created_count = SupplierService.create_batch(db, new_companies)
        logger.info(f"成功插入 {created_count} 家公司")

        # 5. 返回结果
        total_count = SupplierService.get_total_count(db)

        return SearchResponse(
            success=True,
            message=f"搜索完成，新增 {created_count} 家供应商",
            new_companies=created_count,
            total_count=total_count,
            search_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )

    except Exception as e:
        logger.error(f"搜索失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"搜索失败: {str(e)}"
        )


# ==================== 供应商 CRUD ====================

@router.get("/suppliers", response_model=SupplierListResponse)
async def get_suppliers(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=200, description="每页数量"),
    date_filter: Optional[str] = Query(None, description="日期筛选 (YYYY-MM-DD)"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    company_type: Optional[str] = Query(None, description="公司类型"),
    city: Optional[str] = Query(None, description="城市"),
    tags: Optional[str] = Query(None, description="标签 (逗号分隔)"),
    db: Session = Depends(get_db)
):
    """
    获取供应商列表

    支持分页、筛选和搜索
    """
    try:
        skip = (page - 1) * page_size

        # 处理日期筛选
        date_obj = None
        if date_filter:
            try:
                date_obj = datetime.strptime(date_filter, '%Y-%m-%d').date()
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="日期格式错误，请使用 YYYY-MM-DD"
                )

        # 处理标签筛选
        tags_list = None
        if tags:
            tags_list = [t.strip() for t in tags.split(',') if t.strip()]

        # 获取供应商列表
        suppliers, total = SupplierService.get_all(
            db=db,
            skip=skip,
            limit=page_size,
            date_filter=date_obj,
            keyword=keyword,
            company_type=company_type,
            city=city,
            tags=tags_list
        )

        # 计算总页数
        total_pages = (total + page_size - 1) // page_size

        return SupplierListResponse(
            suppliers=suppliers,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取供应商列表失败: {str(e)}"
        )


@router.get("/suppliers/{supplier_id}", response_model=SupplierResponse)
async def get_supplier(supplier_id: int, db: Session = Depends(get_db)):
    """
    根据 ID 获取供应商
    """
    supplier = SupplierService.get_by_id(db, supplier_id)

    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"供应商不存在 (ID: {supplier_id})"
        )

    return supplier


@router.post("/suppliers", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_api_key)])
async def create_supplier(
    supplier_data: SupplierCreate,
    db: Session = Depends(get_db)
):
    """
    创建供应商（手动导入）
    """
    try:
        supplier = SupplierService.create(db, supplier_data)

        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="URL 已存在"
            )

        return supplier

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建供应商失败: {str(e)}"
        )


@router.put("/suppliers/{supplier_id}", response_model=SupplierResponse, dependencies=[Depends(verify_api_key)])
async def update_supplier(
    supplier_id: int,
    supplier_data: SupplierUpdate,
    db: Session = Depends(get_db)
):
    """
    更新供应商
    """
    supplier = SupplierService.update(db, supplier_id, supplier_data)

    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"供应商不存在 (ID: {supplier_id})"
        )

    return supplier


@router.delete("/suppliers/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(verify_api_key)])
async def delete_supplier(supplier_id: int, db: Session = Depends(get_db)):
    """
    删除供应商
    """
    success = SupplierService.delete(db, supplier_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"供应商不存在 (ID: {supplier_id})"
        )

    return None


# ==================== 统计和元数据 ====================

@router.get("/export/suppliers")
async def export_suppliers(
    date_filter: Optional[str] = Query(None, description="日期筛选 (YYYY-MM-DD)"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    company_type: Optional[str] = Query(None, description="公司类型"),
    city: Optional[str] = Query(None, description="城市"),
    tags: Optional[str] = Query(None, description="标签 (逗号分隔)"),
    db: Session = Depends(get_db)
):
    """
    导出供应商数据为Excel文件

    支持分页、筛选和搜索
    """
    from fastapi.responses import StreamingResponse
    from services.export import ExportService

    try:
        # 处理日期筛选
        date_obj = None
        if date_filter:
            try:
                date_obj = datetime.strptime(date_filter, '%Y-%m-%d').date()
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="日期格式错误，请使用 YYYY-MM-DD"
                )

        # 处理标签筛选
        tags_list = None
        if tags:
            tags_list = [t.strip() for t in tags.split(',') if t.strip()]

        # 生成Excel文件
        excel_data = ExportService.export_to_excel(
            db=db,
            date_filter=date_obj,
            keyword=keyword,
            company_type=company_type,
            city=city,
            tags=tags_list
        )

        # 生成文件名
        filename = ExportService.get_filename("suppliers")

        # 返回文件
        return StreamingResponse(
            BytesIO(excel_data),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename*=utf-8''{filename}"}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导出失败: {str(e)}"
        )


@router.get("/suppliers/metadata/dates")
async def get_supplier_dates(db: Session = Depends(get_db)):
    """
    获取所有有数据的日期
    """
    try:
        dates = SupplierService.get_all_dates(db)
        return {"dates": dates}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取日期列表失败: {str(e)}"
        )


@router.get("/suppliers/metadata/stats")
async def get_supplier_stats(db: Session = Depends(get_db)):
    """
    获取统计数据
    """
    try:
        stats = SupplierService.get_stats(db)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计数据失败: {str(e)}"
        )


@router.get("/suppliers/metadata/types")
async def get_supplier_types(db: Session = Depends(get_db)):
    """
    获取所有公司类型
    """
    try:
        types = db.query(Supplier.company_type).distinct().all()
        return {"types": [t[0] for t in types]}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取公司类型失败: {str(e)}"
        )


@router.get("/suppliers/metadata/cities")
async def get_supplier_cities(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    获取城市列表（按数量排序）
    """
    try:
        from sqlalchemy import func

        cities = db.query(
            Supplier.city,
            func.count(Supplier.id)
        ).filter(Supplier.city.isnot(None)).group_by(Supplier.city).order_by(
            func.count(Supplier.id).desc()
        ).limit(limit).all()

        return {"cities": [{"city": c[0], "count": c[1]} for c in cities]}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取城市列表失败: {str(e)}"
        )


# ==================== 调度器 ====================

@router.get("/scheduler/status", response_model=dict)
async def get_scheduler_status():
    """
    获取任务调度器状态
    """
    from services.scheduler import scheduler

    return scheduler.get_jobs_status()


@router.post("/scheduler/trigger/search", dependencies=[Depends(verify_api_key)])
async def trigger_search_task(db: Session = Depends(get_db)):
    """
    手动触发供应商搜索任务
    """
    from services.scheduler import TaskScheduler
    from core.logger import get_logger

    logger = get_logger(__name__)
    logger.info("🔄 手动触发供应商搜索任务")

    # 执行搜索任务
    TaskScheduler._search_suppliers_job()

    return {
        "success": True,
        "message": "任务已触发",
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

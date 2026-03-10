"""
定时任务调度器 - 统一管理所有定时任务
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from core.database import get_db
from services.search import SearchService
from core.logger import get_logger


class TaskScheduler:
    """任务调度器 - 单例模式"""

    _instance = None
    _scheduler = None
    _logger = None

    def __new__(cls):
        """确保单例"""
        if cls._instance is None:
            cls._instance = super(TaskScheduler, cls).__new__(cls)
            cls._logger = get_logger(__name__)
            cls._scheduler = BackgroundScheduler(
                timezone='Asia/Shanghai',
                job_defaults={
                    'coalesce': True,  # 合并错过的任务
                    'max_instances': 1,  # 同一任务最多一个实例
                    'misfire_grace_time': 300  # 错过3分钟内仍执行
                }
            )
        return cls._instance

    @classmethod
    def start(cls):
        """启动调度器"""
        if cls._scheduler and not cls._scheduler.running:
            # 配置定时任务
            cls._setup_scheduled_jobs()
            cls._scheduler.start()
            cls._logger.info("✅ 任务调度器已启动")
            cls._logger.info("📅 已配置定时任务：")
            for job in cls._scheduler.get_jobs():
                cls._logger.info(f"  - {job.id}: {job.next_run_time}")
        else:
            cls._logger.warning("⚠️ 调度器已在运行或未初始化")

    @classmethod
    def stop(cls):
        """停止调度器"""
        if cls._scheduler and cls._scheduler.running:
            cls._scheduler.shutdown(wait=True)
            cls._logger.info("🛑 任务调度器已停止")

    @classmethod
    def _setup_scheduled_jobs(cls):
        """配置所有定时任务"""
        # ==================== 供应商搜索任务 ====================
        cls._scheduler.add_job(
            cls._search_suppliers_job,
            trigger=CronTrigger(
                hour=9,       # 每天9:00
                minute=0,
                second=0,
                timezone='Asia/Shanghai'
            ),
            id='search_suppliers',
            name='供应商搜索',
            replace_existing=True
        )

        cls._logger.info("✅ 已配置定时任务：供应商搜索（每天 9:00）")

    @classmethod
    def _search_suppliers_job(cls):
        """定时搜索供应商任务"""
        try:
            cls._logger.info("🔍 开始执行供应商搜索定时任务...")

            # 调用搜索服务
            search_service = SearchService()

            # 获取已存在的域名
            from services.dedupe import DedupeService
            existing_domains = DedupeService.get_existing_domains(db := next(get_db()))
            cls._logger.info(f"📊 数据库中已存在 {len(existing_domains)} 个域名")

            # 执行搜索
            results = search_service.search_by_tavily()
            cls._logger.info(f"🔎 搜索到 {len(results)} 个结果")

            # 处理搜索结果
            new_companies = search_service.process_search_results(results, existing_domains)
            cls._logger.info(f"➕ 处理完成，找到 {len(new_companies)} 家新公司")

            # 批量保存到数据库
            if new_companies:
                from services.supplier import SupplierService
                created_count = SupplierService.create_batch(db, new_companies)
                cls._logger.info(f"💾 成功保存 {created_count} 家新供应商")

                # 更新统计
                from api.models import Supplier
                total_count = db.query(Supplier.__class__).count()
                cls._logger.info(f"📈 数据库总供应商数量: {total_count}")

        except Exception as e:
            cls._logger.error(f"❌ 定时搜索任务执行失败: {e}")
            import traceback
            cls._logger.error(traceback.format_exc())

    @classmethod
    def get_jobs_status(cls):
        """获取所有任务状态"""
        if not cls._scheduler or not cls._scheduler.running:
            return {
                'status': 'stopped',
                'jobs': []
            }

        jobs = []
        for job in cls._scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                'last_run_time': job.last_run_time.isoformat() if job.last_run_time else None,
                'trigger': str(job.trigger)
            })

        return {
            'status': 'running',
            'jobs': jobs
        }


# 全局调度器实例
scheduler = TaskScheduler()

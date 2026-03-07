"""
统一日志配置模块
提供标准化的日志记录器配置
"""
import logging
import sys
from pathlib import Path
from typing import Optional

from core.config import settings


class ColoredFormatter(logging.Formatter):
    """带颜色的控制台日志格式化器（仅限非Windows终端）"""

    # ANSI颜色代码
    COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[32m',       # 绿色
        'WARNING': '\033[33m',    # 黄色
        'ERROR': '\033[31m',      # 红色
        'CRITICAL': '\033[35m',   # 紫色
    }
    RESET = '\033[0m'

    def format(self, record):
        # 添加颜色
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[Path] = None,
    use_colors: bool = True
) -> None:
    """
    配置应用的日志系统

    Args:
        level: 日志级别，默认为 INFO
        log_file: 日志文件路径（可选）
        use_colors: 是否在控制台使用颜色
    """
    # 创建根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # 清除现有处理器
    root_logger.handlers.clear()

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # 格式化器
    if use_colors and sys.stdout.isatty():
        formatter = ColoredFormatter(
            fmt='%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # 文件处理器（可选）
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)

        # 文件使用不含颜色的格式
        file_formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的日志记录器

    Args:
        name: 日志记录器名称，通常使用 __name__

    Returns:
        配置好的日志记录器实例
    """
    return logging.getLogger(name)


# 初始化默认配置（在应用启动时调用）
def init_logging() -> None:
    """
    初始化应用日志系统
    根据环境变量和配置决定日志级别和输出方式
    """
    # 从配置获取日志级别
    log_level_str = getattr(settings, 'LOG_LEVEL', 'INFO').upper()
    log_level = getattr(logging, log_level_str, logging.INFO)

    # 是否启用文件日志
    log_file = None
    if hasattr(settings, 'LOG_FILE') and settings.LOG_FILE:
        log_file = Path(settings.LOG_FILE)

    # 初始化日志
    setup_logging(level=log_level, log_file=log_file)

    # 记录初始化信息
    logger = get_logger('backend')
    logger.info(f"应用日志系统已初始化，级别: {log_level_str}")
    if log_file:
        logger.info(f"日志文件: {log_file}")

"""
配置管理 - 企业级分层配置方案

配置加载优先级（从高到低）：
1. 环境变量
2. .env 文件
3. 代码默认值（仅限非敏感配置）
"""
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, Field


class Settings(BaseSettings):
    """应用配置 - 分层配置管理"""

    # ==================== 应用信息 ====================
    APP_NAME: str = "Russia Buttons API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    TZ: str = "Asia/Shanghai"

    # ==================== 数据库配置 ====================
    # 必需配置 - 无默认值，强制通过环境变量配置
    DATABASE_URL: str = Field(
        default="",
        description="数据库连接字符串，格式：mysql+pymysql://user:password@host:port/database"
    )
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10

    # ==================== API密钥 ====================
    # 必需配置 - 无默认值，强制通过环境变量配置
    TAVILY_API_KEY: str = Field(
        default="",
        description="Tavily搜索API密钥"
    )

    # API认证密钥 - 使用强随机值
    API_KEY: str = Field(
        default="",
        description="API认证密钥，用于保护写操作接口"
    )

    # ==================== 搜索配置 ====================
    # 业务配置 - 提供默认值
    MAX_RESULTS_PER_QUERY: int = 5
    MAX_NEW_SUPPLIERS: int = 6
    SEARCH_QUERIES: List[str] = [
        'site:ru пуговицы оптом производитель contact email',
        'Moscow швейная фурнитура пуговицы оптом email',
        'Russia button manufacturer LLC contact',
        'Ivanovo Voronezh пуговицы фабрика оптом',
        'Russian garment accessories button supplier contact',
        'Moscow clothing fastener button wholesale email'
    ]

    # ==================== API配置 ====================
    API_PREFIX: str = "/api"
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # ==================== 分页配置 ====================
    DEFAULT_PAGE_SIZE: int = 50
    MAX_PAGE_SIZE: int = 200

    # ==================== 日志配置 ====================
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_FILE: str = ""  # 日志文件路径（可选，为空则不记录文件）

    # ==================== Pydantic配置 ====================
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # 忽略额外的环境变量
    )

    # ==================== 验证器 ====================
    @field_validator('DATABASE_URL', 'TAVILY_API_KEY', 'API_KEY')
    @classmethod
    def validate_required_secrets(cls, v: str, info) -> str:
        """验证必需的敏感配置"""
        if not v or v.strip() == "":
            raise ValueError(
                f"{info.field_name} 环境变量不能为空，请在 .env 文件中配置"
            )
        return v

    @field_validator('ALLOWED_ORIGINS')
    @classmethod
    def validate_origins(cls, v: str) -> str:
        """验证并标准化CORS origins"""
        if not v or v.strip() == "":
            return "http://localhost:5173"
        return v

    @field_validator('LOG_LEVEL')
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """验证日志级别"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"LOG_LEVEL 必须是以下之一: {', '.join(valid_levels)}")
        return v_upper

    # ==================== 辅助属性 ====================
    @property
    def allowed_origins_list(self) -> List[str]:
        """获取 ALLOWED_ORIGINS 列表"""
        if self.ALLOWED_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        """判断是否为生产环境"""
        return not self.DEBUG

    @property
    def is_development(self) -> bool:
        """判断是否为开发环境"""
        return self.DEBUG


def load_settings(env_file: Optional[str] = None) -> Settings:
    """
    加载配置，支持指定 .env 文件路径

    Args:
        env_file: .env 文件路径（可选）

    Returns:
        配置实例

    Raises:
        ValueError: 当必需的配置项缺失时
    """
    try:
        if env_file:
            # 支持自定义 .env 文件路径
            settings = Settings(_env_file=env_file)
        else:
            settings = Settings()

        # 验证关键配置
        if settings.DEBUG:
            print(f"⚠️  开发模式已启用 - DEBUG={settings.DEBUG}")
            print(f"📝 配置来源: .env 文件 + 环境变量")

        return settings

    except ValueError as e:
        print(f"❌ 配置错误: {e}")
        print("\n请确保已创建 .env 文件并配置以下必需项：")
        print("  - DATABASE_URL")
        print("  - TAVILY_API_KEY")
        print("  - API_KEY")
        print("\n可以复制 .env.example 为 .env 并填入实际值")
        raise


# 全局配置实例
settings = load_settings()

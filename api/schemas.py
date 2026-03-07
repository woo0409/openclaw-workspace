"""
Pydantic 模式 - API 请求和响应模型
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime


class SupplierBase(BaseModel):
    """供应商基础模型"""
    title: str = Field(..., description="公司标题", max_length=255)
    url: str = Field(..., description="公司网址", max_length=500)
    domain: str = Field(..., description="域名", max_length=255)
    emails: List[str] = Field(default_factory=list, description="邮箱列表")
    phones: List[str] = Field(default_factory=list, description="电话列表")
    address: Optional[str] = Field(None, description="详细地址")
    city: Optional[str] = Field(None, description="城市", max_length=100)
    country: str = Field(default="Russia", description="国家", max_length=50)
    company_type: str = Field(default="供应商", description="公司类型", max_length=50)
    description_cn: Optional[str] = Field(None, description="中文描述")
    content: Optional[str] = Field(None, description="原始网页内容摘要")
    tags: Optional[List[str]] = Field(default_factory=list, description="标签列表")
    source: str = Field(default="tavily", description="搜索来源", max_length=50)
    date_found: date = Field(..., description="首次发现日期")


class SupplierCreate(SupplierBase):
    """创建供应商请求模型"""
    pass


class SupplierUpdate(BaseModel):
    """更新供应商请求模型"""
    title: Optional[str] = Field(None, max_length=255)
    emails: Optional[List[str]] = None
    phones: Optional[List[str]] = None
    address: Optional[str] = None
    city: Optional[str] = None
    company_type: Optional[str] = None
    description_cn: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None


class SupplierResponse(SupplierBase):
    """供应商响应模型"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SupplierListResponse(BaseModel):
    """供应商列表响应模型"""
    suppliers: List[SupplierResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class SearchRequest(BaseModel):
    """搜索请求模型"""
    trigger: Optional[str] = Field(default="manual", description="触发方式: manual/cron")


class SearchResponse(BaseModel):
    """搜索响应模型"""
    success: bool
    message: str
    new_companies: int
    total_count: int
    search_time: Optional[str] = None


class HealthResponse(BaseModel):
    """健康检查响应模型"""
    status: str
    database: str
    timestamp: datetime


class ErrorResponse(BaseModel):
    """错误响应模型"""
    error: str
    detail: Optional[str] = None

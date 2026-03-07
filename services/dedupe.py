"""
去重服务 - 基于域名
"""
from typing import List, Dict, Any, Set
from sqlalchemy.orm import Session
from api.models import Supplier
from core.logger import get_logger


class DedupeService:
    """去重服务"""

    # 类级别的日志记录器
    logger = get_logger(__name__)

    @staticmethod
    def get_existing_domains(db: Session) -> Set[str]:
        """
        从数据库获取已存在的域名

        Args:
            db: 数据库会话

        Returns:
            域名集合
        """
        try:
            suppliers = db.query(Supplier.domain).all()
            domains = {domain for (domain,) in suppliers}
            return domains
        except Exception as e:
            DedupeService.logger.warning(f"获取已存在域名失败: {e}")
            return set()

    @staticmethod
    def dedupe_by_domain(companies: List[Dict[str, Any]], existing_domains: Set[str]) -> List[Dict[str, Any]]:
        """
        基于域名去重

        Args:
            companies: 待处理的公司列表
            existing_domains: 已存在的域名集合

        Returns:
            去重后的新公司列表
        """
        new_companies = []
        seen_domains = set()

        for company in companies:
            domain = company.get('domain')

            if not domain:
                continue

            # 排除已存在的域名
            if domain in existing_domains:
                self.logger.debug(f"跳过已存在: {domain}")
                continue

            # 排除重复的域名（本次搜索中）
            if domain in seen_domains:
                self.logger.debug(f"跳过重复: {domain}")
                continue

            seen_domains.add(domain)
            new_companies.append(company)
            self.logger.info(f"新增: {domain}")

        return new_companies

    @staticmethod
    def dedupe_by_email(companies: List[Dict[str, Any]], existing_emails: Set[str]) -> List[Dict[str, Any]]:
        """
        基于邮箱去重（备选方案）

        Args:
            companies: 待处理的公司列表
            existing_emails: 已存在的邮箱集合

        Returns:
            去重后的新公司列表
        """
        new_companies = []

        for company in companies:
            emails = company.get('emails', [])

            if not emails:
                # 没有邮箱的公司，保留
                new_companies.append(company)
                continue

            # 检查是否有邮箱已存在
            has_existing_email = any(email.lower() in existing_emails for email in emails)

            if has_existing_email:
                self.logger.debug(f"跳过（邮箱已存在）: {emails[0]}")
                continue

            new_companies.append(company)
            self.logger.info(f"新增: {emails[0] if emails else company['url']}")

        return new_companies

    @staticmethod
    def get_existing_emails(db: Session) -> Set[str]:
        """
        从数据库获取已存在的邮箱

        Args:
            db: 数据库会话

        Returns:
            邮箱集合
        """
        try:
            suppliers = db.query(Supplier.emails).all()
            emails = set()
            for (emails_json,) in suppliers:
                if emails_json:
                    for email in emails_json:
                        if email:
                            emails.add(email.lower())
            return emails
        except Exception as e:
            self.logger.warning(f"获取已存在邮箱失败: {e}")
            return set()

    @staticmethod
    def validate_company(company: Dict[str, Any]) -> bool:
        """
        验证公司数据是否有效

        Args:
            company: 公司数据

        Returns:
            是否有效
        """
        # 必填字段
        required_fields = ['title', 'url', 'domain']
        for field in required_fields:
            if not company.get(field):
                self.logger.warning(f"缺少必填字段: {field}")
                return False

        # URL 格式检查
        url = company.get('url', '')
        if not url.startswith(('http://', 'https://')):
            self.logger.warning(f"URL 格式错误: {url}")
            return False

        # 至少要有邮箱或电话（可选）
        emails = company.get('emails', [])
        phones = company.get('phones', [])
        if not emails and not phones:
            self.logger.debug(f"缺少联系方式: {url}")
            # 允许没有联系方式的公司，但记录警告

        return True

    @staticmethod
    def clean_company_data(company: Dict[str, Any]) -> Dict[str, Any]:
        """
        清理公司数据

        Args:
            company: 原始公司数据

        Returns:
            清理后的公司数据
        """
        # 清理标题
        title = company.get('title', '').strip()
        company['title'] = title[:255]  # 限制长度

        # 清理 URL
        url = company.get('url', '').strip()
        company['url'] = url[:500]

        # 清理域名
        domain = company.get('domain', '').strip()
        company['domain'] = domain[:255]

        # 清理邮箱列表
        emails = company.get('emails', [])
        cleaned_emails = []
        for email in emails:
            email = email.strip().lower()
            if email and '@' in email:
                cleaned_emails.append(email)
        company['emails'] = cleaned_emails

        # 清理电话列表
        phones = company.get('phones', [])
        cleaned_phones = []
        for phone in phones:
            phone = phone.strip()
            if phone:
                cleaned_phones.append(phone)
        company['phones'] = cleaned_phones

        # 清理城市
        city = company.get('city')
        if city:
            company['city'] = city.strip()[:100]

        # 清理国家
        country = company.get('country', 'Russia')
        company['country'] = country.strip()[:50]

        # 清理公司类型
        company_type = company.get('company_type', '供应商')
        company['company_type'] = company_type.strip()[:50]

        # 清理标签
        tags = company.get('tags', [])
        cleaned_tags = []
        for tag in tags:
            tag = tag.strip()
            if tag:
                cleaned_tags.append(tag)
        company['tags'] = cleaned_tags

        # 清理来源
        source = company.get('source', 'tavily')
        company['source'] = source.strip()[:50]

        # 清理地址
        address = company.get('address')
        if address:
            company['address'] = address.strip()

        # 清理描述
        description_cn = company.get('description_cn')
        if description_cn:
            company['description_cn'] = description_cn.strip()

        # 清理内容
        content = company.get('content')
        if content:
            company['content'] = content.strip()[:2000]  # 限制长度

        return company

    @staticmethod
    def process_companies(companies: List[Dict[str, Any]], existing_urls: Set[str]) -> List[Dict[str, Any]]:
        """
        处理公司数据：验证、清理、去重

        Args:
            companies: 待处理的公司列表
            existing_urls: 已存在的 URL 集合

        Returns:
            处理后的公司列表
        """
        self.logger.info(f"开始处理 {len(companies)} 家公司...")

        new_companies = []

        for company in companies:
            # 清理数据
            company = DedupeService.clean_company_data(company)

            # 验证数据
            if not DedupeService.validate_company(company):
                continue

            # 去重
            new_companies.append(company)

        self.logger.info(f"处理完成，有效公司: {len(new_companies)} 家")
        return new_companies

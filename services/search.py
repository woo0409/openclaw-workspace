"""
搜索服务 - 调用现有搜索脚本
"""
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from tavily import TavilyClient
from core.config import settings
from core.logger import get_logger


class SearchService:
    """搜索服务 - 方案A：复用现有脚本"""

    def __init__(self):
        """初始化搜索服务"""
        self.tavily = TavilyClient(api_key=settings.TAVILY_API_KEY)
        self.project_dir = Path(__file__).parent.parent.parent
        self.memory_dir = self.project_dir / 'memory'
        self.scripts_dir = self.project_dir / 'scripts'
        self.logger = get_logger(__name__)

    def search_by_tavily(self) -> List[Dict[str, Any]]:
        """使用 Tavily API 搜索（直接调用，不依赖脚本）"""
        self.logger.info("开始 Tavily 搜索...")

        all_results = []
        for i, query in enumerate(settings.SEARCH_QUERIES[:4], 1):  # 限制前4个查询
            try:
                self.logger.info(f"[{i}/{len(settings.SEARCH_QUERIES)}] 搜索: {query[:50]}...")
                response = self.tavily.search(
                    query=query,
                    search_depth='advanced',
                    max_results=settings.MAX_RESULTS_PER_QUERY,
                    include_raw_content=True
                )
                all_results.extend(response['results'])
                self.logger.info(f"找到 {len(response['results'])} 个结果")
            except Exception as e:
                self.logger.error(f"搜索错误: {e}")

        self.logger.info(f"Tavily 搜索完成，总共找到 {len(all_results)} 个结果")
        return all_results

    def generate_company_data(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        从搜索结果生成公司数据

        Args:
            result: Tavily 搜索结果

        Returns:
            格式化的公司数据
        """
        import re
        from urllib.parse import urlparse

        url = result.get('url', '')
        title = result.get('title', '')[:255]
        content = result.get('raw_content', '')

        # 提取域名
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.replace('www.', '')

        # 提取联系方式
        emails = list(set(re.findall(r'[\w.-]+@[\w.-]+\.\w+', content)))
        phones = list(set(re.findall(r'\+7[\s\-\(\)]*\d{1,4}[\s\-\(\)]*\d{1,4}[\s\-\(\)]*\d{1,4}', content)))

        # 判断公司类型
        title_lower = title.lower()
        if 'производитель' in title_lower or 'производство' in title_lower:
            company_type = "制造商"
        elif 'оптом' in title_lower:
            company_type = "批发商"
        elif 'фурнитура' in title_lower:
            company_type = "服装配件供应商"
        else:
            company_type = "供应商"

        # 判断俄罗斯域名
        is_ru = '.ru' in url or '.ru' in domain

        # 生成描述
        if is_ru:
            description_cn = f"俄罗斯{company_type}，专业提供纽扣及服装配件服务，支持俄罗斯本地业务。"
        else:
            description_cn = f"{company_type}，专业提供纽扣及服装配件服务。"

        # 提取地址（简单版）
        address = None
        city = None

        # 尝试从内容中提取城市
        cities = ['Москва', 'Moscow', 'Иваново', 'Ivanovo', 'Воронеж', 'Voronezh', 'Санкт-Петербург', 'Saint Petersburg']
        for city_name in cities:
            if city_name in content:
                city = city_name
                break

        # 生成标签
        tags = []
        if 'металл' in title_lower or 'металлические' in title_lower:
            tags.append('金属纽扣')
        if 'пластик' in title_lower or 'пластиковые' in title_lower:
            tags.append('塑料纽扣')
        if 'дерево' in title_lower or 'деревянные' in title_lower:
            tags.append('木质纽扣')
        if 'заказ' in title_lower or 'на заказ' in title_lower:
            tags.append('定制服务')
        if tags:
            tags.append('纽扣')
        else:
            tags = ['纽扣']

        return {
            'title': title,
            'url': url,
            'domain': domain,
            'emails': emails[:2],  # 最多2个邮箱
            'phones': phones[:2],  # 最多2个电话
            'address': address,
            'city': city,
            'country': 'Russia',
            'company_type': company_type,
            'description_cn': description_cn,
            'content': content[:1000].replace('\n', ' '),
            'tags': tags,
            'source': 'tavily',
            'date_found': datetime.now().strftime('%Y-%m-%d')
        }

    def process_search_results(self, results: List[Dict[str, Any]], existing_domains: str) -> List[Dict[str, Any]]:
        """
        处理搜索结果，去重并格式化

        Args:
            results: 搜索结果列表
            existing_domains: 已存在的域名集合

        Returns:
            去重后的新供应商列表
        """
        new_companies = []
        seen_domains = set()

        for result in results:
            url = result.get('url', '')
            from urllib.parse import urlparse
            domain = urlparse(url).netloc.replace('www.', '')

            # 排除非俄罗斯网站
            exclude_keywords = ['alanic', 'goldtailor', 'made-in-china', '1688']
            if any(kw in url for kw in exclude_keywords):
                continue

            # 排除重复的域名
            if domain in seen_domains:
                continue
            seen_domains.add(domain)

            # 排除已存在的域名
            if domain in existing_domains:
                continue

            # 排除没有内容的页面
            content = result.get('raw_content', '')
            if not content or len(content) < 100:
                continue

            # 生成公司数据
            company_data = self.generate_company_data(result)
            new_companies.append(company_data)

            # 限制最大数量
            if len(new_companies) >= settings.MAX_NEW_SUPPLIERS:
                break

        self.logger.info(f"处理完成，找到 {len(new_companies)} 家新公司")
        return new_companies

if __name__ == '__main__':
    # 测试搜索情况
    search_service = SearchService()
    search_service.search_by_tavily()
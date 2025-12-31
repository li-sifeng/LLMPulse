"""
数据获取模块 - 负责从各种 RSS 源获取最新内容
"""
import feedparser
import requests
from datetime import datetime, timedelta
from typing import List, Dict
import time
import ssl

# 禁用 SSL 证书验证（仅用于解决某些 RSS 源的证书问题）
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context


class DataFetcher:
    """从配置的数据源获取内容"""

    def __init__(self, config: dict):
        self.config = config
        self.data_sources = config.get('data_sources', {})
        self.days_back = config.get('report', {}).get('days_back', 7)

    def fetch_all(self) -> Dict[str, List[Dict]]:
        """
        获取所有数据源的内容

        Returns:
            按类别分组的内容字典
        """
        results = {
            'industry': [],
            'academic': [],
            'applications': [],
            'startups': []
        }

        # 获取行业动态
        for source in self.data_sources.get('industry', []):
            items = self._fetch_rss(source)
            results['industry'].extend(items)

        # 获取学术前沿
        for source in self.data_sources.get('academic', []):
            items = self._fetch_rss(source)
            results['academic'].extend(items)

        # 获取应用生态
        for source in self.data_sources.get('applications', []):
            items = self._fetch_rss(source)
            results['applications'].extend(items)

        # 获取创业生态
        for source in self.data_sources.get('startups', []):
            items = self._fetch_rss(source)
            results['startups'].extend(items)

        # 按时间排序并过滤
        cutoff_date = datetime.now() - timedelta(days=self.days_back)
        for category in results:
            results[category] = self._filter_and_sort(results[category], cutoff_date)

        return results

    def _fetch_rss(self, source: Dict) -> List[Dict]:
        """
        获取单个 RSS 源的内容

        Args:
            source: 数据源配置

        Returns:
            内容列表
        """
        items = []
        try:
            print(f"正在获取: {source['name']}...")
            feed = feedparser.parse(source['url'])

            for entry in feed.entries:
                # 解析发布时间
                published = self._parse_date(entry)

                item = {
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'summary': entry.get('summary', entry.get('description', '')),
                    'published': published,
                    'source': source['name'],
                    'category': source.get('category', 'unknown')
                }
                items.append(item)

            print(f"  ✓ 获取到 {len(items)} 条内容")
            time.sleep(0.5)  # 避免请求过快

        except Exception as e:
            print(f"  ✗ 获取失败: {str(e)}")

        return items

    def _parse_date(self, entry) -> datetime:
        """解析 RSS entry 的日期"""
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            return datetime(*entry.published_parsed[:6])
        elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
            return datetime(*entry.updated_parsed[:6])
        else:
            return datetime.now()

    def _filter_and_sort(self, items: List[Dict], cutoff_date: datetime) -> List[Dict]:
        """
        过滤并排序内容

        Args:
            items: 内容列表
            cutoff_date: 截止日期

        Returns:
            过滤排序后的内容列表
        """
        # 过滤日期
        filtered = [item for item in items if item['published'] >= cutoff_date]

        # 按发布时间倒序排序
        sorted_items = sorted(filtered, key=lambda x: x['published'], reverse=True)

        # 限制数量
        max_items = self.config.get('report', {}).get('max_items_per_category', 10)
        return sorted_items[:max_items]

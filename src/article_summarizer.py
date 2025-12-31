"""
文章内容获取和摘要生成模块
"""
import requests
from bs4 import BeautifulSoup
from typing import Dict
import time
from anthropic import Anthropic
import os


class ArticleSummarizer:
    """获取文章内容并生成摘要"""

    def __init__(self, config: dict):
        self.config = config
        llm_config = config.get('llm', {})

        self.api_key = llm_config.get('api_key', os.getenv('ANTHROPIC_API_KEY'))
        self.model = llm_config.get('model', 'claude-3-5-sonnet-20241022')
        self.client = Anthropic(api_key=self.api_key)

        # 请求头，模拟浏览器
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def fetch_and_summarize(self, item: Dict) -> str:
        """
        获取文章内容并生成摘要

        Args:
            item: 包含 title, link, summary 的字典

        Returns:
            文章摘要（核心观点）
        """
        try:
            # 首先尝试从 RSS 的 summary 获取内容
            rss_summary = item.get('summary', '')

            # 如果是 arXiv 论文，直接使用 abstract
            if 'arxiv.org' in item.get('link', ''):
                return self._summarize_text(rss_summary, is_paper=True)

            # 对于博客文章，尝试获取完整内容
            content = self._fetch_article_content(item['link'])

            if content:
                # 如果成功获取到内容，用完整内容生成摘要
                return self._summarize_text(content, is_paper=False)
            else:
                # 如果获取失败，使用 RSS summary
                return self._summarize_text(rss_summary, is_paper=False)

        except Exception as e:
            print(f"  ⚠️  摘要生成失败 ({item.get('title', '')[:50]}...): {str(e)}")
            # 返回简短的备选摘要
            return item.get('summary', '')[:100] + '...' if item.get('summary') else '暂无摘要'

    def _fetch_article_content(self, url: str) -> str:
        """
        获取文章正文内容

        Args:
            url: 文章链接

        Returns:
            文章正文文本
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # 移除脚本和样式
            for script in soup(['script', 'style', 'nav', 'footer', 'header']):
                script.decompose()

            # 尝试找到主要内容区域（常见的类名）
            main_content = None
            for selector in ['article', 'main', '.post-content', '.article-content', '.entry-content']:
                main_content = soup.select_one(selector)
                if main_content:
                    break

            # 如果找不到主要内容，使用整个 body
            if not main_content:
                main_content = soup.body

            if main_content:
                # 获取文本，限制长度
                text = main_content.get_text(separator='\n', strip=True)
                # 限制为前 3000 字符（避免过长）
                return text[:3000]

            return ""

        except Exception as e:
            print(f"    ⚠️  无法获取文章内容: {str(e)}")
            return ""

    def _summarize_text(self, text: str, is_paper: bool = False) -> str:
        """
        使用 LLM 生成文章摘要

        Args:
            text: 文章文本
            is_paper: 是否为学术论文

        Returns:
            摘要文本
        """
        if not text or len(text.strip()) < 50:
            return "内容不足，无法生成摘要"

        # 构建提示词
        if is_paper:
            prompt = f"""请用一句话（30-50字）总结这篇学术论文的核心观点：

{text[:1500]}

要求：
- 只用一句话说明研究的核心创新点或主要发现
- 语言简洁专业
- 不要包含"本文"、"这篇论文"等开头
- 直接陈述核心内容

示例：提出了一种基于多模态的XXX方法，在YYY任务上提升了ZZZ性能。
"""
        else:
            prompt = f"""请用一句话（30-50字）总结这篇文章的核心观点：

{text[:1500]}

要求：
- 只用一句话说明文章的主要内容或观点
- 语言简洁易懂
- 不要包含"本文"、"这篇文章"等开头
- 直接陈述核心内容

示例：OpenAI发布了新的XXX功能，可以帮助用户YYY。
"""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=200,  # 摘要不需要太长
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            summary = message.content[0].text.strip()

            # 去除可能的引号
            summary = summary.strip('"').strip("'")

            return summary

        except Exception as e:
            print(f"    ⚠️  LLM 摘要失败: {str(e)}")
            # 返回文本的前 100 个字符作为备选
            return text[:100] + '...'

    def summarize_batch(self, items: list, max_workers: int = 3) -> list:
        """
        批量生成摘要（带进度显示）

        Args:
            items: 文章列表
            max_workers: 并发数量（为避免 API 限流，设置较小值）

        Returns:
            带摘要的文章列表
        """
        total = len(items)
        print(f"  开始生成 {total} 篇文章的摘要...")

        for idx, item in enumerate(items, 1):
            print(f"  [{idx}/{total}] {item.get('title', '')[:50]}...")

            # 生成摘要
            item['ai_summary'] = self.fetch_and_summarize(item)

            # 避免请求过快
            if idx < total:
                time.sleep(1)  # 每篇文章间隔1秒

        print(f"  ✓ 摘要生成完成")
        return items

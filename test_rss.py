"""
测试脚本 - 检查各个 RSS 源是否正常工作
"""
import feedparser
import sys
import io

# Windows 控制台 UTF-8 支持
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sources = {
    "OpenAI Blog": "https://openai.com/blog/rss.xml",
    "Anthropic News": "https://www.anthropic.com/news/rss",
    "Google AI Blog": "https://ai.googleblog.com/feeds/posts/default",
    "Meta AI Blog": "https://ai.meta.com/blog/rss/",
    "arXiv AI": "http://export.arxiv.org/rss/cs.AI",
    "arXiv CL": "http://export.arxiv.org/rss/cs.CL",
}

print("检查 RSS 源状态...\n")
print("=" * 70)

for name, url in sources.items():
    print(f"\n【{name}】")
    print(f"URL: {url}")
    try:
        feed = feedparser.parse(url)

        # 检查是否有错误
        if hasattr(feed, 'bozo') and feed.bozo:
            print(f"⚠️  解析警告: {feed.get('bozo_exception', 'Unknown error')}")

        # 检查状态
        if hasattr(feed, 'status'):
            print(f"HTTP 状态: {feed.status}")

        # 检查条目数
        entries_count = len(feed.entries)
        print(f"条目数量: {entries_count}")

        if entries_count > 0:
            print(f"✓ 最新条目: {feed.entries[0].get('title', 'No title')[:80]}")
            print(f"  发布时间: {feed.entries[0].get('published', 'No date')}")
        else:
            print(f"✗ 没有找到任何条目")
            print(f"  Feed 标题: {feed.feed.get('title', 'No title')}")
            print(f"  Feed 链接: {feed.feed.get('link', 'No link')}")

    except Exception as e:
        print(f"✗ 错误: {str(e)}")

    print("-" * 70)

"""
LLMPulse - AI 大语言模型领域周报生成器
主程序入口
"""
import os
import sys
import yaml
from pathlib import Path

# 设置控制台编码为 UTF-8（Windows 兼容性）
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.data_fetcher import DataFetcher
from src.llm_analyzer import LLMAnalyzer
from src.report_generator import ReportGenerator
from src.html_report_generator import HTMLReportGenerator
from src.article_summarizer import ArticleSummarizer


def load_config():
    """加载配置文件"""
    config_path = Path('config/config.yaml')

    if not config_path.exists():
        print("❌ 配置文件不存在!")
        print("请先复制 config/config.example.yaml 到 config/config.yaml 并填入你的配置")
        sys.exit(1)

    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    return config


def main():
    """主程序"""
    print("=" * 60)
    print("🚀 LLMPulse - AI 大语言模型周报生成器")
    print("=" * 60)
    print()

    # 加载配置
    print("📖 正在加载配置...")
    config = load_config()
    print("✓ 配置加载成功\n")

    # 初始化模块
    print("🔧 正在初始化模块...")
    fetcher = DataFetcher(config)
    analyzer = LLMAnalyzer(config)

    # 根据配置选择报告生成器
    output_format = config.get('report', {}).get('output_format', 'markdown')
    if output_format == 'html':
        generator = HTMLReportGenerator(config)
        print("✓ 使用 HTML 格式生成报告")
    else:
        generator = ReportGenerator(config)
        print("✓ 使用 Markdown 格式生成报告")
    print("✓ 模块初始化成功\n")

    # 获取数据
    print("📡 正在获取数据源...")
    print("-" * 60)
    data = fetcher.fetch_all()
    print("-" * 60)
    print(f"✓ 数据获取完成\n")

    # 统计信息
    total_items = sum(len(items) for items in data.values())
    print(f"📊 本周共获取 {total_items} 条内容:")
    print(f"   - 行业动态: {len(data.get('industry', []))} 条")
    print(f"   - 学术前沿: {len(data.get('academic', []))} 条")
    print(f"   - 应用实践: {len(data.get('applications', []))} 条")
    print(f"   - 创业生态: {len(data.get('startups', []))} 条")
    print()

    if total_items == 0:
        print("⚠️  没有获取到任何内容，可能是数据源配置有误或时间范围内无更新")
        sys.exit(0)

    # 生成每篇文章的摘要
    print("📝 正在为每篇文章生成核心观点摘要...")
    article_summarizer = ArticleSummarizer(config)

    for category in ['industry', 'academic', 'applications', 'startups']:
        if data.get(category):
            print(f"\n{category} 类别:")
            data[category] = article_summarizer.summarize_batch(data[category])

    print()

    # 生成类别摘要
    print("🤖 正在使用 LLM 生成类别摘要...")
    summaries = {}

    for category in ['industry', 'academic', 'applications', 'startups']:
        if data.get(category):
            print(f"   正在分析 {category}...")
            summaries[category] = analyzer.summarize_category(data[category], category)

    print("✓ 摘要生成完成\n")

    # 生成洞察
    insights = ""
    if config.get('report', {}).get('generate_insights', True):
        print("💡 正在生成洞察分析...")
        insights = analyzer.generate_insights(data)
        print("✓ 洞察生成完成\n")

    # 生成报告
    print("📝 正在生成报告...")
    report_path = generator.generate_report(data, summaries, insights)
    print(f"✓ 报告已生成: {report_path}\n")

    print("=" * 60)
    print("✅ 任务完成!")
    print(f"📄 报告文件: {report_path}")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  程序已中止")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

"""
HTML 报告生成模块 - 生成美观的 HTML 格式周报
"""
from datetime import datetime
from typing import Dict, List
import os


class HTMLReportGenerator:
    """生成 HTML 格式的周报，使用表格布局"""

    def __init__(self, config: dict):
        self.config = config
        self.output_dir = config.get('report', {}).get('output_dir', 'reports')

    def generate_report(self, data: Dict[str, List[Dict]], summaries: Dict[str, str], insights: str = "") -> str:
        """
        生成完整的 HTML 报告

        Args:
            data: 原始数据
            summaries: 各类别的摘要
            insights: 洞察分析

        Returns:
            报告文件路径
        """
        # 生成报告内容
        report_content = self._build_html_report(data, summaries, insights)

        # 保存报告
        filepath = self._save_report(report_content)

        return filepath

    def _build_html_report(self, data: Dict[str, List[Dict]], summaries: Dict[str, str], insights: str) -> str:
        """构建 HTML 报告内容"""
        week_num = datetime.now().isocalendar()[1]
        year = datetime.now().year
        date_str = datetime.now().strftime('%Y年%m月%d日')

        # 统计信息
        total_items = sum(len(items) for items in data.values())
        industry_count = len(data.get('industry', []))
        academic_count = len(data.get('academic', []))
        applications_count = len(data.get('applications', []))
        startups_count = len(data.get('startups', []))

        # 构建 HTML
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LLMPulse 周报 | 第 {week_num} 周</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}

        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}

        header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}

        header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}

        .summary {{
            background: #f8f9fa;
            padding: 30px;
            border-bottom: 4px solid #667eea;
        }}

        .summary h2 {{
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.8em;
        }}

        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}

        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.2s;
        }}

        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}

        .stat-card .icon {{
            font-size: 2em;
            margin-bottom: 10px;
        }}

        .stat-card .number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
        }}

        .stat-card .label {{
            color: #666;
            font-size: 0.9em;
        }}

        .section {{
            padding: 40px;
        }}

        .section h2 {{
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
            font-size: 1.8em;
        }}

        .section h2::before {{
            content: attr(data-icon);
            margin-right: 10px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-radius: 8px;
            overflow: hidden;
        }}

        thead {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}

        th {{
            padding: 15px;
            text-align: left;
            font-weight: 600;
            font-size: 0.95em;
        }}

        td {{
            padding: 15px;
            border-bottom: 1px solid #eee;
        }}

        tr:hover {{
            background: #f8f9fa;
        }}

        tr:last-child td {{
            border-bottom: none;
        }}

        .title-cell {{
            font-weight: 500;
            color: #333;
        }}

        .title-cell a {{
            color: #667eea;
            text-decoration: none;
            transition: color 0.2s;
        }}

        .title-cell a:hover {{
            color: #764ba2;
            text-decoration: underline;
        }}

        .source-cell {{
            color: #666;
            font-size: 0.9em;
        }}

        .date-cell {{
            color: #999;
            font-size: 0.85em;
            white-space: nowrap;
        }}

        .summary-cell {{
            color: #555;
            font-size: 0.9em;
            line-height: 1.5;
            max-width: 400px;
        }}

        .summary-text {{
            background: #f8f9fa;
            padding: 20px;
            border-left: 4px solid #667eea;
            margin: 20px 0;
            border-radius: 4px;
            line-height: 1.8;
        }}

        .insights {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 40px;
        }}

        .insights h2 {{
            color: white;
            border-bottom-color: white;
        }}

        .insights-content {{
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
            backdrop-filter: blur(10px);
        }}

        .insights-content h3 {{
            margin-top: 20px;
            margin-bottom: 10px;
        }}

        .insights-content p {{
            line-height: 1.8;
            margin-bottom: 15px;
        }}

        footer {{
            background: #2d3748;
            color: white;
            padding: 30px;
            text-align: center;
        }}

        footer p {{
            margin: 5px 0;
            opacity: 0.8;
        }}

        .no-data {{
            text-align: center;
            padding: 40px;
            color: #999;
            font-style: italic;
        }}

        @media (max-width: 768px) {{
            .container {{
                border-radius: 0;
            }}

            header h1 {{
                font-size: 1.8em;
            }}

            .section {{
                padding: 20px;
            }}

            table {{
                font-size: 0.9em;
            }}

            th, td {{
                padding: 10px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🚀 LLMPulse 周报</h1>
            <p>第 {week_num} 周 | {date_str}</p>
        </header>

        <div class="summary">
            <h2>📊 执行摘要</h2>
            <div class="stats">
                <div class="stat-card">
                    <div class="icon">📈</div>
                    <div class="number">{total_items}</div>
                    <div class="label">本周总动态</div>
                </div>
                <div class="stat-card">
                    <div class="icon">🏢</div>
                    <div class="number">{industry_count}</div>
                    <div class="label">行业动态</div>
                </div>
                <div class="stat-card">
                    <div class="icon">📚</div>
                    <div class="number">{academic_count}</div>
                    <div class="label">学术前沿</div>
                </div>
                <div class="stat-card">
                    <div class="icon">🚀</div>
                    <div class="number">{applications_count}</div>
                    <div class="label">应用实践</div>
                </div>
                <div class="stat-card">
                    <div class="icon">💼</div>
                    <div class="number">{startups_count}</div>
                    <div class="label">创业生态</div>
                </div>
            </div>
        </div>

        {self._build_category_section('industry', '🏢 行业动态', data.get('industry', []), summaries.get('industry', ''))}

        {self._build_category_section('academic', '📚 学术前沿', data.get('academic', []), summaries.get('academic', ''))}

        {self._build_category_section('applications', '🚀 应用实践', data.get('applications', []), summaries.get('applications', ''))}

        {self._build_category_section('startups', '💼 创业生态', data.get('startups', []), summaries.get('startups', ''))}

        {self._build_insights_section(insights)}

        <footer>
            <p><strong>由 LLMPulse 自动生成</strong></p>
            <p>追踪 AI 大语言模型领域的最新进展</p>
        </footer>
    </div>
</body>
</html>"""
        return html

    def _build_category_section(self, category: str, title: str, items: List[Dict], summary: str) -> str:
        """构建分类章节"""
        if not items:
            return f"""
        <div class="section">
            <h2 data-icon="">{title}</h2>
            <div class="no-data">本周暂无内容更新</div>
        </div>"""

        # 构建表格
        table_rows = ""
        for item in items:
            date_str = item['published'].strftime('%m月%d日')
            # 获取 AI 生成的摘要
            ai_summary = item.get('ai_summary', '暂无摘要')

            table_rows += f"""
                <tr>
                    <td class="title-cell">
                        <a href="{item['link']}" target="_blank">{item['title']}</a>
                    </td>
                    <td class="summary-cell">{ai_summary}</td>
                    <td class="source-cell">{item['source']}</td>
                    <td class="date-cell">{date_str}</td>
                </tr>"""

        summary_html = ""
        if summary and summary != "暂无内容":
            # 将 markdown 格式的摘要转换为 HTML
            summary_html = f'<div class="summary-text">{self._markdown_to_html(summary)}</div>'

        return f"""
        <div class="section">
            <h2 data-icon="">{title}</h2>
            {summary_html}
            <table>
                <thead>
                    <tr>
                        <th style="width: 30%;">标题</th>
                        <th style="width: 35%;">核心观点</th>
                        <th style="width: 20%;">来源</th>
                        <th style="width: 15%;">发布时间</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </div>"""

    def _build_insights_section(self, insights: str) -> str:
        """构建洞察章节"""
        if not insights:
            return ""

        insights_html = self._markdown_to_html(insights)

        return f"""
        <div class="insights">
            <h2 data-icon="">💡 洞察与思考</h2>
            <div class="insights-content">
                {insights_html}
            </div>
        </div>"""

    def _markdown_to_html(self, markdown_text: str) -> str:
        """简单的 Markdown 转 HTML（处理常见格式）"""
        html = markdown_text

        # 处理标题
        html = html.replace('### ', '<h3>').replace('\n\n', '</h3>\n\n')

        # 处理粗体
        import re
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)

        # 处理链接
        html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2" target="_blank">\1</a>', html)

        # 处理换行
        html = html.replace('\n\n', '<br><br>')
        html = html.replace('\n', '<br>')

        return html

    def _save_report(self, content: str) -> str:
        """保存报告到文件"""
        os.makedirs(self.output_dir, exist_ok=True)

        filename = f"week_{datetime.now().isocalendar()[1]}_{datetime.now().strftime('%Y%m%d')}.html"
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return filepath

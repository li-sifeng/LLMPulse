"""
报告生成模块 - 生成格式化的周报
"""
from datetime import datetime
from typing import Dict, List
import os


class ReportGenerator:
    """生成 Markdown 格式的周报"""

    def __init__(self, config: dict):
        self.config = config
        self.output_dir = config.get('report', {}).get('output_dir', 'reports')

    def generate_report(self, data: Dict[str, List[Dict]], summaries: Dict[str, str], insights: str = "") -> str:
        """
        生成完整报告

        Args:
            data: 原始数据
            summaries: 各类别的摘要
            insights: 洞察分析

        Returns:
            报告文件路径
        """
        # 生成报告内容
        report_content = self._build_report_content(data, summaries, insights)

        # 保存报告
        filepath = self._save_report(report_content)

        return filepath

    def _build_report_content(self, data: Dict[str, List[Dict]], summaries: Dict[str, str], insights: str) -> str:
        """构建报告内容"""
        # 获取时间范围
        week_num = datetime.now().isocalendar()[1]
        year = datetime.now().year
        date_str = datetime.now().strftime('%Y-%m-%d')

        # 构建报告
        report = f"""# LLMPulse 周报 | 第 {week_num} 周
> 生成时间: {date_str}

---

## 📊 执行摘要

本周共追踪到 **{sum(len(items) for items in data.values())}** 条重要动态：

- 🏢 行业动态: {len(data.get('industry', []))} 条
- 📚 学术前沿: {len(data.get('academic', []))} 条
- 🚀 应用实践: {len(data.get('applications', []))} 条
- 💼 创业生态: {len(data.get('startups', []))} 条

---

## 🏢 行业动态

{summaries.get('industry', '暂无内容')}

<details>
<summary>查看完整列表</summary>

{self._format_item_list(data.get('industry', []))}

</details>

---

## 📚 学术前沿

{summaries.get('academic', '暂无内容')}

<details>
<summary>查看完整列表</summary>

{self._format_item_list(data.get('academic', []))}

</details>

---

## 🚀 应用实践

{summaries.get('applications', '暂无内容')}

<details>
<summary>查看完整列表</summary>

{self._format_item_list(data.get('applications', []))}

</details>

---

## 💼 创业生态

{summaries.get('startups', '暂无内容')}

<details>
<summary>查看完整列表</summary>

{self._format_item_list(data.get('startups', []))}

</details>

---

## 💡 洞察与思考

{insights if insights else '本周暂无特别洞察。'}

---

*由 LLMPulse 自动生成 | [GitHub](https://github.com/li-sifeng/LLMPulse)*
"""
        return report

    def _format_item_list(self, items: List[Dict]) -> str:
        """格式化内容列表"""
        if not items:
            return "暂无内容"

        formatted = []
        for item in items:
            date_str = item['published'].strftime('%m-%d')
            formatted.append(
                f"- **[{item['title']}]({item['link']})**\n"
                f"  - 来源: {item['source']} | 日期: {date_str}\n"
            )

        return "\n".join(formatted)

    def _save_report(self, content: str) -> str:
        """
        保存报告到文件

        Args:
            content: 报告内容

        Returns:
            文件路径
        """
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)

        # 生成文件名
        filename = f"week_{datetime.now().isocalendar()[1]}_{datetime.now().strftime('%Y%m%d')}.md"
        filepath = os.path.join(self.output_dir, filename)

        # 写入文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return filepath

"""
LLM 分析模块 - 使用 LLM 对内容进行总结和分析
"""
from typing import List, Dict
import os
from anthropic import Anthropic


class LLMAnalyzer:
    """使用 LLM 进行内容分析和总结"""

    def __init__(self, config: dict):
        self.config = config
        llm_config = config.get('llm', {})

        self.provider = llm_config.get('provider', 'anthropic')
        self.api_key = llm_config.get('api_key', os.getenv('ANTHROPIC_API_KEY'))
        self.model = llm_config.get('model', 'claude-3-5-sonnet-20241022')
        self.max_tokens = llm_config.get('max_tokens', 4096)

        if self.provider == 'anthropic':
            self.client = Anthropic(api_key=self.api_key)

    def summarize_category(self, items: List[Dict], category: str) -> str:
        """
        为某个类别的内容生成摘要

        Args:
            items: 内容列表
            category: 类别名称

        Returns:
            摘要文本
        """
        if not items:
            return f"本周 {category} 类别暂无更新。"

        # 构建提示词
        content_text = self._format_items_for_prompt(items)
        prompt = self._build_summary_prompt(content_text, category)

        # 调用 LLM
        summary = self._call_llm(prompt)
        return summary

    def generate_insights(self, all_data: Dict[str, List[Dict]]) -> str:
        """
        基于所有数据生成洞察和思考

        Args:
            all_data: 所有类别的数据

        Returns:
            洞察分析文本
        """
        # 统计信息
        total_items = sum(len(items) for items in all_data.values())
        if total_items == 0:
            return "本周暂无重要内容更新。"

        # 构建综合分析提示词
        content_summary = ""
        for category, items in all_data.items():
            if items:
                content_summary += f"\n## {category} ({len(items)} 项)\n"
                for item in items[:5]:  # 每个类别取前5项
                    content_summary += f"- {item['title']}\n"

        prompt = f"""基于本周 AI/LLM 领域的以下动态，请生成 3 个精简洞察：

{content_summary}

要求：
1. **只输出 3 个核心洞察**（严格限制数量）
2. 每个洞察 1-2 句话，不超过 50 字
3. 聚焦：技术趋势、行业影响、创新亮点
4. 语言精炼，直击要害

输出格式：
1. **洞察标题**：核心观点（1-2句话）
2. **洞察标题**：核心观点（1-2句话）
3. **洞察标题**：核心观点（1-2句话）"""

        insights = self._call_llm(prompt)
        return insights

    def _format_items_for_prompt(self, items: List[Dict]) -> str:
        """格式化内容用于提示词"""
        formatted = []
        for idx, item in enumerate(items[:15], 1):  # 最多取15条
            formatted.append(
                f"{idx}. 标题: {item['title']}\n"
                f"   来源: {item['source']}\n"
                f"   摘要: {item.get('summary', '')[:200]}...\n"
                f"   链接: {item['link']}\n"
            )
        return "\n".join(formatted)

    def _build_summary_prompt(self, content: str, category: str) -> str:
        """构建摘要提示词"""
        category_names = {
            'industry': '行业动态',
            'academic': '学术前沿',
            'applications': '应用实践',
            'startups': '创业生态'
        }

        category_cn = category_names.get(category, category)

        # 为创业生态类别定制提示词 - 聚焦生产力工具和 AIOps
        if category == 'startups':
            return f"""你是一位专业的 AI/LLM 生产力工具和 AIOps 领域分析师。请基于以下信息，生成本周{category_cn}的精简摘要。

内容列表：
{content}

**聚焦领域**：
- LLM 生产力工具（代码助手、写作工具、知识管理、自动化工具等）
- AIOps 工具（智能运维、监控、日志分析、故障预测等）
- DevOps + AI（CI/CD、测试自动化、部署优化等）
- 开发者工具（IDE 插件、API 工具、调试助手等）

要求：
1. **优先筛选**：只选择生产力工具和 AIOps 相关的项目（过滤掉无关内容）
2. **提取 3-5 个核心要点**（严格限制数量）
3. 关注：新产品发布、功能更新、融资动态、技术创新
4. 每个要点：工具名 + 核心功能/更新（20-30字）
5. 语言精炼专业，突出实用价值

输出格式（简洁版）：
- **工具/产品名**：核心功能或更新信息。[链接](url)
- **工具/产品名**：核心功能或更新信息。[链接](url)

注意：
- 严格控制在 3-5 个要点
- 每个要点不超过 30 字
- 如果没有相关内容，返回"本周暂无生产力工具和 AIOps 相关更新"
"""

        return f"""你是一位专业的 AI/LLM 领域分析师。请基于以下内容，生成本周{category_cn}的精简摘要。

内容列表：
{content}

要求：
1. **只提取 3-5 个最重要的核心要点**（严格限制数量）
2. 每个要点：一句话概括（20-30字），不要过多细节
3. 使用简洁的 bullet point 格式
4. 语言精炼专业，直击重点
5. 突出最具影响力的技术创新

输出格式（简洁版）：
- **要点标题**：一句话核心内容。[链接](url)
- **要点标题**：一句话核心内容。[链接](url)

注意：严格控制在 3-5 个要点，每个要点不超过 30 字。
"""

    def _call_llm(self, prompt: str) -> str:
        """
        调用 LLM API

        Args:
            prompt: 提示词

        Returns:
            LLM 响应文本
        """
        try:
            if self.provider == 'anthropic':
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                return message.content[0].text
            else:
                return "暂不支持此 LLM 提供商"

        except Exception as e:
            print(f"LLM 调用失败: {str(e)}")
            return f"摘要生成失败: {str(e)}"

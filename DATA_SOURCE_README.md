# 数据源问题说明

## 问题分析

根据测试结果，以下是各数据源的状态：

### ✅ 正常工作的数据源

1. **OpenAI Blog** - 793 条内容 ✓
2. **DeepMind Blog** - 100 条内容 ✓
3. **Hugging Face Blog** - 713 条内容 ✓
4. **Hacker News AI** - 20 条内容 ✓

### ❌ 有问题的数据源

1. **arXiv 系列** (AI, CL, LG) - SSL 证书验证失败
   - 原因：可能是证书链问题或网络限制
   - 解决方案：已将 http 改为 https，但仍需要系统证书配置

2. **OpenAI Research** - RSS 源为空
   - 可能该 URL 不提供 RSS 订阅

## 为什么行业/学术动态没有数据？

**原因**：`days_back: 7` 的过滤设置

- OpenAI Blog、DeepMind 和 Hugging Face 虽然获取了大量历史数据
- 但这些数据大部分**不在最近7天内**发布
- 程序过滤掉了超过7天的内容
- 只有 Hacker News AI 有最近7天的内容，所以只显示在"应用实践"类别

## 解决方案

### 方案 1：调整时间范围（推荐）

编辑 `config/config.yaml`，将 `days_back` 改为更大的值：

```yaml
report:
  days_back: 30  # 改为30天或更长
```

### 方案 2：添加更多实时数据源

可以添加以下 RSS 源：

```yaml
industry:
  - name: "AI News - The Verge"
    url: "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml"
    category: "industry"

  - name: "TechCrunch AI"
    url: "https://techcrunch.com/category/artificial-intelligence/feed/"
    category: "industry"
```

### 方案 3：解决 arXiv SSL 问题

在 `src/data_fetcher.py` 中禁用 SSL 验证（仅用于测试）：

```python
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
```

## HTML 报告功能

已成功实现 HTML 表格展示：

- ✅ 美观的渐变色设计
- ✅ 卡片式统计摘要
- ✅ 表格形式展示内容列表
- ✅ 响应式布局（移动端友好）
- ✅ LLM 生成的摘要和洞察分析

报告文件：`reports/week_1_20251231.html`

直接在浏览器中打开即可查看！

# LLMPulse | 大模型脉搏

> 自动追踪 AI 大语言模型领域的最新进展、学术突破和应用实践

## 功能模块

### 1. 行业动态追踪
监测全球主流 LLM 公司（OpenAI、Anthropic、Google、Meta 等）的最新进展

### 2. 学术前沿分析
从 arXiv 等来源识别高影响力研究，提取核心观点

### 3. 应用生态扫描
追踪生产力工具、AIOps 领域的创业公司和大厂项目

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 配置 API keys（可选）
cp config/config.example.yaml config/config.yaml
# 编辑 config/config.yaml 填入你的 API keys

# 运行周报生成
python main.py

# 查看报告
# 报告将生成在 reports/ 目录下
```

## 配置说明

在 `config/config.yaml` 中配置：
- LLM API keys（用于内容分析和摘要）
- 数据源订阅列表
- 报告生成参数

## 输出示例

报告将以 Markdown 格式生成，包含：
- 📊 执行摘要
- 🏢 行业动态
- 📚 学术前沿
- 🚀 应用实践
- 💡 洞察与思考

## 技术栈

- Python 3.8+
- feedparser (RSS 订阅)
- requests (API 调用)
- PyYAML (配置管理)
- python-dotenv (环境变量)

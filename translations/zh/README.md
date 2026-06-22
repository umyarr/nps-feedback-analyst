🌐 [English](../../README.md) | [Русский](../ru/README.md)

# NPS Feedback Analyst

安全的本地优先客户满意度调查与 NPS 分析工具。

## 功能

1. **三种分析模式**：
   - **精简模式（算法分析）**：100% 离线 NLP — 词频、二元组、启发式投诉分类。免费，即时（0.05 秒）。
   - **本地 AI（Ollama）**：运行本地模型（`gemma2`、`llama3` 等）— 数据不离开设备。
   - **云端 AI（Gemini API）**：集成 Google Gemini，支持查询压缩与优化。

2. **提示注入防护**：通过 XML 标签实现数据与指令分离。本地扫描器拦截用户评论中的注入攻击。

3. **幻觉防护**：Python 本地精确计算 NPS 统计数据。AI 报告与真实指标交叉验证，并标注信任状态（`完全信任` / `有限信任`）。

4. **Token 效率**：智能去重节省高达 50% 的上下文。基于 MD5 的缓存 — 文件未变更时即时返回缓存报告。

## 快速开始

```bash
pip install -r requirements.txt

# 精简模式（离线，免费）
python analyze_feedback_secure.py --lite --file "path/to/survey.xlsx"

# Gemini API
python analyze_feedback_secure.py --file "path/to/survey.xlsx"

# 本地 Ollama
python analyze_feedback_secure.py --local --model gemma2 --file "path/to/survey.xlsx"
```

## Telegram 机器人

发送任意 `.xlsx` 文件给机器人，立即获得 NPS 指标和完整 Markdown 报告。

```bash
# .env
TELEGRAM_BOT_TOKEN=your_token

python nps_telegram_bot.py
```

## 技术栈

`Python` `Gemini API` `Ollama` `openpyxl` `aiogram` `systemd`

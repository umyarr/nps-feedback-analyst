🌐 [Русский](translations/ru/README.md) | [中文](translations/zh/README.md)

# NPS Feedback Analyst

A secure, local-first tool for analyzing customer satisfaction surveys and NPS scores.

## Features

1. **Three analysis modes**:
   - **Lite (Algorithmic)**: 100% offline NLP — word frequency, bigrams, heuristic complaint categorization. Free, instant (0.05s).
   - **Local AI (Ollama)**: Run local models (`gemma2`, `llama3`, etc.) — no data leaves your device.
   - **Cloud AI (Gemini API)**: Google Gemini integration with query compression and optimization.

2. **Prompt Injection Guard**: Data-Instruction Separation via XML tagging. Local scanner intercepts injection attempts in user comments.

3. **Hallucination Shield**: Python calculates exact NPS stats locally. AI report is verified against real metrics — trust status assigned (`FULL TRUST` / `LIMITED TRUST`).

4. **Token efficiency**: Smart deduplication saves up to 50% context. MD5-based cache — unchanged files return instant cached reports.

## Quick start

```bash
pip install -r requirements.txt

# Lite mode (offline, free)
python analyze_feedback_secure.py --lite --file "path/to/survey.xlsx"

# Gemini API
python analyze_feedback_secure.py --file "path/to/survey.xlsx"

# Local Ollama
python analyze_feedback_secure.py --local --model gemma2 --file "path/to/survey.xlsx"
```

## Telegram Bot

Send any `.xlsx` file to the bot — get NPS metrics and a full Markdown report back instantly.

```bash
# .env
TELEGRAM_BOT_TOKEN=your_token

python nps_telegram_bot.py
```

## Stack

`Python` `Gemini API` `Ollama` `openpyxl` `aiogram` `systemd`

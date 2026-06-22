🌐 [English](../../README.md) | [中文](../zh/README.md)

# NPS Feedback Analyst

Инструмент для безопасного локального анализа обратной связи и NPS-опросов.

## Возможности

1. **Три режима анализа**:
   - **Lite (Алгоритмический)**: 100% локальный NLP — частотность слов, биграммы, эвристика. Бесплатно, оффлайн, 0.05 сек.
   - **Локальный ИИ (Ollama)**: модели `gemma2`, `llama3` и др. — данные не покидают устройство.
   - **Облачный ИИ (Gemini API)**: интеграция с Google Gemini со сжатием запросов.

2. **Защита от Prompt Injection**: разделение данных и инструкций через XML-теги. Локальный сканер перехватывает попытки взлома в отзывах.

3. **Борьба с галлюцинациями**: Python считает точную статистику NPS локально. ИИ-отчёт сверяется с реальными метриками — выставляется статус доверия (`ПОЛНОЕ ДОВЕРИЕ` / `ОГРАНИЧЕННОЕ ДОВЕРИЕ`).

4. **Экономия токенов**: дедупликация одинаковых отзывов экономит до 50% контекста. MD5-кэш — если файл не менялся, отчёт мгновенно из кэша.

## Быстрый старт

```bash
pip install -r requirements.txt

# Lite-режим (оффлайн, бесплатно)
python analyze_feedback_secure.py --lite --file "путь/к/таблице.xlsx"

# Gemini API
python analyze_feedback_secure.py --file "путь/к/таблице.xlsx"

# Ollama
python analyze_feedback_secure.py --local --model gemma2 --file "путь/к/таблице.xlsx"
```

## Telegram-бот

Отправь боту `.xlsx` — получи метрики NPS и Markdown-отчёт прямо в чат.

```bash
# .env
TELEGRAM_BOT_TOKEN=твой_токен

python nps_telegram_bot.py
```

## Стек

`Python` `Gemini API` `Ollama` `openpyxl` `aiogram` `systemd`

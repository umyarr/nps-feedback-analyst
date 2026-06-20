import os
import sys
import subprocess
import shutil
import tempfile
from pathlib import Path

# Попробуем импортировать telebot, если его нет — выведем инструкцию по установке
try:
    import telebot
except ImportError:
    print("[ИНФО] Библиотека pyTelegramBotAPI не установлена.")
    print("Установка через pip...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyTelegramBotAPI"])
    import telebot

# Перенастройка кодировки на UTF-8 для корректного вывода в Windows
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Путь к основному скрипту анализатора
ANALYZER_SCRIPT = str(Path(__file__).parent / "analyze_feedback_secure.py")

# Попытка прочесть токен из .env файла
BOT_TOKEN = None
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith("TELEGRAM_BOT_TOKEN="):
                BOT_TOKEN = line.strip().split("=", 1)[1].strip().strip('"').strip("'")

if not BOT_TOKEN:
    BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

if not BOT_TOKEN:
    print("======================================================================")
    print("[ОШИБКА] Telegram Bot Token не найден!")
    print(f"Пожалуйста, создайте файл .env рядом с ботом со следующим содержимым:")
    print("TELEGRAM_BOT_TOKEN=ВАШ_ТОКЕН_БОТА")
    print("Или задайте переменную окружения TELEGRAM_BOT_TOKEN.")
    print("======================================================================")
    
    # Создаем шаблон .env файла для удобства пользователя
    try:
        with open(env_path, "w", encoding="utf-8") as f:
            f.write("TELEGRAM_BOT_TOKEN=ВСТАВЬТЕ_СЮДА_ТОКЕН_ОТ_BOTFATHER\n")
        print(f"[ИНФО] Создан шаблон файла конфигурации: {env_path.resolve()}")
    except Exception:
        pass
        
    input("\nНажмите Enter для выхода...")
    sys.exit(1)

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "👋Привет! Я Telegram-бот для экспресс-анализа NPS удовлетворенности клиентов (Режим Lite).\n\n"
        "📊 **Что я умею:**\n"
        "Вы отправляете мне Excel-файл (формата `.xlsx` с оценками и комментариями), "
        "а я провожу быстрый локальный контент-анализ и присылаю вам подробный Markdown-отчет с расчетом NPS, "
        "выделением проблем по категориям, популярными словами и ключевыми цитатами.\n\n"
        "🔒 **Безопасность:**\n"
        "Анализ проводится полностью локально на сервере, ваши данные защищены от утечек в облачные LLM, "
        "а временные файлы удаляются сразу после отправки отчета.\n\n"
        "📥 **Отправьте мне файл .xlsx для начала анализа!**"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(content_types=['document'])
def handle_document(message):
    document = message.document
    file_name = document.file_name
    
    if not file_name.lower().endswith('.xlsx'):
        bot.reply_to(message, "❌ Пожалуйста, отправьте файл в формате Excel (.xlsx)")
        return
        
    status_msg = bot.reply_to(message, "📥 Получаю файл и запускаю локальный анализ...")
    
    # Создаем временную директорию для безопасной работы
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        input_excel_path = temp_dir_path / file_name
        
        try:
            # Скачиваем файл из Telegram
            file_info = bot.get_file(document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            
            with open(input_excel_path, 'wb') as new_file:
                new_file.write(downloaded_file)
                
            # Путь, по которому скрипт сгенерирует отчет
            # Так как мы обновили analyze_feedback_secure.py, отчет создается рядом с входным файлом
            expected_report_name = f"{input_excel_path.stem}_Feedback_Analysis_Report.md"
            expected_report_path = temp_dir_path / expected_report_name
            
            bot.edit_message_text("⚙️ Запускаю локальный контент-анализ (без LLM)...", chat_id=message.chat.id, message_id=status_msg.message_id)
            
            # Запускаем скрипт анализа в режиме Lite
            result = subprocess.run([
                sys.executable, 
                ANALYZER_SCRIPT, 
                "--lite", 
                "--file", str(input_excel_path)
            ], capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode != 0:
                error_log = result.stderr if result.stderr else result.stdout
                print(f"[ОШИБКА] Анализатор завершился с кодом {result.returncode}. Лог:\n{error_log}")
                bot.edit_message_text(f"❌ Ошибка при анализе файла:\n<pre>{error_log[:300]}...</pre>", 
                                      chat_id=message.chat.id, message_id=status_msg.message_id, parse_mode="HTML")
                return
                
            # Проверяем, создался ли отчет
            if not expected_report_path.exists():
                bot.edit_message_text("❌ Ошибка: Отчет не был сгенерирован скриптом.", chat_id=message.chat.id, message_id=status_msg.message_id)
                return
                
            # Читаем отчет, чтобы вытащить краткую сводку для сообщения
            report_text = ""
            summary_lines = []
            with open(expected_report_path, "r", encoding="utf-8") as f:
                report_text = f.read()
                f.seek(0)
                # Берем первые ~10 значимых строк для быстрой сводки в чате
                for _ in range(12):
                    line = f.readline()
                    if not line:
                        break
                    summary_lines.append(line.strip())
            
            summary_message = "\n".join(summary_lines)
            
            # Отправляем сводку
            bot.edit_message_text(
                f"✅ **Анализ завершен!**\n\n{summary_message}\n\nПолный отчет прикреплен ниже 👇", 
                chat_id=message.chat.id, 
                message_id=status_msg.message_id,
                parse_mode="Markdown"
            )
            
            # Отправляем файл отчета
            with open(expected_report_path, 'rb') as doc:
                bot.send_document(message.chat.id, doc, visible_file_name=expected_report_name)
                
        except Exception as e:
            print(f"[Исключение] {e}")
            bot.send_message(message.chat.id, f"❌ Произошла критическая ошибка: {str(e)}")

if __name__ == "__main__":
    print("======================================================================")
    print("        NPS Feedback Analyst Telegram Bot - ЗАПУЩЕН")
    print("======================================================================")
    print("Бот готов к работе. Отправьте ему файл Excel (.xlsx) в Telegram.")
    print("Нажмите Ctrl+C для остановки бота.")
    print("======================================================================")
    try:
        bot.infinity_polling()
    except KeyboardInterrupt:
        print("\nБот остановлен пользователем.")
        sys.exit(0)

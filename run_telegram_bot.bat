@echo off
chcp 65001 > nul
title NPS Feedback Analyst Telegram Bot

echo ======================================================================
echo          NPS Feedback Analyst - Telegram Bot Runner
echo ======================================================================
echo.

:: Проверка наличия Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Python не найден в системе! 
    echo Установите Python и добавьте его в PATH.
    echo.
    pause
    exit /b
)

:: Запуск бота
python "%~dp0nps_telegram_bot.py"
echo.
pause

@echo off
chcp 65001 > nul
title NPS Feedback Analyst - Lite Mode

echo ======================================================================
echo          NPS Feedback Analyst - Режим Lite (Без ИИ и Интернета)
echo ======================================================================
echo.

:: Проверка наличия Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Python не найден в системе! 
    echo Пожалуйста, установите Python и убедитесь, что при установке выбрана галочка "Add Python to PATH".
    echo.
    pause
    exit /b
)

:: Проверка/установка библиотеки openpyxl
python -c "import openpyxl" >nul 2>&1
if errorlevel 1 (
    echo [ИНФО] Библиотека openpyxl не найдена. Устанавливаем...
    pip install openpyxl
    if errorlevel 1 (
        echo [ОШИБКА] Не удалось автоматически установить библиотеку openpyxl via pip.
        echo Попробуйте вручную выполнить команду: pip install openpyxl
        echo.
        pause
        exit /b
    )
)

:: Определение входного файла (поддерживает Drag-and-Drop)
set "INPUT_FILE=%~1"
if "%INPUT_FILE%"=="" (
    set "INPUT_FILE=C:\Users\user\Desktop\Npc.xlsx"
    echo [ИНФО] Файл не перетащен на скрипт. Используется файл по умолчанию:
    echo        C:\Users\user\Desktop\Npc.xlsx
) else (
    echo [ИНФО] Анализ перетащенного файла:
    echo        "%INPUT_FILE%"
)
echo.

:: Проверка существования файла
if not exist "%INPUT_FILE%" (
    echo [ОШИБКА] Файл не найден: "%INPUT_FILE%"
    echo Пожалуйста, убедитесь, что файл существует, или перетащите его прямо на значок этого батника.
    echo.
    pause
    exit /b
)

echo [ПРОЦЕСС] Запуск локального алгоритмического анализа (Lite)...
echo ----------------------------------------------------------------------
python "%~dp0analyze_feedback_secure.py" --lite --file "%INPUT_FILE%"
echo ----------------------------------------------------------------------
echo.

if %errorlevel% equ 0 (
    echo [УСПЕХ] Анализ успешно завершен!
    echo Отчет сохранен в ту же папку, где лежит исходный файл Excel.
) else (
    echo [ОШИБКА] В ходе выполнения скрипта произошла ошибка.
)
echo.
pause

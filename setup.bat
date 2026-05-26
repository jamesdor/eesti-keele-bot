@echo off
cd /d "%~dp0"
echo ========================================
echo  Eesti Keele Bot - Setup
echo ========================================
echo.
echo Установка бота в автозагрузку Windows...
echo.

:: Устанавливаем через PowerShell
powershell -ExecutionPolicy Bypass -File "%~dp0install_task.ps1"

if %ERRORLEVEL% equ 0 (
    echo.
    echo Готово! Бот будет запускаться автоматически при входе в систему.
    echo.
    echo Сейчас открой config.json и введи:
    echo   BOT_TOKEN - токен от @BotFather
    echo   CHANNEL_ID - @username канала
    echo   ADMIN_ID - твой Telegram ID
    echo.
    echo После этого запусти start_bot.bat чтобы проверить
) else (
    echo.
    echo Ошибка при создании задачи. Запусти setup.bat от имени администратора.
)

pause

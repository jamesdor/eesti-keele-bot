@echo off
cd /d "%~dp0"
echo ========================================
echo  Eesti Keele Bot - Setup
echo ========================================
echo.
echo Установка бота в автозагрузку Windows...
echo.

:: Создаём задачу в Task Scheduler
schtasks /create /tn "EestiKeeleBot" /tr "%~dp0start_bot.vbs" /sc onlogon /ru %USERNAME% /f

if %ERRORLEVEL% equ 0 (
    echo.
    echo Готово! Бот будет запускаться автоматически при входе в систему.
    echo.
    echo Чтобы запустить сейчас - запусти start_bot.bat
) else (
    echo.
    echo Ошибка при создании задачи. Запусти от имени администратора.
)

pause

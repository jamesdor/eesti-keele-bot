# Eesti Keele Kursus — Telegram Bot

Бот для продажи доступа к курсу эстонского языка через Telegram Stars.

## Быстрый старт

### 1. Создать бота в Telegram
1. Напиши [@BotFather](https://t.me/BotFather)
2. Отправь `/newbot`
3. Выбери имя (например `Eesti Keele Kursus Bot`)
4. Получи **токен** (вида `123456:ABC-DEF...`)

### 2. Создать канал
1. Создай канал в Telegram (например `@eesti_keele_kursus`)
2. Добавь бота как администратора канала
3. В настройках канала → Administrators → Add Admin → выбери бота
4. Дай права: "Invite users via link"

### 3. Узнать CHANNEL_ID и ADMIN_ID
1. Напиши боту [@userinfobot](https://t.me/userinfobot) — узнай свой ID
2. Чтобы узнать CHANNEL_ID, напиши в канале что-нибудь и перешли боту

### 4. Задеплоить на Render.com
1. Залей код на GitHub
2. На [Render.com](https://render.com) → New + → Blueprint
3. Подключи репозиторий
4. Render сам найдёт `render.yaml`
5. Введи переменные: `BOT_TOKEN`, `CHANNEL_ID`, `ADMIN_ID`

Или задеплой вручную:
```
pip install -r requirements.txt
BOT_TOKEN=xxx CHANNEL_ID=@xxx ADMIN_ID=123 python bot.py
```

## Переменные окружения

| Переменная | Описание |
|-----------|----------|
| `BOT_TOKEN` | Токен от @BotFather |
| `CHANNEL_ID` | @username канала |
| `PRICE_STARS` | Цена в Telegram Stars (по умолч. 100) |
| `ADMIN_ID` | Твой Telegram ID для уведомлений |

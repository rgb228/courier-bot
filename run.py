import asyncio
import logging
import os
from aiohttp import web
from aiogram import Bot, Dispatcher
from app.database import init_db
from app.handlers import user, admin

# Получаем токен из переменных окружения (Render передает их сюда)
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден! Добавь его в Environment Variables на Render.")

# --- Мини веб-сервер для Render ---
async def handle(request):
    return web.Response(text="Bot is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Веб-сервер запущен на порту {port}")

async def start_bot():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(admin.router)
    dp.include_router(user.router)
    print("Бот успешно запущен!")
    await dp.start_polling(bot)

async def main():
    logging.basicConfig(level=logging.INFO)
    await init_db()
    
    # Запускаем веб-сервер и бота как две параллельные задачи
    await asyncio.gather(
        start_web_server(),
        start_bot()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен.")
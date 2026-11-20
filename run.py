import asyncio
import logging
import os
from aiohttp import web
from aiogram import Bot, Dispatcher
from app.config import BOT_TOKEN
from app.database import init_db
from app.handlers import user, admin

# --- ини веб-сервер для Render ---
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
    print(f"еб-сервер запущен на порту {port}")

async def main():
    logging.basicConfig(level=logging.INFO)
    await init_db()
    
    asyncio.create_task(start_web_server())
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(admin.router)
    dp.include_router(user.router)
    
    print("от успешно запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("от остановлен.")
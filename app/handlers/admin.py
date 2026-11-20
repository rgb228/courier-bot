import asyncio
from aiogram import Router, F, types
from aiogram.filters import Command
from app.config import ADMIN_ID
from app.database import get_users, get_stats
from app.keyboards import admin_menu

router = Router()

@router.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    total, registered = await get_stats()
    await message.answer("🛠 Админ-панель\nВыбери действие:", reply_markup=admin_menu(total, registered))

@router.callback_query(F.data == "admin_all")
async def admin_all(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID: return
    users = await get_users()
    if not users:
        await callback.message.answer("Пока никого нет.")
        return
    text = "👥 Все пользователи:\n\n"
    for u in users[:30]:
        phone_str = f" | 📞 {u[3]}" if u[3] else ""
        text += f"ID: {u[0]} | @{u[1] or 'нет'} | {u[2]}{phone_str} | {u[4]}\n"
    if len(users) > 30:
        text += f"\n...и еще {len(users)-30} чел."
    await callback.message.answer(text)

@router.callback_query(F.data == "admin_reg")
async def admin_reg(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID: return
    users = await get_users(status="registered")
    if not users:
        await callback.message.answer("Пока никто не зарегистрировался.")
        return
    text = "✅ Зарегистрированные лиды:\n\n"
    for u in users:
        phone_str = f" | 📞 {u[3]}" if u[3] else ""
        text += f"ID: {u[0]} | @{u[1] or 'нет'} | {u[2]}{phone_str}\n"
    await callback.message.answer(text)

@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID: return
    await callback.message.answer("📢 Отправь команду:\n/send Твой текст")

@router.message(Command("send"))
async def send_broadcast(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    text_to_send = message.text.replace("/send ", "")
    users = await get_users()
    success, fail = 0, 0
    msg = await message.answer("⏳ Рассылка началась...")
    for u in users:
        try:
            await message.bot.send_message(u[0], text_to_send)
            success += 1
            await asyncio.sleep(0.05)
        except Exception:
            fail += 1
    await msg.edit_text(f"✅ Рассылка завершена!\nУспешно: {success}\nОшибок: {fail}")

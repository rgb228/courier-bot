# fix_all.py
import os

# 1. Обновляем admin.py (уведомления) - без изменений
admin_content = '''import asyncio
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
    await message.answer("🛠 Админ-панель\\nВыбери действие:", reply_markup=admin_menu(total, registered))

@router.callback_query(F.data == "admin_all")
async def admin_all(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID: return
    users = await get_users()
    if not users:
        await callback.message.answer("Пока никого нет.")
        return
    text = "👥 Все пользователи:\\n\\n"
    for u in users[:30]:
        phone_str = f" | 📞 {u[3]}" if u[3] else ""
        text += f"ID: {u[0]} | @{u[1] or 'нет'} | {u[2]}{phone_str} | {u[4]}\\n"
    if len(users) > 30:
        text += f"\\n...и еще {len(users)-30} чел."
    await callback.message.answer(text)

@router.callback_query(F.data == "admin_reg")
async def admin_reg(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID: return
    users = await get_users(status="registered")
    if not users:
        await callback.message.answer("Пока никто не зарегистрировался.")
        return
    text = "✅ Зарегистрированные лиды:\\n\\n"
    for u in users:
        phone_str = f" | 📞 {u[3]}" if u[3] else ""
        text += f"ID: {u[0]} | @{u[1] or 'нет'} | {u[2]}{phone_str}\\n"
    await callback.message.answer(text)

@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID: return
    await callback.message.answer("📢 Отправь команду:\\n/send Твой текст")

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
    await msg.edit_text(f"✅ Рассылка завершена!\\nУспешно: {success}\\nОшибок: {fail}")
'''

# 2. Обновляем user.py (Безопасное редактирование)
user_content = '''import asyncio
from aiogram import Router, F, types, Bot
from aiogram.filters import CommandStart
from app.database import save_user, update_status, save_phone
from app.keyboards import main_menu, back_menu, reg_menu, phone_menu
from app import texts
from app.config import PARTNER_LINK, ADMIN_ID

router = Router()
pending_users = {}

WELCOME_IMAGE_URL = "https://i.imgur.com/S5T5Etl.jpeg"

async def remind_user(user_id: int, message_id: int, bot: Bot):
    await asyncio.sleep(7200)
    if user_id in pending_users and not pending_users[user_id]:
        try:
            await bot.send_message(user_id, "Привет! 👋 Заметил, что ты получил ссылку, но еще не зарегистрировался.\\n\\nВозникли вопросы? Напиши мне @DedTamaz — помогу!\\n\\nИли нажми кнопку ниже:", reply_markup=reg_menu())
        except Exception:
            pass
        del pending_users[user_id]

# Безопасная функция замены сообщения
async def safe_edit(callback: types.CallbackQuery, text: str, markup):
    try:
        await callback.message.edit_text(text, reply_markup=markup)
    except Exception:
        # Если сообщение нельзя отредактировать (оно с фото), удаляем его и отправляем новое
        try:
            await callback.message.delete()
        except Exception:
            pass
        await callback.message.answer(text, reply_markup=markup)

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    await save_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    try:
        await message.answer_photo(
            photo=WELCOME_IMAGE_URL,
            caption=texts.WELCOME_TEXT.format(name=message.from_user.first_name),
            reply_markup=main_menu()
        )
    except Exception:
        await message.answer(
            texts.WELCOME_TEXT.format(name=message.from_user.first_name),
            reply_markup=main_menu()
        )

@router.callback_query(F.data == "start_earning")
async def start_earning(callback: types.CallbackQuery):
    text = texts.START_EARNING_TEXT.format(link=PARTNER_LINK)
    pending_users[callback.from_user.id] = False
    asyncio.create_task(remind_user(callback.from_user.id, callback.message.message_id, callback.bot))
    await safe_edit(callback, text, reg_menu())
    await callback.answer()

@router.callback_query(F.data == "registered")
async def registered(callback: types.CallbackQuery):
    if callback.from_user.id in pending_users:
        pending_users[callback.from_user.id] = True
    await update_status(callback.from_user.id, "registered")
    
    username = f"@{callback.from_user.username}" if callback.from_user.username else "Нет ника"
    admin_text = f"🔥 НОВЫЙ ЛИД!\\n\\nИмя: {callback.from_user.first_name}\\nНик: {username}\\nID: {callback.from_user.id}"
    try:
        await callback.bot.send_message(ADMIN_ID, admin_text)
    except Exception:
        pass
        
    await safe_edit(callback, texts.REGISTERED_TEXT, back_menu())
    await callback.message.answer("📱 Оставь свой номер телефона, чтобы я мог связаться с тобой (или нажми «Пропустить»):", reply_markup=phone_menu())
    await callback.answer()

@router.message(F.contact)
async def handle_contact(message: types.Message):
    phone = message.contact.phone_number
    await save_phone(message.from_user.id, phone)
    try:
        await message.bot.send_message(ADMIN_ID, f"📞 Лид {message.from_user.first_name} (@{message.from_user.username}) оставил номер: {phone}")
    except Exception:
        pass
    await message.answer("✅ Отлично! Номер сохранен.\\n\\nВозвращайся в меню:", reply_markup=main_menu())

@router.message(F.text == "Пропустить")
async def skip_phone(message: types.Message):
    await message.answer("Хорошо! Если передумаешь, пиши @DedTamaz.\\n\\nВозвращайся в меню:", reply_markup=main_menu())

@router.callback_query(F.data == "conditions")
async def show_conditions(callback: types.CallbackQuery):
    await safe_edit(callback, texts.CONDITIONS_TEXT, back_menu())
    await callback.answer()

@router.callback_query(F.data == "pay_card")
async def show_pay_card(callback: types.CallbackQuery):
    await safe_edit(callback, texts.PAY_CARD_TEXT, back_menu())
    await callback.answer()

@router.callback_query(F.data == "how_to_start")
async def show_how_to_start(callback: types.CallbackQuery):
    await safe_edit(callback, texts.HOW_TO_START_TEXT, back_menu())
    await callback.answer()

@router.callback_query(F.data == "bonuses")
async def show_bonuses(callback: types.CallbackQuery):
    await safe_edit(callback, texts.BONUSES_TEXT, back_menu())
    await callback.answer()

@router.callback_query(F.data == "faq")
async def show_faq(callback: types.CallbackQuery):
    await safe_edit(callback, texts.FAQ_TEXT, back_menu())
    await callback.answer()

@router.callback_query(F.data == "contact")
async def show_contact(callback: types.CallbackQuery):
    await safe_edit(callback, texts.CONTACT_TEXT, back_menu())
    await callback.answer()

@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery):
    await safe_edit(callback, texts.WELCOME_TEXT.format(name=callback.from_user.first_name), main_menu())
    await callback.answer()
'''

with open("app/handlers/admin.py", "w", encoding="utf-8") as f:
    f.write(admin_content)

with open("app/handlers/user.py", "w", encoding="utf-8") as f:
    f.write(user_content)

print("Файлы обновлены! Ошибка 'there is no text' исправлена.")
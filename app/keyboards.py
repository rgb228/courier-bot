from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

def main_menu():
    kb = [
        [InlineKeyboardButton(text="🚀 Начать зарабатывать", callback_data="start_earning")],
        [InlineKeyboardButton(text="💳 Карта Пэй (моментальные выплаты)", callback_data="pay_card")],
        [InlineKeyboardButton(text="👣 Как начать (Пошагово)", callback_data="how_to_start")],
        [InlineKeyboardButton(text="📋 Условия работы", callback_data="conditions")],
        [InlineKeyboardButton(text="🎁 Бонусы и плюшки", callback_data="bonuses")],
        [InlineKeyboardButton(text="❓ Частые вопросы (FAQ)", callback_data="faq")],
        [InlineKeyboardButton(text="📞 Связаться с нами", callback_data="contact")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def back_menu():
    kb = [[InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back_to_main")]]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def reg_menu():
    kb = [
        [InlineKeyboardButton(text="✅ Я зарегистрировался", callback_data="registered")],
        [InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def phone_menu():
    kb = [
        [KeyboardButton(text="📱 Отправить мой номер", request_contact=True)],
        [KeyboardButton(text="Пропустить")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)

def admin_menu(total, registered):
    kb = [
        [InlineKeyboardButton(text=f"👥 Все пользователи ({total})", callback_data="admin_all")],
        [InlineKeyboardButton(text=f"✅ Зарегистрировались ({registered})", callback_data="admin_reg")],
        [InlineKeyboardButton(text="📢 Сделать рассылку", callback_data="admin_broadcast")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

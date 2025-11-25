from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from keyboards.inline import get_main_menu_keyboard

router = Router()


@router.callback_query(F.data == "main_menu")
async def show_main_menu(callback: CallbackQuery):
    """Показать главное меню"""
    text = (
        "🏠 <b>Главное меню</b>\n\n"
        "Выберите действие:"
    )
    await callback.message.edit_text(text, reply_markup=get_main_menu_keyboard())
    await callback.answer()


@router.callback_query(F.data == "about")
async def show_about(callback: CallbackQuery):
    """Раздел 'Обо мне'"""
    text = (
        "👤 <b>Обо мне</b>\n\n"
        "🔑 Только реальные объекты\n"
"🏡 Квартиры с ремонтом, мебелью и локацией\n"
"🔥 Без фейка — только то, что продаётся\n"
"📲 Пишите: @RieltVlad"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")
    ]])
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "channel")
async def show_channel(callback: CallbackQuery):
    """Раздел 'Канал с вариантами квартир'"""
    text = (
        "📢 <b>Канал с вариантами квартир</b>\n\n"
        "Подпишитесь на наш канал, чтобы видеть все доступные варианты квартир!"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="📢 Перейти в канал", url="https://t.me/Kvartira_doma_Tashkent")
    ], [
        InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")
    ]])
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "contact")
async def show_contact(callback: CallbackQuery):
    """Раздел 'Связаться со мной'"""
    text = (
        "💬 <b>Связаться со мной</b>\n\n"
        "Свяжитесь с нашим консультантом для получения дополнительной информации."
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="💬 Написать консультанту", url="https://t.me/RieltVlad")
    ], [
        InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")
    ]])
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()




from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.inline import get_main_menu_keyboard
from services.api import get_apartment_by_id
from utils.formatters import format_apartment_card, get_apartment_media_group

router = Router()


class SearchByIdStates(StatesGroup):
    waiting_for_id = State()


@router.callback_query(F.data == "search_by_id")
async def start_search_by_id(callback: CallbackQuery, state: FSMContext):
    """Начать поиск по ID"""
    await state.set_state(SearchByIdStates.waiting_for_id)
    text = (
        "🔍 <b>Поиск по ID</b>\n\n"
        "Введите ID квартиры:"
    )
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="◀️ Отмена", callback_data="main_menu")
    ]])
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.message(SearchByIdStates.waiting_for_id)
async def process_id(message: Message, state: FSMContext):
    """Обработка введенного ID"""
    try:
        apartment_id = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Пожалуйста, введите корректный ID (число).")
        return
    
    # Запрос к API
    apartment = await get_apartment_by_id(apartment_id)
    
    if not apartment:
        await message.answer(
            f"😔 Квартира с ID {apartment_id} не найдена.\n\n"
            "Попробуйте ввести другой ID.",
            reply_markup=get_main_menu_keyboard()
        )
        await state.clear()
        return
    
    # Форматируем карточку
    card_text = format_apartment_card(apartment)
    
    # Получаем медиа-группу
    media_group = get_apartment_media_group(apartment)

    if media_group and len(media_group) >= 2:
        # Если есть 2+ изображения, отправляем медиа-группу
        try:
            media_group[0].caption = card_text
            await message.bot.send_media_group(
                chat_id=message.chat.id,
                media=media_group
            )
            await message.answer("✅ Квартира найдена!", reply_markup=get_main_menu_keyboard())
        except Exception as e:
            print(f"Ошибка при отправке медиа-группы: {e}")
            await message.answer(card_text, reply_markup=get_main_menu_keyboard())
    elif media_group and len(media_group) == 1:
        # Если только 1 фото, отправляем отдельным сообщением
        try:
            await message.bot.send_photo(
                chat_id=message.chat.id,
                photo=media_group[0].media,
                caption=card_text,
                parse_mode="HTML"
            )
            await message.answer("✅ Квартира найдена!", reply_markup=get_main_menu_keyboard())
        except Exception as e:
            print(f"Ошибка при отправке фото: {e}")
            await message.answer(card_text, reply_markup=get_main_menu_keyboard())
    else:
        # Если нет изображений, отправляем только текст
        await message.answer(card_text, reply_markup=get_main_menu_keyboard())
    
    await state.clear()


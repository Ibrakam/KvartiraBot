from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from keyboards.inline import get_main_menu_keyboard
from services.database import add_subscription, remove_subscription, get_subscription, init_db

router = Router()

# Инициализация БД при импорте
init_db()


@router.callback_query(F.data == "subscribe")
async def subscribe(callback: CallbackQuery, state: FSMContext):
    """Подписаться на рассылку"""
    user_id = callback.from_user.id
    
    # Получаем текущие фильтры из state (если есть)
    filters = await state.get_data()
    
    # Если фильтров нет, предлагаем начать поиск
    if not any(filters.values()):
        text = (
            "✉️ <b>Подписка на рассылку</b>\n\n"
            "Для подписки на рассылку сначала выполните поиск квартиры с нужными параметрами.\n"
            "После этого вы сможете подписаться на уведомления о новых квартирах, соответствующих вашим критериям."
        )
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="🏠 Выбрать квартиру", callback_data="search_apartment")
        ], [
            InlineKeyboardButton(text="◀️ Главное меню", callback_data="main_menu")
        ]])
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
        return
    
    # Сохраняем подписку
    add_subscription(user_id, filters)
    
    text = (
        "✅ <b>Вы успешно подписались на рассылку!</b>\n\n"
        "Вы будете получать уведомления о новых квартирах, соответствующих вашим критериям поиска."
    )
    await callback.message.edit_text(text, reply_markup=get_main_menu_keyboard())
    await callback.answer("Подписка активирована!")


@router.callback_query(F.data == "unsubscribe")
async def unsubscribe(callback: CallbackQuery):
    """Отписаться от рассылки"""
    user_id = callback.from_user.id
    
    # Проверяем, есть ли подписка
    subscription = get_subscription(user_id)
    
    if not subscription:
        text = "ℹ️ У вас нет активной подписки на рассылку."
    else:
        remove_subscription(user_id)
        text = "❌ <b>Вы отписались от рассылки</b>\n\nВы больше не будете получать уведомления о новых квартирах."
    
    await callback.message.edit_text(text, reply_markup=get_main_menu_keyboard())
    await callback.answer()


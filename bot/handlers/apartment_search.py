from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from states.apartment_search import ApartmentSearchStates
from keyboards.inline import (
    get_type_keyboard, get_district_keyboard, get_condition_keyboard,
    get_area_keyboard, get_rooms_keyboard, get_price_keyboard, get_pagination_keyboard
)
from services.api import get_apartments
from services.database import init_db
from utils.formatters import format_apartment_card, get_apartment_media_group

router = Router()

# Инициализация БД при импорте
init_db()


@router.callback_query(F.data == "search_apartment")
async def start_search(callback: CallbackQuery, state: FSMContext):
    """Начать процесс поиска квартиры"""
    await state.clear()
    await state.update_data(
        type=[],
        type_any=False,
        district=[],
        district_any=False,
        condition=[],
        condition_any=False,
        area_ranges=[],
        area_any=False,
        rooms=[],
        rooms_any=False,
        price_ranges=[],
        price_any=False,
    )
    await state.set_state(ApartmentSearchStates.choosing_type)
    text = "🏠 <b>Выбор квартиры</b>\n\nВыберите тип жилья (можно несколько):"
    await callback.message.edit_text(text, reply_markup=get_type_keyboard())
    await callback.answer()


@router.callback_query(F.data.startswith("type_toggle:"), ApartmentSearchStates.choosing_type)
async def toggle_type(callback: CallbackQuery, state: FSMContext):
    """Отмечаем тип жилья"""
    value = callback.data.split(":", 1)[1]
    data = await state.get_data()
    selected = list(data.get('type', []))
    any_selected = data.get('type_any', False)

    if value == "any":
        any_selected = not any_selected
        if any_selected:
            selected = []
    else:
        if value in selected:
            selected.remove(value)
        else:
            selected.append(value)
        any_selected = False

    await state.update_data(type=selected, type_any=any_selected)
    text = "🏠 <b>Выбор квартиры</b>\n\nВыберите тип жилья (можно несколько):"
    await callback.message.edit_text(text, reply_markup=get_type_keyboard(selected, any_selected))
    await callback.answer()


@router.callback_query(F.data == "type_next", ApartmentSearchStates.choosing_type)
async def proceed_to_district(callback: CallbackQuery, state: FSMContext):
    """Переход к выбору района"""
    data = await state.get_data()
    if not data.get('type') and not data.get('type_any'):
        await callback.answer("Выберите вариант или укажите 'Не важно'", show_alert=True)
        return

    await state.set_state(ApartmentSearchStates.choosing_district)
    text = "🏠 <b>Выбор квартиры</b>\n\nВыберите район (можно несколько):"
    districts = data.get('district', [])
    any_selected = data.get('district_any', False)
    await callback.message.edit_text(text, reply_markup=get_district_keyboard(districts, any_selected))
    await callback.answer()


@router.callback_query(F.data.startswith("district_toggle:"), ApartmentSearchStates.choosing_district)
async def toggle_district(callback: CallbackQuery, state: FSMContext):
    """Отмечаем районы"""
    value = callback.data.split(":", 1)[1]
    data = await state.get_data()
    selected = list(data.get('district', []))
    any_selected = data.get('district_any', False)

    if value == "any":
        any_selected = not any_selected
        if any_selected:
            selected = []
    else:
        if value in selected:
            selected.remove(value)
        else:
            selected.append(value)
        any_selected = False

    await state.update_data(district=selected, district_any=any_selected)
    text = "🏠 <b>Выбор квартиры</b>\n\nВыберите район (можно несколько):"
    await callback.message.edit_text(text, reply_markup=get_district_keyboard(selected, any_selected))
    await callback.answer()


@router.callback_query(F.data == "district_next", ApartmentSearchStates.choosing_district)
async def proceed_to_condition(callback: CallbackQuery, state: FSMContext):
    """Переход к выбору состояния"""
    data = await state.get_data()
    if not data.get('district') and not data.get('district_any'):
        await callback.answer("Выберите район или отметьте 'Не важно'", show_alert=True)
        return

    await state.set_state(ApartmentSearchStates.choosing_condition)
    text = "🏠 <b>Выбор квартиры</b>\n\nВыберите тип ремонта (можно несколько):"
    selected = data.get('condition', [])
    any_selected = data.get('condition_any', False)
    await callback.message.edit_text(text, reply_markup=get_condition_keyboard(selected, any_selected))
    await callback.answer()


@router.callback_query(F.data.startswith("condition_toggle:"), ApartmentSearchStates.choosing_condition)
async def toggle_condition(callback: CallbackQuery, state: FSMContext):
    """Отмечаем состояние"""
    value = callback.data.split(":", 1)[1]
    data = await state.get_data()
    selected = list(data.get('condition', []))
    any_selected = data.get('condition_any', False)

    if value == "any":
        any_selected = not any_selected
        if any_selected:
            selected = []
    else:
        if value in selected:
            selected.remove(value)
        else:
            selected.append(value)
        any_selected = False

    await state.update_data(condition=selected, condition_any=any_selected)
    text = "🏠 <b>Выбор квартиры</b>\n\nВыберите тип ремонта (можно несколько):"
    await callback.message.edit_text(text, reply_markup=get_condition_keyboard(selected, any_selected))
    await callback.answer()


@router.callback_query(F.data == "condition_next", ApartmentSearchStates.choosing_condition)
async def proceed_to_area(callback: CallbackQuery, state: FSMContext):
    """Переход к выбору площади"""
    data = await state.get_data()
    if not data.get('condition') and not data.get('condition_any'):
        await callback.answer("Выберите состояние или отметьте 'Не важно'", show_alert=True)
        return

    await state.set_state(ApartmentSearchStates.choosing_area)
    selected = data.get('area_ranges', [])
    any_selected = data.get('area_any', False)
    text = "🏠 <b>Выбор квартиры</b>\n\nВыберите площадь (можно несколько диапазонов):"
    await callback.message.edit_text(text, reply_markup=get_area_keyboard(selected, any_selected))
    await callback.answer()


@router.callback_query(F.data.startswith("area_toggle:"), ApartmentSearchStates.choosing_area)
async def toggle_area(callback: CallbackQuery, state: FSMContext):
    """Отмечаем диапазоны площади"""
    value = callback.data.split(":", 1)[1]
    data = await state.get_data()
    selected = list(data.get('area_ranges', []))
    any_selected = data.get('area_any', False)

    if value == "any":
        any_selected = not any_selected
        if any_selected:
            selected = []
    else:
        if value in selected:
            selected.remove(value)
        else:
            selected.append(value)
        any_selected = False

    await state.update_data(area_ranges=selected, area_any=any_selected)
    text = "🏠 <b>Выбор квартиры</b>\n\nВыберите площадь (можно несколько диапазонов):"
    await callback.message.edit_text(text, reply_markup=get_area_keyboard(selected, any_selected))
    await callback.answer()


@router.callback_query(F.data == "area_next", ApartmentSearchStates.choosing_area)
async def proceed_to_rooms(callback: CallbackQuery, state: FSMContext):
    """Переход к выбору комнат"""
    data = await state.get_data()
    if not data.get('area_ranges') and not data.get('area_any'):
        await callback.answer("Выберите диапазон площади или отметьте 'Не важно'", show_alert=True)
        return

    await state.set_state(ApartmentSearchStates.choosing_rooms)
    selected = data.get('rooms', [])
    any_selected = data.get('rooms_any', False)
    text = "🏠 <b>Выбор квартиры</b>\n\nВыберите количество комнат (можно несколько):"
    await callback.message.edit_text(text, reply_markup=get_rooms_keyboard(selected, any_selected))
    await callback.answer()


@router.callback_query(F.data.startswith("rooms_toggle:"), ApartmentSearchStates.choosing_rooms)
async def toggle_rooms(callback: CallbackQuery, state: FSMContext):
    """Отмечаем количество комнат"""
    value = callback.data.split(":", 1)[1]
    data = await state.get_data()
    selected = list(data.get('rooms', []))
    any_selected = data.get('rooms_any', False)

    if value == "any":
        any_selected = not any_selected
        if any_selected:
            selected = []
    else:
        rooms_value = int(value)
        if rooms_value in selected:
            selected.remove(rooms_value)
        else:
            selected.append(rooms_value)
        any_selected = False

    await state.update_data(rooms=selected, rooms_any=any_selected)
    text = "🏠 <b>Выбор квартиры</b>\n\nВыберите количество комнат (можно несколько):"
    await callback.message.edit_text(text, reply_markup=get_rooms_keyboard(selected, any_selected))
    await callback.answer()


@router.callback_query(F.data == "rooms_next", ApartmentSearchStates.choosing_rooms)
async def proceed_to_price(callback: CallbackQuery, state: FSMContext):
    """Переход к выбору цены"""
    data = await state.get_data()
    if not data.get('rooms') and not data.get('rooms_any'):
        await callback.answer("Выберите количество комнат или отметьте 'Не важно'", show_alert=True)
        return

    await state.set_state(ApartmentSearchStates.choosing_price)
    selected = data.get('price_ranges', [])
    any_selected = data.get('price_any', False)
    text = "🏠 <b>Выбор квартиры</b>\n\nВыберите ценовой диапазон (можно несколько):"
    await callback.message.edit_text(text, reply_markup=get_price_keyboard(selected, any_selected))
    await callback.answer()


@router.callback_query(F.data.startswith("price_toggle:"), ApartmentSearchStates.choosing_price)
async def toggle_price(callback: CallbackQuery, state: FSMContext):
    """Отмечаем ценовые диапазоны"""
    value = callback.data.split(":", 1)[1]
    data = await state.get_data()
    selected = list(data.get('price_ranges', []))
    any_selected = data.get('price_any', False)

    if value == "any":
        any_selected = not any_selected
        if any_selected:
            selected = []
    else:
        if value in selected:
            selected.remove(value)
        else:
            selected.append(value)
        any_selected = False

    await state.update_data(price_ranges=selected, price_any=any_selected)
    text = "🏠 <b>Выбор квартиры</b>\n\nВыберите ценовой диапазон (можно несколько):"
    await callback.message.edit_text(text, reply_markup=get_price_keyboard(selected, any_selected))
    await callback.answer()


@router.callback_query(F.data == "price_next", ApartmentSearchStates.choosing_price)
async def run_search(callback: CallbackQuery, state: FSMContext):
    """Запускаем поиск после выбора цены"""
    data = await state.get_data()
    if not data.get('price_ranges') and not data.get('price_any'):
        await callback.answer("Выберите диапазон цены или отметьте 'Не важно'", show_alert=True)
        return

    # Выполняем поиск (не очищаем state, чтобы сохранить фильтры для пагинации)
    await show_search_results(callback, state, data, page=1)


@router.callback_query(F.data.startswith("page:"))
async def handle_pagination(callback: CallbackQuery, state: FSMContext):
    """Обработка пагинации"""
    page = int(callback.data.split(":")[1])
    filters = await state.get_data()
    # При пагинации сразу показываем результаты, без сообщения "Ищу квартиры..."
    await show_search_results(callback, state, filters, page, show_loading=False)


async def show_search_results(callback: CallbackQuery, state: FSMContext, filters: dict, page: int = 1, show_loading: bool = True):
    """Показать результаты поиска"""
    message_deleted = False
    
    # Обновляем сообщение о поиске (если это не пагинация)
    if show_loading:
        try:
            await callback.message.edit_text("🔍 Ищу квартиры...")
        except Exception:
            # Сообщение уже удалено или не существует
            message_deleted = True
    else:
        # При пагинации удаляем предыдущее сообщение с пагинацией
        try:
            await callback.message.delete()
            message_deleted = True
        except Exception:
            # Сообщение уже удалено или не существует
            message_deleted = True
    
    # Подготавливаем фильтры для API
    api_filters = {}
    for key in ('type', 'district', 'condition', 'rooms'):
        if filters.get(key):
            api_filters[key] = filters[key]
    if filters.get('area_ranges'):
        api_filters['area_ranges'] = filters['area_ranges']
    if filters.get('price_ranges'):
        api_filters['price_ranges'] = filters['price_ranges']
    
    # Запрос к API
    result = await get_apartments(api_filters, page)
    apartments = result.get('results', [])
    count = result.get('count', 0)
    
    if not apartments:
        text = "😔 К сожалению, по вашим критериям ничего не найдено.\n\nПопробуйте изменить параметры поиска."
        keyboard = get_pagination_keyboard(page, 1, filters)
        if message_deleted:
            await callback.bot.send_message(
                chat_id=callback.message.chat.id,
                text=text,
                reply_markup=keyboard
            )
        else:
            try:
                await callback.message.edit_text(text, reply_markup=keyboard)
            except Exception:
                await callback.bot.send_message(
                    chat_id=callback.message.chat.id,
                    text=text,
                    reply_markup=keyboard
                )
        await callback.answer()
        return
    
    # Вычисляем общее количество страниц
    total_pages = (count + 9) // 10  # 10 квартир на страницу

    # Удаляем сообщение о поиске перед отправкой квартир
    if not message_deleted:
        try:
            await callback.message.delete()
            message_deleted = True
        except Exception:
            message_deleted = True

    # Показываем ВСЕ квартиры на странице
    for idx, apartment in enumerate(apartments):
        card_text = format_apartment_card(apartment)

        # Получаем медиа-группу
        media_group = get_apartment_media_group(apartment)

        if media_group:
            # Если есть изображения, отправляем медиа-группу
            try:
                media_group[0].caption = card_text

                # Логируем информацию о медиа-группе перед отправкой
                print(f"[DEBUG] Квартира {idx+1}/{len(apartments)}: Отправка медиа-группы из {len(media_group)} изображений")
                for i, media in enumerate(media_group):
                    print(f"[DEBUG] Изображение {i+1}: {media.media}")

                await callback.bot.send_media_group(
                    chat_id=callback.message.chat.id,
                    media=media_group
                )
                print(f"[DEBUG] Медиа-группа успешно отправлена")

            except Exception as e:
                # Если ошибка при отправке медиа-группы, отправляем только текст
                print(f"[ERROR] Ошибка при отправке медиа-группы для квартиры {apartment['id']}: {e}")
                await callback.bot.send_message(
                    chat_id=callback.message.chat.id,
                    text=card_text,
                    parse_mode="HTML"
                )
        else:
            # Если нет изображений, отправляем только текст
            await callback.bot.send_message(
                chat_id=callback.message.chat.id,
                text=card_text,
                parse_mode="HTML"
            )

    # Отправляем сообщение с пагинацией в конце
    pagination_text = f"📄 Страница {page} из {total_pages} | Найдено: {count}"
    keyboard = get_pagination_keyboard(page, total_pages, filters)
    await callback.bot.send_message(
        chat_id=callback.message.chat.id,
        text=pagination_text,
        reply_markup=keyboard
    )

    # Предлагаем подписаться на рассылку
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    from services.database import get_subscription

    # Проверяем, есть ли уже подписка
    user_id = callback.from_user.id
    existing_subscription = get_subscription(user_id)

    if existing_subscription:
        subscription_text = (
            "✅ <b>У вас активна подписка на рассылку</b>\n\n"
            "Вы получите уведомление, когда появятся новые квартиры по вашим фильтрам."
        )
        subscription_keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="❌ Отписаться", callback_data="unsubscribe")
        ]])
    else:
        subscription_text = (
            "📬 <b>Не нашли нужную квартиру?</b>\n\n"
            "Подпишитесь на рассылку, и мы сообщим вам, когда появятся новые квартиры "
            "по вашим фильтрам!"
        )
        subscription_keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="📬 Подписаться на рассылку", callback_data="subscribe")
        ]])

    await callback.bot.send_message(
        chat_id=callback.message.chat.id,
        text=subscription_text,
        reply_markup=subscription_keyboard
    )

    await callback.answer()

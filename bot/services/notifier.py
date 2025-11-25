"""
Система уведомлений о новых квартирах для подписчиков
"""
import asyncio
from typing import Dict, List
from aiogram import Bot

from services.api import get_apartments
from services.database import (
    get_all_subscriptions,
    get_last_checked_apartment_id,
    update_last_checked_apartment_id
)
from utils.formatters import format_apartment_card, get_apartment_media_group


def apartment_matches_filters(apartment: Dict, filters: Dict) -> bool:
    """
    Проверяет, соответствует ли квартира фильтрам подписки

    Args:
        apartment: Данные квартиры
        filters: Фильтры подписки

    Returns:
        True если квартира соответствует фильтрам
    """
    # Проверяем тип жилья
    if filters.get('type') and not filters.get('type_any'):
        if apartment['type'] not in filters['type']:
            return False

    # Проверяем район
    if filters.get('district') and not filters.get('district_any'):
        if apartment['district'] not in filters['district']:
            return False

    # Проверяем состояние
    if filters.get('condition') and not filters.get('condition_any'):
        if apartment['condition'] not in filters['condition']:
            return False

    # Проверяем количество комнат
    if filters.get('rooms') and not filters.get('rooms_any'):
        if apartment['rooms'] not in filters['rooms']:
            return False

    # Проверяем площадь
    if filters.get('area_ranges') and not filters.get('area_any'):
        area = apartment['area']
        matches_area = False
        for area_range in filters['area_ranges']:
            parts = area_range.split(':')
            min_area = float(parts[0]) if parts[0] else 0
            max_area = float(parts[1]) if len(parts) > 1 and parts[1] else float('inf')
            if min_area <= area <= max_area:
                matches_area = True
                break
        if not matches_area:
            return False

    # Проверяем цену
    if filters.get('price_ranges') and not filters.get('price_any'):
        price = apartment['price']
        matches_price = False
        for price_range in filters['price_ranges']:
            parts = price_range.split(':')
            min_price = int(float(parts[0])) if parts[0] else 0
            max_price = int(float(parts[1])) if len(parts) > 1 and parts[1] else float('inf')
            if min_price <= price <= max_price:
                matches_price = True
                break
        if not matches_price:
            return False

    return True


async def send_apartment_notification(bot: Bot, user_id: int, apartment: Dict):
    """
    Отправляет уведомление пользователю о новой квартире

    Args:
        bot: Экземпляр бота
        user_id: ID пользователя Telegram
        apartment: Данные квартиры
    """
    try:
        # Формируем карточку квартиры
        card_text = "🔔 <b>Новая квартира по вашим фильтрам!</b>\n\n" + format_apartment_card(apartment)

        # Получаем медиа-группу
        media_group = get_apartment_media_group(apartment)

        if media_group and len(media_group) >= 2:
            # Отправляем медиа-группу (2+ фото)
            media_group[0].caption = card_text
            await bot.send_media_group(chat_id=user_id, media=media_group)
        elif media_group and len(media_group) == 1:
            # Отправляем одно фото
            await bot.send_photo(
                chat_id=user_id,
                photo=media_group[0].media,
                caption=card_text,
                parse_mode="HTML"
            )
        else:
            # Отправляем только текст
            await bot.send_message(chat_id=user_id, text=card_text, parse_mode="HTML")

        print(f"[NOTIFIER] Отправлено уведомление пользователю {user_id} о квартире {apartment['id']}")

    except Exception as e:
        print(f"[ERROR] Ошибка при отправке уведомления пользователю {user_id}: {e}")


async def check_new_apartments(bot: Bot):
    """
    Проверяет новые квартиры и отправляет уведомления подписчикам

    Args:
        bot: Экземпляр бота
    """
    print("[NOTIFIER] Начинаю проверку новых квартир...")

    # Получаем ID последней проверенной квартиры
    last_checked_id = get_last_checked_apartment_id()
    print(f"[NOTIFIER] Последняя проверенная квартира: {last_checked_id}")

    # Получаем все квартиры (последняя страница, отсортированные по дате создания)
    result = await get_apartments({}, page=1)
    apartments = result.get('results', [])

    if not apartments:
        print("[NOTIFIER] Нет квартир в базе")
        return

    # Фильтруем только новые квартиры
    new_apartments = []
    max_apartment_id = 0

    for apartment in apartments:
        apartment_id = apartment['id']
        max_apartment_id = max(max_apartment_id, apartment_id)

        if last_checked_id is None or apartment_id > last_checked_id:
            new_apartments.append(apartment)

    print(f"[NOTIFIER] Найдено новых квартир: {len(new_apartments)}")

    if not new_apartments:
        # Обновляем ID последней проверки даже если нет новых квартир
        if max_apartment_id > 0:
            update_last_checked_apartment_id(max_apartment_id)
        return

    # Получаем все подписки
    subscriptions = get_all_subscriptions()
    print(f"[NOTIFIER] Активных подписок: {len(subscriptions)}")

    if not subscriptions:
        # Обновляем ID последней проверки
        update_last_checked_apartment_id(max_apartment_id)
        return

    # Для каждой новой квартиры проверяем подписки
    notifications_sent = 0
    for apartment in new_apartments:
        print(f"[NOTIFIER] Проверяю квартиру {apartment['id']}")

        for subscription in subscriptions:
            user_id = subscription['user_id']
            filters = subscription['filters']

            # Проверяем, подходит ли квартира под фильтры
            if apartment_matches_filters(apartment, filters):
                await send_apartment_notification(bot, user_id, apartment)
                notifications_sent += 1
                # Небольшая задержка между отправками
                await asyncio.sleep(0.5)

    print(f"[NOTIFIER] Отправлено уведомлений: {notifications_sent}")

    # Обновляем ID последней проверенной квартиры
    update_last_checked_apartment_id(max_apartment_id)
    print(f"[NOTIFIER] Обновлен ID последней проверки: {max_apartment_id}")


async def start_notification_scheduler(bot: Bot, interval_minutes: int = 5):
    """
    Запускает периодическую проверку новых квартир

    Args:
        bot: Экземпляр бота
        interval_minutes: Интервал проверки в минутах (по умолчанию 5 минут)
    """
    print(f"[NOTIFIER] Запущен планировщик проверки новых квартир (интервал: {interval_minutes} мин)")

    while True:
        try:
            await check_new_apartments(bot)
        except Exception as e:
            print(f"[ERROR] Ошибка в планировщике уведомлений: {e}")

        # Ждем следующей проверки
        await asyncio.sleep(interval_minutes * 60)

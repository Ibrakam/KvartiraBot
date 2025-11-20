import asyncio
import logging
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from handlers import start, apartment_search, search_by_id, subscription, menu
from services.notifier import start_notification_scheduler

load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения")

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


async def main():
    # Регистрация роутеров
    dp.include_router(start.router)
    dp.include_router(menu.router)
    dp.include_router(apartment_search.router)
    dp.include_router(search_by_id.router)
    dp.include_router(subscription.router)

    # Запуск системы уведомлений в фоновом режиме
    # Интервал проверки: 5 минут (можно изменить)
    notification_task = asyncio.create_task(start_notification_scheduler(bot, interval_minutes=60))

    # Запуск бота
    logger.info("Бот запущен")
    logger.info("Система уведомлений запущена (интервал: 5 минут)")

    try:
        await dp.start_polling(bot)
    finally:
        # Отменяем фоновую задачу при остановке бота
        notification_task.cancel()


if __name__ == '__main__':
    asyncio.run(main())


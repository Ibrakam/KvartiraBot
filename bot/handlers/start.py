from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from keyboards.inline import get_main_menu_keyboard

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    text = (
        "🏠 <b>Добро пожаловать в Tashkent Estate Bot!</b>\n\n"
        "Я помогу вам подобрать квартиру в Ташкенте.\n\n"
        "Выберите действие из меню:"
    )
    await message.answer(text, reply_markup=get_main_menu_keyboard())


@router.message(Command("check_new"))
async def cmd_check_new(message: Message):
    """Команда для ручной проверки новых квартир (для тестирования)"""
    from services.notifier import check_new_apartments

    await message.answer("🔍 Запускаю проверку новых квартир...")

    try:
        await check_new_apartments(message.bot)
        await message.answer("✅ Проверка завершена! Уведомления отправлены подписчикам.")
    except Exception as e:
        await message.answer(f"❌ Ошибка при проверке: {e}")




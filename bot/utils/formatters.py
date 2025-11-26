import os
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urlparse

from aiogram.types import InputMediaPhoto, FSInputFile
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_MEDIA_ROOT = BASE_DIR / 'backend' / 'media'
ENV_MEDIA_ROOT = os.getenv('LOCAL_MEDIA_ROOT')
LOCAL_MEDIA_ROOT = Path(ENV_MEDIA_ROOT).expanduser() if ENV_MEDIA_ROOT else DEFAULT_MEDIA_ROOT


def _resolve_local_media_path(image_ref: str) -> Optional[Path]:
    """Пытается найти локальный файл для указанного пути/URL"""
    print(f"  [RESOLVE] Попытка найти локальный файл для: '{image_ref}'")

    if not image_ref:
        print(f"  [RESOLVE] ❌ image_ref пустой")
        return None

    image_ref = image_ref.strip()
    if not image_ref:
        print(f"  [RESOLVE] ❌ image_ref пустой после strip")
        return None

    # Сначала проверяем, не является ли это уже полным путём к файлу
    candidate = Path(image_ref)
    print(f"  [RESOLVE] Проверка как абсолютный путь: {candidate}")
    if candidate.is_file():
        print(f"  [RESOLVE] ✅ Найден как абсолютный путь: {candidate}")
        return candidate

    # Парсим URL если это URL
    parsed = urlparse(image_ref)
    print(f"  [RESOLVE] URL parsed - scheme: '{parsed.scheme}', hostname: '{parsed.hostname}', path: '{parsed.path}'")

    path_part = ''
    if parsed.scheme in ('http', 'https'):
        host = parsed.hostname or ''
        if host not in {'localhost', '127.0.0.1'}:
            print(f"  [RESOLVE] ⚠️  Хост '{host}' не localhost, пропускаем")
            return None
        path_part = parsed.path or ''
    else:
        path_part = image_ref

    path_part = path_part.lstrip('/')
    print(f"  [RESOLVE] path_part после lstrip('/'): '{path_part}'")

    if path_part.startswith('media/'):
        path_part = path_part[len('media/') :]
        print(f"  [RESOLVE] Убрали префикс 'media/', осталось: '{path_part}'")

    if not path_part:
        print(f"  [RESOLVE] ❌ path_part пустой после обработки")
        return None

    candidate = LOCAL_MEDIA_ROOT / path_part
    print(f"  [RESOLVE] Финальный путь для проверки: {candidate}")
    print(f"  [RESOLVE] Файл существует: {candidate.exists()}")
    print(f"  [RESOLVE] Это файл: {candidate.is_file()}")

    if candidate.is_file():
        print(f"  [RESOLVE] ✅ НАЙДЕН: {candidate}")
        return candidate

    print(f"  [RESOLVE] ❌ Файл не найден")
    return None


def format_apartment_card(apartment: Dict) -> str:
    """
    Форматировать карточку квартиры для отображения
    
    Args:
        apartment: Словарь с данными квартиры
    
    Returns:
        Отформатированная строка
    """
    rooms_text = f"{apartment['rooms']}-х комнатная"
    if apartment['rooms'] >= 5:
        rooms_text = "5+ комнатная"
    
    card = (
        f"🏙 {rooms_text} квартира"
    )
    
    if apartment.get('address'):
        card += f"\n📍 Адрес: {apartment['address']}"
    
    card += f"\n🆔 ID: {apartment['id']}"
    card += f"\n🏢 Тип: {apartment['type']}"
    card += f"\n🛠 Ремонт: {apartment['condition']}"
    
    if apartment.get('orientation'):
        card += f"\n📍 Ориентир: {apartment['orientation']}"
    
    card += f"\n📌 Район: {apartment['district']}"
    card += f"\n🚪 Комнаты: {apartment['rooms']}"
    card += f"\n🏗 Этаж: {apartment['floor']} из {apartment['floors_total']}"
    card += f"\n📏 Площадь: {apartment['area']} м²"
    card += f"\n💰 Цена: ${apartment['price']:,}".replace(',', ' ')
    
    if apartment.get('description'):
        card += f"\n\n📝 {apartment['description']}"
    
    card += f"\n\n💬 Заинтересовало? Свяжитесь:\n"
    card += f"📞 {apartment['contact_phone']} — {apartment['contact_name']}"
    
    return card


def get_apartment_media_group(apartment: Dict, base_url: str = "") -> List[InputMediaPhoto]:
    """
    Создать медиа-группу с изображениями квартиры

    Args:
        apartment: Словарь с данными квартиры
        base_url: Базовый URL сервера (например, http://localhost:8000) для относительных URL

    Returns:
        Список InputMediaPhoto (максимум 10, т.к. Telegram поддерживает до 10 фото в медиа-группе)
    """
    print(f"\n{'='*80}")
    print(f"[MEDIA_GROUP] Создание медиа-группы для квартиры ID: {apartment.get('id')}")
    print(f"[MEDIA_GROUP] LOCAL_MEDIA_ROOT: {LOCAL_MEDIA_ROOT}")
    print(f"{'='*80}\n")

    media_group = []
    images = apartment.get('images', [])
    print(f"[MEDIA_GROUP] Всего изображений в квартире: {len(images)}")
    
    # Если base_url не передан, пытаемся получить из API_BASE_URL
    if not base_url:
        api_base_url = os.getenv('API_BASE_URL', 'http://localhost:8000/api')
        # Убираем /api из конца, если есть
        base_url = api_base_url.rstrip('/api').rstrip('/')
    
    # Берем максимум 10 изображений (лимит Telegram для медиа-группы)
    for idx, img in enumerate(images[:10], 1):
        print(f"\n[IMAGE {idx}] Обработка изображения {idx}/{min(len(images), 10)}")
        print(f"[IMAGE {idx}] Полные данные изображения: {img}")

        image_url = img.get('image_url')
        print(f"[IMAGE {idx}] Извлечённый image_url: '{image_url}'")
        print(f"[IMAGE {idx}] Тип image_url: {type(image_url)}")
        
        # Пропускаем None, пустые строки и невалидные URL
        if not image_url or not isinstance(image_url, str):
            print(f"[IMAGE {idx}] ❌ ПРОПУЩЕНО: image_url пустой или не строка")
            continue

        # Убираем пробелы
        image_url = image_url.strip()
        if not image_url:
            print(f"[IMAGE {idx}] ❌ ПРОПУЩЕНО: image_url пустой после strip")
            continue

        print(f"[IMAGE {idx}] После strip: '{image_url}'")

        # Пытаемся найти и использовать локальный файл
        print(f"[IMAGE {idx}] Попытка найти локальный файл...")
        local_file = _resolve_local_media_path(image_url)

        if local_file:
            print(f"[IMAGE {idx}] ✅ Локальный файл найден: {local_file}")
            print(f"[IMAGE {idx}] Файл существует: {local_file.exists()}")
            print(f"[IMAGE {idx}] Размер файла: {local_file.stat().st_size if local_file.exists() else 'N/A'} байт")
            try:
                media_group.append(InputMediaPhoto(media=FSInputFile(str(local_file))))
                print(f"[IMAGE {idx}] ✅ УСПЕШНО добавлено в медиа-группу как локальный файл")
                continue
            except Exception as e:
                print(f"[IMAGE {idx}] ❌ ОШИБКА при добавлении локального файла: {e}")
        else:
            print(f"[IMAGE {idx}] ⚠️  Локальный файл НЕ найден, попытка использовать URL")
        
        final_url = image_url
        print(f"[IMAGE {idx}] Формирование финального URL...")
        print(f"[IMAGE {idx}] base_url: '{base_url}'")

        # Если URL относительный (начинается с /), добавляем base_url
        if final_url.startswith('/') and base_url:
            final_url = base_url.rstrip('/') + final_url
            print(f"[IMAGE {idx}] Добавлен base_url (относительный путь): '{final_url}'")
        elif not final_url.startswith(('http://', 'https://')) and base_url:
            if not final_url.startswith('http'):
                final_url = base_url.rstrip('/') + '/' + final_url.lstrip('/')
                print(f"[IMAGE {idx}] Добавлен base_url (вариант 2): '{final_url}'")
        
        # Проверяем, что URL валидный (начинается с http:// или https://)
        if not final_url.startswith(('http://', 'https://')):
            print(f"[IMAGE {idx}] ❌ ОШИБКА: Невалидный URL (не начинается с http/https): '{final_url}'")
            continue

        # Проверяем, что URL не содержит пробелов или других недопустимых символов
        if ' ' in final_url or '\n' in final_url or '\r' in final_url:
            print(f"[IMAGE {idx}] ❌ ОШИБКА: URL содержит недопустимые символы: '{final_url}'")
            continue

        # Проверяем, что URL не указывает на localhost (Telegram не может получить доступ)
        if 'localhost' in final_url or '127.0.0.1' in final_url:
            print(f"[IMAGE {idx}] ⚠️  WARNING: URL указывает на localhost: '{final_url}'")
            print(f"[IMAGE {idx}] Telegram не может получить доступ к localhost. Попытка найти локальный файл...")
            # В последний раз пробуем найти локальный файл по нормализованному URL
            alt_local = _resolve_local_media_path(final_url)
            if alt_local:
                print(f"[IMAGE {idx}] ✅ Найден локальный файл (fallback): {alt_local}")
                try:
                    media_group.append(InputMediaPhoto(media=FSInputFile(str(alt_local))))
                    print(f"[IMAGE {idx}] ✅ УСПЕШНО добавлено через fallback")
                except Exception as e:
                    print(f"[IMAGE {idx}] ❌ ОШИБКА при добавлении через fallback: {e}")
            else:
                print(f"[IMAGE {idx}] ❌ Локальный файл не найден через fallback")
            continue

        print(f"[IMAGE {idx}] Финальный URL для отправки: '{final_url}'")

        try:
            media_group.append(InputMediaPhoto(media=final_url))
            print(f"[IMAGE {idx}] ✅ УСПЕШНО добавлено в медиа-группу как URL")
        except Exception as e:
            print(f"[IMAGE {idx}] ❌ ОШИБКА при добавлении URL в медиа-группу: {e}")
            continue

    print(f"\n{'='*80}")
    print(f"[MEDIA_GROUP] Итого добавлено изображений в медиа-группу: {len(media_group)}/{len(images)}")
    print(f"{'='*80}\n")

    return media_group

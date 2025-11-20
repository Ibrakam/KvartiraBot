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
    if not image_ref:
        return None
    image_ref = image_ref.strip()
    if not image_ref:
        return None
    candidate = Path(image_ref)
    if candidate.is_file():
        return candidate
    parsed = urlparse(image_ref)
    path_part = ''
    if parsed.scheme in ('http', 'https'):
        host = parsed.hostname or ''
        if host not in {'localhost', '127.0.0.1'}:
            return None
        path_part = parsed.path or ''
    else:
        path_part = image_ref
    path_part = path_part.lstrip('/')
    if path_part.startswith('media/'):
        path_part = path_part[len('media/') :]
    if not path_part:
        return None
    candidate = LOCAL_MEDIA_ROOT / path_part
    if candidate.is_file():
        return candidate
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
        Список InputMediaPhoto (максимум 5)
    """
    media_group = []
    images = apartment.get('images', [])
    
    # Если base_url не передан, пытаемся получить из API_BASE_URL
    if not base_url:
        api_base_url = os.getenv('API_BASE_URL', 'http://localhost:8000/api')
        # Убираем /api из конца, если есть
        base_url = api_base_url.rstrip('/api').rstrip('/')
    
    # Берем максимум 5 изображений
    for img in images[:5]:
        image_url = img.get('image_url')
        
        # Логируем исходный URL для отладки
        print(f"[DEBUG] Исходный image_url: {image_url}, тип: {type(image_url)}")
        
        # Пропускаем None, пустые строки и невалидные URL
        if not image_url or not isinstance(image_url, str):
            print(f"[DEBUG] Пропущен: image_url пустой или не строка")
            continue
        
        # Убираем пробелы
        image_url = image_url.strip()
        if not image_url:
            print(f"[DEBUG] Пропущен: image_url пустой после strip")
            continue
        
        print(f"[DEBUG] После strip: {image_url}")
        local_file = _resolve_local_media_path(image_url)
        if local_file:
            try:
                media_group.append(InputMediaPhoto(media=FSInputFile(str(local_file))))
                print(f"[DEBUG] Используем локальный файл: {local_file}")
                continue
            except Exception as e:
                print(f"[ERROR] Не удалось прикрепить локальный файл {local_file}: {e}")
        
        final_url = image_url
        # Если URL относительный (начинается с /), добавляем base_url
        if final_url.startswith('/') and base_url:
            final_url = base_url.rstrip('/') + final_url
            print(f"[DEBUG] После добавления base_url: {final_url}")
        elif not final_url.startswith(('http://', 'https://')) and base_url:
            if not final_url.startswith('http'):
                final_url = base_url.rstrip('/') + '/' + final_url.lstrip('/')
                print(f"[DEBUG] После добавления base_url (вариант 2): {final_url}")
        
        # Проверяем, что URL валидный (начинается с http:// или https://)
        if not final_url.startswith(('http://', 'https://')):
            print(f"[ERROR] Пропущен невалидный URL изображения: {final_url}")
            continue
        
        # Проверяем, что URL не содержит пробелов или других недопустимых символов
        if ' ' in final_url or '\n' in final_url or '\r' in final_url:
            print(f"[ERROR] URL содержит недопустимые символы: {final_url}")
            continue
        
        # Проверяем, что URL не указывает на localhost (Telegram не может получить доступ)
        if 'localhost' in final_url or '127.0.0.1' in final_url:
            print(f"[WARNING] URL указывает на localhost: {final_url}")
            print(f"[WARNING] Telegram не может получить доступ к localhost. Используйте ngrok или внешний хостинг.")
            # В последний раз пробуем найти локальный файл по нормализованному URL
            alt_local = _resolve_local_media_path(final_url)
            if alt_local:
                try:
                    media_group.append(InputMediaPhoto(media=FSInputFile(str(alt_local))))
                    print(f"[DEBUG] Используем локальный файл (fallback): {alt_local}")
                except Exception as e:
                    print(f"[ERROR] Не удалось прикрепить локальный файл {alt_local}: {e}")
            continue
        
        print(f"[DEBUG] Финальный URL для отправки: {final_url}")
        
        try:
            media_group.append(InputMediaPhoto(media=final_url))
            print(f"[DEBUG] Изображение успешно добавлено в медиа-группу")
        except Exception as e:
            print(f"[ERROR] Ошибка при добавлении изображения {final_url}: {e}")
            continue
    
    return media_group

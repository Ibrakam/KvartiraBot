import aiohttp
import os
from typing import Optional, Dict
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000/api')


async def get_apartments(filters: Optional[Dict] = None, page: int = 1) -> Dict:
    """
    Получить список квартир с фильтрами
    
    Args:
        filters: Словарь с фильтрами
        page: Номер страницы
    
    Returns:
        Словарь с результатами и пагинацией
    """
    url = f"{API_BASE_URL}/apartments/"
    params = [('page', page)]
    
    if filters:
        # Добавляем фильтры в параметры запроса
        for key in ('type', 'district', 'condition'):
            values = filters.get(key)
            if values:
                for value in values:
                    params.append((key, value))
        if filters.get('rooms'):
            for value in filters['rooms']:
                params.append(('rooms', value))
        if filters.get('area_ranges'):
            for value in filters['area_ranges']:
                params.append(('area_range', value))
        if filters.get('price_ranges'):
            for value in filters['price_ranges']:
                params.append(('price_range', value))
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    return {'results': [], 'count': 0, 'next': None, 'previous': None}
        except Exception as e:
            print(f"Ошибка при запросе к API: {e}")
            return {'results': [], 'count': 0, 'next': None, 'previous': None}


async def get_apartment_by_id(apartment_id: int) -> Optional[Dict]:
    """
    Получить квартиру по ID
    
    Args:
        apartment_id: ID квартиры
    
    Returns:
        Словарь с данными квартиры или None
    """
    url = f"{API_BASE_URL}/apartments/{apartment_id}/"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return None
        except Exception as e:
            print(f"Ошибка при запросе к API: {e}")
            return None


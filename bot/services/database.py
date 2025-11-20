import sqlite3
import json
from typing import Optional, Dict, List
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / 'bot.db'


def get_connection():
    """Получить соединение с БД"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Инициализация базы данных"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscriptions (
            user_id INTEGER PRIMARY KEY,
            filters TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Таблица для отслеживания последних проверенных квартир
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS last_check (
            id INTEGER PRIMARY KEY,
            last_apartment_id INTEGER,
            checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()


def add_subscription(user_id: int, filters: Dict):
    """Добавить подписку пользователя"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO subscriptions (user_id, filters)
        VALUES (?, ?)
    ''', (user_id, json.dumps(filters)))
    
    conn.commit()
    conn.close()


def remove_subscription(user_id: int):
    """Удалить подписку пользователя"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM subscriptions WHERE user_id = ?', (user_id,))
    
    conn.commit()
    conn.close()


def get_subscription(user_id: int) -> Optional[Dict]:
    """Получить подписку пользователя"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT filters FROM subscriptions WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    
    conn.close()
    
    if row:
        return json.loads(row[0])
    return None


def get_all_subscriptions() -> List[Dict]:
    """Получить все подписки"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT user_id, filters FROM subscriptions')
    rows = cursor.fetchall()

    conn.close()

    return [{'user_id': row[0], 'filters': json.loads(row[1])} for row in rows]


def get_last_checked_apartment_id() -> Optional[int]:
    """Получить ID последней проверенной квартиры"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT last_apartment_id FROM last_check WHERE id = 1')
    row = cursor.fetchone()

    conn.close()

    return row[0] if row else None


def update_last_checked_apartment_id(apartment_id: int):
    """Обновить ID последней проверенной квартиры"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT OR REPLACE INTO last_check (id, last_apartment_id, checked_at)
        VALUES (1, ?, CURRENT_TIMESTAMP)
    ''', (apartment_id,))

    conn.commit()
    conn.close()


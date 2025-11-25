from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def _mark_selected(text: str, selected: bool) -> str:
    """Добавляет галочку к выбранной опции"""
    return f"{text} ✅" if selected else text


def get_main_menu_keyboard():
    """Главное меню бота"""
    keyboard = [
        [InlineKeyboardButton(text="🏠 Выбор квартиры", callback_data="search_apartment")],
        [InlineKeyboardButton(text="✉️ Подписаться на рассылку", callback_data="subscribe")],
        [InlineKeyboardButton(text="⛔ Отписаться от рассылки", callback_data="unsubscribe")],
        [InlineKeyboardButton(text="👤 Обо мне", callback_data="about")],
        [InlineKeyboardButton(text="📢 Канал с вариантами квартир", callback_data="channel")],
        [InlineKeyboardButton(text="💬 Связаться со мной", callback_data="contact")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_type_keyboard(selected=None, any_selected: bool = False):
    """Клавиатура выбора типа жилья"""
    selected = selected or []
    keyboard = [
        [InlineKeyboardButton(
            text=_mark_selected("Новостройка", "Новостройка" in selected),
            callback_data="type_toggle:Новостройка"
        )],
        [InlineKeyboardButton(
            text=_mark_selected("Вторичное жильё", "Вторичное жильё" in selected),
            callback_data="type_toggle:Вторичное жильё"
        )],
        [InlineKeyboardButton(
            text=_mark_selected("Не важно", any_selected),
            callback_data="type_toggle:any"
        )],
    ]

    if selected or any_selected:
        keyboard.append([InlineKeyboardButton(text="Далее ▶️", callback_data="type_next")])

    keyboard.append([InlineKeyboardButton(text="◀️ Отмена", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_district_keyboard(selected=None, any_selected: bool = False):
    """Клавиатура выбора района"""
    selected = selected or []
    districts = [
        "Мирабадский",
        "Мирзо-Улугбекский",
        "Юнусабадский",
        "Шайхантохурский",
        "Яккасарайский",
        "Яшнабадский",
    ]
    keyboard = []
    for district in districts:
        keyboard.append([
            InlineKeyboardButton(
                text=_mark_selected(district, district in selected),
                callback_data=f"district_toggle:{district}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            text=_mark_selected("Не важно", any_selected),
            callback_data="district_toggle:any"
        )
    ])

    if selected or any_selected:
        keyboard.append([InlineKeyboardButton(text="Далее ▶️", callback_data="district_next")])

    keyboard.append([InlineKeyboardButton(text="◀️ Назад", callback_data="search_apartment")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_condition_keyboard(selected=None, any_selected: bool = False):
    """Клавиатура выбора типа ремонта"""
    selected = selected or []
    keyboard = [
        [InlineKeyboardButton(
            text=_mark_selected("С ремонтом", "С ремонтом" in selected),
            callback_data="condition_toggle:С ремонтом"
        )],
        [InlineKeyboardButton(
            text=_mark_selected("Без ремонта", "Без ремонта" in selected),
            callback_data="condition_toggle:Без ремонта"
        )],
        [InlineKeyboardButton(
            text=_mark_selected("Среднее состояние", "Среднее состояние" in selected),
            callback_data="condition_toggle:Среднее состояние"
        )],
        [InlineKeyboardButton(
            text=_mark_selected("Не важно", any_selected),
            callback_data="condition_toggle:any"
        )],
    ]

    if selected or any_selected:
        keyboard.append([InlineKeyboardButton(text="Далее ▶️", callback_data="condition_next")])

    keyboard.append([InlineKeyboardButton(text="◀️ Назад", callback_data="search_apartment")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_area_keyboard(selected=None, any_selected: bool = False):
    """Клавиатура выбора площади"""
    selected = selected or []
    areas = [
        ("до 40 м²", "0:40"),
        ("40-66 м²", "40:66"),
        ("67-85 м²", "67:85"),
        ("85-105 м²", "85:105"),
        ("105-130 м²", "105:130"),
        ("131-160 м²", "131:160"),
        ("161-200 м²", "161:200"),
        ("более 200 м²", "200:9999"),
    ]
    keyboard = []
    for label, data in areas:
        keyboard.append([
            InlineKeyboardButton(
                text=_mark_selected(label, data in selected),
                callback_data=f"area_toggle:{data}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            text=_mark_selected("Не важно", any_selected),
            callback_data="area_toggle:any"
        )
    ])

    if selected or any_selected:
        keyboard.append([InlineKeyboardButton(text="Далее ▶️", callback_data="area_next")])

    keyboard.append([InlineKeyboardButton(text="◀️ Назад", callback_data="search_apartment")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_rooms_keyboard(selected=None, any_selected: bool = False):
    """Клавиатура выбора количества комнат"""
    selected = selected or []
    keyboard = [
        [InlineKeyboardButton(
            text=_mark_selected("1", 1 in selected),
            callback_data="rooms_toggle:1"
        ),
         InlineKeyboardButton(
             text=_mark_selected("2", 2 in selected),
             callback_data="rooms_toggle:2"
         ),
         InlineKeyboardButton(
             text=_mark_selected("3", 3 in selected),
             callback_data="rooms_toggle:3"
         )],
        [InlineKeyboardButton(
            text=_mark_selected("4", 4 in selected),
            callback_data="rooms_toggle:4"
        ),
         InlineKeyboardButton(
             text=_mark_selected("5+", 5 in selected),
             callback_data="rooms_toggle:5"
         )],
        [InlineKeyboardButton(
            text=_mark_selected("Не важно", any_selected),
            callback_data="rooms_toggle:any"
        )],
    ]

    if selected or any_selected:
        keyboard.append([InlineKeyboardButton(text="Далее ▶️", callback_data="rooms_next")])

    keyboard.append([InlineKeyboardButton(text="◀️ Назад", callback_data="search_apartment")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_price_keyboard(selected=None, any_selected: bool = False):
    """Клавиатура выбора ценового диапазона"""
    selected = selected or []
    prices = [
        ("до 70 000 $", "0:70000"),
        ("70-100 000 $", "70000:100000"),
        ("100-150 000 $", "100000:150000"),
        ("150-200 000 $", "150000:200000"),
        ("более 200 000 $", "200000:999999"),
    ]
    keyboard = []
    for label, data in prices:
        keyboard.append([
            InlineKeyboardButton(
                text=_mark_selected(label, data in selected),
                callback_data=f"price_toggle:{data}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            text=_mark_selected("Не важно", any_selected),
            callback_data="price_toggle:any"
        )
    ])

    if selected or any_selected:
        keyboard.append([InlineKeyboardButton(text="Далее ▶️", callback_data="price_next")])

    keyboard.append([InlineKeyboardButton(text="◀️ Назад", callback_data="search_apartment")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_pagination_keyboard(page: int, total_pages: int, filters: dict):
    """Клавиатура пагинации результатов"""
    keyboard = []
    buttons = []
    
    if page > 1:
        buttons.append(InlineKeyboardButton(text="◀️ Назад", callback_data=f"page:{page-1}"))
    if page < total_pages:
        buttons.append(InlineKeyboardButton(text="Вперёд ▶️", callback_data=f"page:{page+1}"))
    
    if buttons:
        keyboard.append(buttons)
    
    keyboard.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)



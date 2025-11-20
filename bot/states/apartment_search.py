from aiogram.fsm.state import State, StatesGroup


class ApartmentSearchStates(StatesGroup):
    """Состояния для процесса поиска квартиры"""
    choosing_type = State()
    choosing_district = State()
    choosing_condition = State()
    choosing_area = State()
    choosing_rooms = State()
    choosing_price = State()




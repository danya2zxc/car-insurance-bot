from aiogram.fsm.state import State, StatesGroup


class Form(StatesGroup):
    waiting_for_passport = State()
    waiting_for_vehicle_document = State()
    waiting_for_summary_confirmation = State()
    waiting_for_price_confirmation = State()
    waiting_for_change_choice = State()

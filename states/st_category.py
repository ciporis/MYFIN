from aiogram.fsm.state import State, StatesGroup

class st_Category(StatesGroup):
    title_state = State()
    edit_title_state = State()
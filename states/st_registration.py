from aiogram.fsm.state import State, StatesGroup

class st_Registration(StatesGroup):
    fio_state = State()
    phone_number_state = State()

    fio_key: str = "fio"
    phone_number_key: str = "phone_number"
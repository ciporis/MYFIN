from aiogram.fsm.state import State, StatesGroup

class st_WalletCreation(StatesGroup):
    title_state = State()
    amount_state = State()
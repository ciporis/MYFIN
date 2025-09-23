from aiogram.fsm.state import State, StatesGroup

class st_User_Commands(StatesGroup):
    comment_key: str = "comment"
    phone_number_key: str = "phone_number"

    class st_IncomeCommand(StatesGroup):
        income_command_state = State()
        amount_state = State()
        category_state = State()
        comment_state = State()

    class st_OutcomeCommand(StatesGroup):
        outcome_command_state = State()
        amount_state = State()
        category_state = State()
        comment_state = State()

    class st_TransferCommand(StatesGroup):
        transfer_command_state = State()
        phone_number_state = State()
        amount_state = State()
        category_state = State()
        comment_state = State()

    class st_EditProfile(StatesGroup):
        fio_state = State()
        phone_number_state = State()
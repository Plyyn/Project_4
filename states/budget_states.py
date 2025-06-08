from aiogram.fsm.state import StatesGroup, State


class BudgetStates(StatesGroup):
    """FSM состояния для управления бюджетом пользователя"""

    waiting_for_amount = State()  # Ожидание ввода суммы бюджета (положительное число)
    waiting_for_confirmation = State()  # Ожидание подтверждения (да/нет)

    # Добавьте метод для проверки состояний
    @classmethod
    def get_state_names(cls) -> list[str]:
        return [state.name for state in cls.__states__]
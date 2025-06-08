from aiogram.fsm.state import StatesGroup, State


class CurrencyStates(StatesGroup):
    """FSM состояния для конвертации валют"""

    waiting_for_amount = State()  # Ожидание ввода суммы в RUB (положительное число)
    waiting_for_currency = State()  # Ожидание выбора валюты из списка

    # Добавьте список поддерживаемых валют
    @staticmethod
    def supported_currencies() -> tuple:
        return ("USD", "EUR", "GBP", "CNY", "JPY", "TRY", "KZT", "UAH", "BYN")
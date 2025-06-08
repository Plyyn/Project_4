from datetime import datetime
from typing import Union


def format_money(amount: Union[float, int], currency: str = "руб.") -> str:
    """Форматирование денежных сумм с разделением тысяч и указанием валюты.

    Args:
        amount: Сумма для форматирования
        currency: Обозначение валюты (по умолчанию 'руб.')

    Returns:
        Строка вида "12 345,67 руб."
    """
    try:
        return f"{float(amount):,.2f} {currency}".replace(",", " ").replace(".", ",")
    except (ValueError, TypeError):
        return f"0,00 {currency}"


def format_date(dt: datetime, with_time: bool = True) -> str:
    """Форматирование даты в удобочитаемый вид.

    Args:
        dt: Объект datetime для форматирования
        with_time: Включать ли время в вывод

    Returns:
        Строка вида "01.01.2023 12:00" или "01.01.2023"
    """
    fmt = "%d.%m.%Y %H:%M" if with_time else "%d.%m.%Y"
    return dt.strftime(fmt) if dt else "Дата не указана"
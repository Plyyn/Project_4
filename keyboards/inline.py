from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="➕ Добавить расход", callback_data="add_expense"),
            InlineKeyboardButton(text="📊 Статистика", callback_data="show_stats")
        ],
        [
            InlineKeyboardButton(text="💰 Установить бюджет", callback_data="set_budget"),
            InlineKeyboardButton(text="🔄 Остаток бюджета", callback_data="remaining_budget")
        ],
        [
            InlineKeyboardButton(text="💱 Конвертер валют", callback_data="convert"),
            InlineKeyboardButton(text="ℹ️ Помощь", callback_data="help")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_currency_keyboard() -> InlineKeyboardMarkup:
    currencies = [
        ("USD", "EUR", "GBP"),
        ("CNY", "JPY", "TRY"),
        ("KZT", "UAH", "BYN")
    ]

    buttons = []
    for row in currencies:
        button_row = []
        for currency in row:
            button_row.append(InlineKeyboardButton(
                text=currency,
                callback_data=f"curr_{currency}"
            ))
        buttons.append(button_row)

    buttons.append([
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_admin_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Статистика", callback_data="stats_all")
    builder.button(text="Рассылка", callback_data="broadcast")
    builder.adjust(1)
    return builder.as_markup()
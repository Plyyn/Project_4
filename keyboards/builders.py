from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from typing import List, Optional


def build_category_keyboard(categories: List[str],
                            skip_button: bool = False,
                            cancel_button: bool = True) -> ReplyKeyboardMarkup:
    """
    Строит reply-клавиатуру для выбора категории расхода
    """
    keyboard = []

    # Добавляем кнопки категорий
    row = []
    for i, category in enumerate(categories):
        row.append(KeyboardButton(text=category))
        if (i + 1) % 2 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    # Добавляем дополнительные кнопки
    additional_buttons = []
    if skip_button:
        additional_buttons.append(KeyboardButton(text="Пропустить"))
    if cancel_button:
        additional_buttons.append(KeyboardButton(text="❌ Отмена"))

    if additional_buttons:
        keyboard.append(additional_buttons)

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )
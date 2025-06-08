from aiogram import Router, F
from aiogram.types import Message, BufferedInputFile, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from states.currency_states import CurrencyStates
from services.currency_api import convert_currency
from services.database import get_session, User, Expense
from services.diagram_generator import generate_pie_chart
from keyboards.inline import get_currency_keyboard, get_main_menu_keyboard




router = Router()


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    session = get_session()
    try:
        user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
        if not user:
            await message.answer("У вас еще нет расходов")
            return

        expenses = session.query(Expense).filter_by(user_id=user.id).all()
        if not expenses:
            await message.answer("У вас еще нет расходов")
            return

        total = sum(exp.amount for exp in expenses)
        remaining = user.budget - total if user.budget > 0 else 0

        img_buffer = generate_pie_chart(message.from_user.id)
        if img_buffer:
            await message.answer_photo(
                BufferedInputFile(img_buffer.read(), filename="stats.png"),
                caption=f"📊 Общие расходы: {total} руб.\n"
                        f"💰 Бюджет: {user.budget} руб.\n"
                        f"🔄 Осталось: {remaining} руб."
            )
        else:
            await message.answer("Не удалось сгенерировать диаграмму")
    finally:
        session.close()

@router.callback_query(F.data == "convert")
async def start_currency_conversion(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "💱 Введите сумму в рублях для конвертации:",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(CurrencyStates.waiting_for_amount)
    await callback.answer()


@router.message(CurrencyStates.waiting_for_amount, F.text.regexp(r'^\d+(\.\d+)?$'))
async def process_currency_amount(message: Message, state: FSMContext):
    amount = float(message.text)
    await state.update_data(amount=amount)
    await message.answer(
        "Выберите валюту для конвертации:",
        reply_markup=get_currency_keyboard()
    )
    await state.set_state(CurrencyStates.waiting_for_currency)


@router.callback_query(CurrencyStates.waiting_for_currency, F.data.startswith("curr_"))
async def process_currency_selection(callback: CallbackQuery, state: FSMContext):
    currency = callback.data.split("_")[1]
    data = await state.get_data()
    amount = data['amount']

    if currency == "cancel":
        await callback.message.answer("❌ Конвертация отменена")
    else:
        result = await convert_currency(amount, "RUB", currency)  # RUB -> выбранная валюта
        if result is None:
            await callback.message.answer("⚠️ Ошибка конвертации. Попробуйте позже.")
        else:
            await callback.message.answer(
                f"🔢 Результат: {amount:.2f} RUB = {result:.2f} {currency}"
            )
    await state.clear()


@router.message(CurrencyStates.waiting_for_amount, Command("cancel"))
@router.message(CurrencyStates.waiting_for_currency, Command("cancel"))
async def cancel_conversion(message: Message, state: FSMContext):
    await message.answer(
        "❌ Конвертация отменена",
        reply_markup=get_main_menu_keyboard()
    )
    await state.clear()



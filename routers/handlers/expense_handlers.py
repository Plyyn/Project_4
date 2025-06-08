from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, CallbackQuery
from aiogram.fsm.context import FSMContext
from states.expense_states import ExpenseStates
from services.database import get_session, User, Expense
from datetime import datetime
from keyboards.builders import build_category_keyboard
from aiogram.filters import Command
from contextlib import contextmanager

router = Router()

categories = ["🍏 Еда", "🚕 Транспорт", "🎮 Развлечения", "📌 Другое"]


@contextmanager
def db_session():
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


@router.message(Command("add"))
async def cmd_add_expense(message: Message, state: FSMContext):
    with db_session() as session:
        user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
        if not user:
            user = User(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name
            )
            session.add(user)
            session.commit()

    await message.answer("Введите сумму расхода:")
    await state.set_state(ExpenseStates.waiting_for_amount)


@router.message(ExpenseStates.waiting_for_amount, F.text.regexp(r'^\d+(\.\d+)?$'))
async def process_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text)
        await state.update_data(amount=amount)
        await message.answer(
            "Выберите категорию:",
            reply_markup=build_category_keyboard(categories))
        await state.set_state(ExpenseStates.waiting_for_category)
    except ValueError:
        await message.answer("Пожалуйста, введите корректную сумму")


@router.message(ExpenseStates.waiting_for_category, F.text.in_(categories))
async def process_category(message: Message, state: FSMContext):
    await state.update_data(category=message.text)
    await message.answer(
        "Введите описание расхода (необязательно):",
        reply_markup=ReplyKeyboardRemove())
    await state.set_state(ExpenseStates.waiting_for_description)


@router.message(ExpenseStates.waiting_for_description)
async def process_description(message: Message, state: FSMContext):
    data = await state.get_data()
    if 'amount' not in data or 'category' not in data:
        await message.answer("Ошибка: данные не найдены. Начните заново.")
        await state.clear()
        return

    try:
        with db_session() as session:
            user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
            if not user:
                await message.answer("Ошибка: пользователь не найден")
                return

            expense = Expense(
                user_id=user.id,
                amount=data['amount'],
                category=data['category'],
                description=message.text if message.text else "Без описания",
                date=datetime.now()
            )
            session.add(expense)

            await message.answer(
                f"✅ Расход добавлен:\n"
                f"Сумма: {data['amount']} руб.\n"
                f"Категория: {data['category']}\n"
                f"Описание: {message.text if message.text else 'Без описания'}"
            )
    except Exception as e:
        await message.answer("Произошла ошибка при сохранении расхода")
        print(f"Ошибка: {e}")
    finally:
        await state.clear()


from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command
from aiogram import F


@router.message(Command("delete"))
async def cmd_delete_expense(message: Message):
    session = get_session()
    try:
        user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
        if not user:
            await message.answer("У вас нет расходов для удаления")
            return

        expenses = session.query(Expense).filter_by(user_id=user.id).order_by(Expense.date.desc()).limit(10).all()

        if not expenses:
            await message.answer("У вас нет расходов для удаления")
            return

        builder = InlineKeyboardBuilder()
        for expense in expenses:
            builder.button(
                text=f"{expense.date.strftime('%d.%m')} - {expense.category} - {expense.amount} руб.",
                callback_data=f"delete_{expense.id}"
            )
        builder.adjust(1)

        await message.answer(
            "Выберите расход для удаления:",
            reply_markup=builder.as_markup()
        )
    finally:
        session.close()


@router.callback_query(F.data.startswith("delete"))
async def process_delete_expense(callback: CallbackQuery):
    expense_id = int(callback.data.split("_")[1])
    session = get_session()
    try:
        expense = session.query(Expense).filter_by(id=expense_id).first()
        if expense:
            session.delete(expense)
            session.commit()
            await callback.message.edit_text(
                f"✅ Расход удален:\n"
                f"Дата: {expense.date.strftime('%d.%m.%Y')}\n"
                f"Категория: {expense.category}\n"
                f"Сумма: {expense.amount} руб."
            )
        else:
            await callback.answer("Расход не найден")
    except Exception as e:
        await callback.answer("Ошибка при удалении")
        print(f"Delete error: {e}")
    finally:
        session.close()
        await callback.answer()
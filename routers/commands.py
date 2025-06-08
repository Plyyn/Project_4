from keyboards.inline import get_main_menu_keyboard
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from keyboards.inline import get_main_menu_keyboard
from states.expense_states import ExpenseStates
from states.budget_states import BudgetStates
from states.currency_states import CurrencyStates
from services.database import get_session, User, Expense
from routers.handlers.stats_handlers import cmd_stats
from aiogram.types import ReplyKeyboardRemove
from config.settings import ADMIN_IDS
from keyboards.inline import get_admin_keyboard



router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Добро пожаловать в финансовый трекер!\n"
        "Я помогу вам отслеживать ваши расходы и управлять бюджетом.",
        reply_markup=get_main_menu_keyboard()
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    help_text = (
        "📌 Доступные команды:\n"
        "/start - начать работу с ботом\n"
        "/add - добавить новый расход\n"
        "/stats - посмотреть статистику расходов\n"
        "/delete_expense - удалить расход\n"
        "/budget - установить бюджет\n"
        "/convert - конвертировать валюту\n"
        "/help - показать это сообщение"
    )
    await message.answer(help_text, reply_markup=ReplyKeyboardRemove())

@router.callback_query(F.data == "help")
async def show_help(callback: CallbackQuery):
    help_text = (
        "📌 Доступные команды:\n"
        "/add - добавить расход\n"
        "/stats - просмотреть статистику\n"
        "/budget - установить бюджет\n"
        "/remaining - оставшийся бюджет\n"
        "/delete - удалить расход\n" 
        "/convert - конвертировать валюту\n\n"
        "Для админов:\n"
        "/stats_all - статистика по всем пользователям\n"
        "/broadcast - рассылка сообщений"
    )
    await callback.message.answer(help_text)
    await callback.answer()


@router.callback_query(F.data == "add_expense")
async def add_expense_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите сумму расхода:")
    await state.set_state(ExpenseStates.waiting_for_amount)
    await callback.answer()

@router.callback_query(F.data == "show_stats")
async def show_stats_callback(callback: CallbackQuery):
    await cmd_stats(callback.message)
    await callback.answer()

@router.callback_query(F.data == "set_budget")
async def set_budget_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите сумму вашего бюджета:")
    await state.set_state(BudgetStates.waiting_for_amount)
    await callback.answer()

@router.callback_query(F.data == "remaining_budget")
async def remaining_budget_callback(callback: CallbackQuery):
    session = get_session()
    try:
        user = session.query(User).filter_by(telegram_id=callback.from_user.id).first()
        if user and user.budget > 0:
            expenses = session.query(Expense).filter_by(user_id=user.id).all()
            total = sum(exp.amount for exp in expenses)
            remaining = user.budget - total
            await callback.message.answer(f"🔄 Остаток бюджета: {remaining:.2f} руб.")
        else:
            await callback.message.answer("Бюджет не установлен. Используйте /budget")
    finally:
        session.close()
    await callback.answer()

@router.callback_query(F.data == "convert")
async def currency_convert_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите сумму для конвертации:")
    await state.set_state(CurrencyStates.waiting_for_amount)
    await callback.answer()



@router.message(BudgetStates.waiting_for_amount, F.text.regexp(r'^\d+(\.\d+)?$'))
async def process_budget_amount(message: Message, state: FSMContext):
    amount = float(message.text)
    if amount <= 0:
        await message.answer("Бюджет должен быть положительным числом")
        return
    session = get_session()
    try:
        user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
        if not user:
            user = User(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name
            )
            session.add(user)

        user.budget = amount
        session.commit()

        await message.answer(
            f"✅ Бюджет установлен: {amount} руб.\n"
            f"Теперь вы можете отслеживать свои расходы относительно этого бюджета.",
            reply_markup=get_main_menu_keyboard()
        )
    except Exception as e:
        await message.answer("⚠️ Произошла ошибка при сохранении бюджета")
        print(f"Budget save error: {e}")
    finally:
        session.close()
        await state.clear()

@router.message(Command("admin"))
async def admin_panel(message: Message):
    await message.answer(
        "Панель администратора:",
        reply_markup=get_admin_keyboard()  # Ваша клавиатура
    )

@router.message(Command("check_admin"))
async def check_admin(message: Message):
    is_admin = message.from_user.id in ADMIN_IDS
    await message.answer(f"Вы администратор: {is_admin}\nADMIN_IDS: {ADMIN_IDS}")
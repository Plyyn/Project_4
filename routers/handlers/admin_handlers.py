from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from filters.admin_filter import admin_filter
from services.database import get_session, User, Expense
from keyboards.inline import get_admin_keyboard
import logging

logger = logging.getLogger(__name__)
router = Router()
router.message.filter(admin_filter)
router.callback_query.filter(admin_filter)  # Фильтр для callback-кнопок

@router.message(Command("admin"))
async def admin_panel(message: Message):
    logger.info(f"Admin access by {message.from_user.id}")
    await message.answer(
        "Панель администратора:",
        reply_markup=get_admin_keyboard()
    )

@router.message(Command("stats_all"))
async def cmd_stats_all(message: Message):
    session = get_session()
    try:
        users = session.query(User).all()
        total_users = len(users)
        total_expenses = sum(exp.amount for exp in session.query(Expense).all())

        await message.answer(
            "📊 Статистика по всем пользователям:\n"
            f"👥 Пользователей: {total_users}\n"
            f"💸 Всего расходов: {total_expenses} руб."
        )
    finally:
        session.close()

@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message, state: FSMContext):
    if len(message.text.split()) > 1:
        text = ' '.join(message.text.split()[1:])
        session = get_session()
        try:
            users = session.query(User).all()
            for user in users:
                try:
                    await message.bot.send_message(user.telegram_id, text)
                except Exception as e:
                    logger.error(f"Failed to send to {user.telegram_id}: {e}")
            await message.answer(f"Рассылка завершена. Отправлено {len(users)} сообщений")
        finally:
            session.close()
    else:
        await message.answer("Использование: /broadcast <текст>")
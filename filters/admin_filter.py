from aiogram import F
from aiogram.types import Message, CallbackQuery
from config.settings import ADMIN_IDS

class AdminFilter:
    @staticmethod
    def check(message: Message | CallbackQuery) -> bool:
        try:
            user_id = message.from_user.id if isinstance(message, Message) else callback.from_user.id
            return user_id in ADMIN_IDS
        except Exception as e:
            print(f"Admin filter error: {e}")
            return False

admin_filter = F(AdminFilter.check)
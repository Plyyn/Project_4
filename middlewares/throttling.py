from aiogram import types
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from datetime import datetime, timedelta
from typing import Dict, Any, Union


class ThrottlingMiddleware(BaseMiddleware):
    THROTTLE_MESSAGE = "⏳ Пожалуйста, не так быстро! Подождите пару секунд."

    def __init__(self):
        self.user_timeouts: Dict[int, datetime] = {}
        self.timeout = timedelta(seconds=2)
        self.cleanup_interval = timedelta(minutes=30)
        self.last_cleanup = datetime.now()

    async def _cleanup_old_entries(self):
        now = datetime.now()
        if now - self.last_cleanup >= self.cleanup_interval:
            self.user_timeouts = {
                uid: time for uid, time in self.user_timeouts.items()
                if now - time < self.cleanup_interval
            }
            self.last_cleanup = now

    async def __call__(
            self,
            handler,
            event: Union[types.Message, types.CallbackQuery],
            data: Dict[str, Any]
    ):
        await self._cleanup_old_entries()

        user_id = event.from_user.id
        current_time = datetime.now()

        if user_id in self.user_timeouts:
            last_message_time = self.user_timeouts[user_id]
            if current_time - last_message_time < self.timeout:
                if isinstance(event, types.Message):
                    await event.answer(self.THROTTLE_MESSAGE)
                return

        self.user_timeouts[user_id] = current_time
        return await handler(event, data)
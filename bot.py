import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config.settings import BOT_TOKEN
from routers.handlers.expense_handlers import router as expense_router
from routers.handlers.stats_handlers import router as stats_router
from routers.handlers.admin_handlers import router as admin_router
from middlewares.throttling import ThrottlingMiddleware
from utils.logger import setup_logger
from routers.commands import router as commands_router


async def main():
    setup_logger()
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    # Регистрация middleware
    dp.message.middleware(ThrottlingMiddleware())

    # Регистрация роутеров
    dp.include_router(commands_router)
    dp.include_router(expense_router)
    dp.include_router(stats_router)
    dp.include_router(admin_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")
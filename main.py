from aiogram import Bot, Dispatcher
import asyncio
from config import API_TOKEN
from database import init_db
from handlers import register_handlers

async def main():
    bot = Bot(token=API_TOKEN, parse_mode="HTML")
    dp = Dispatcher()
    init_db()
    register_handlers(dp, bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

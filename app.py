import asyncio
from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from db.repo import init_db
from handlers import router as main_router


async def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is empty. Put BOT_TOKEN into .env")

    await init_db()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(main_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

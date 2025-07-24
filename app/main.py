import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import Redis, RedisStorage
from aiogram.types import BotCommand

from app.config import s
from app.handlers import router


# --- Set up logging ---
async def set_commands(bot):
    commands = [
        BotCommand(command="start", description="Start the bot"),
        BotCommand(command="help", description="Get help"),
        BotCommand(command="info", description="Get information about the bot"),
        BotCommand(command="cancel", description="Cancel current operation"),
    ]
    await bot.set_my_commands(commands)


# --- Initialize Redis storage ---
redis = Redis.from_url(s.redis_url)
storage = RedisStorage(redis=redis)


# --- Initialize bot and dispatcher ---
bot = Bot(token=s.telegram_bot_token)
dp = Dispatcher(storage=storage)


# --- Main function to start the bot ---
async def main():
    dp.include_router(router)
    await set_commands(bot)
    # Register handlers
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped")

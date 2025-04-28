import asyncio

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message, BotCommand
from aiogram.utils.callback_answer import CallbackAnswerMiddleware
from loguru import logger

from config import config
from handlers import router as handlers_router

from utils.logger import setup_logging, log_user_action

setup_logging()

@log_user_action('/start')
async def start_handler(message: Message):
    await message.answer('Пришли ссылку')


async def main():
    logger.info("Бот запускается...")
    bot = Bot(token=config.token)
    dp = Dispatcher()
    dp.callback_query.middleware(CallbackAnswerMiddleware())
    dp.include_router(handlers_router)
    await bot.set_my_commands([
        BotCommand(command='start', description='Начать работу'),
        BotCommand(command='help', description='Помощь'),
    ])
    dp.message.register(start_handler, CommandStart())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

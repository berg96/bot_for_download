import asyncio
import os
import re
from contextlib import asynccontextmanager

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile
from loguru import logger

from utils.download import download_video_and_get_description
from utils.logger import LOG_WITH_USER

URL_RE = re.compile(
    r'^(https?://)'
    r'([A-Za-z0-9-]+\.)+'
    r'[A-Za-z]{2,}'
    r'(/[^\s]*)?$'
)

router = Router()


async def animate_text(message: Message, stop_event: asyncio.Event, text: str):
    """Анимация сообщения с изменением точек."""
    dots = ['', '.', '..', '...']
    while not stop_event.is_set():
        for dot in dots:
            if stop_event.is_set():
                break
            try:
                await message.edit_text(f'{text}{dot}')
                await asyncio.sleep(0.5)
            except Exception:
                return

@asynccontextmanager
async def animated_message(message: Message, initial_text: str):
    """Контекстный менеджер для анимации."""
    stop_event = asyncio.Event()
    task = asyncio.create_task(animate_text(message, stop_event, initial_text))
    try:
        yield
    finally:
        stop_event.set()
        await task


async def log_action(user, action):
    logger.info(
        LOG_WITH_USER.format(
            user.full_name,
            user.id,
            user.username,
            action
        )
    )

@router.message(F.text.regexp(URL_RE))
async def handler_download_link(message: Message, state: FSMContext):
    url = message.text.strip()
    user = message.from_user
    os.makedirs('./downloads', exist_ok=True)
    answer_message = await message.answer('⏳ З')
    await log_action(user, f'Подготовка к загрузке с URL {url}')
    try:
        async with animated_message(answer_message, '⏳ Загрузка'):
            description, file_path = await download_video_and_get_description(url)
        if not os.path.exists(file_path):
            await answer_message.edit_text('❌ Не удалось найти скачанный файл.')
            await state.clear()
            return
        video = FSInputFile(file_path)
        await answer_message.edit_text('📦 Отправка')
        await log_action(user, f'Отправляю файл {os.path.basename(file_path)}')
        async with animated_message(answer_message, '📦 Отправка файла'):
            await message.answer_video(video, caption=description)
        os.remove(file_path)
        await log_action(user, 'Файл успешно отправлен!')
        await answer_message.delete()
    except Exception as e:
        await answer_message.edit_text(f'❌ Ошибка: {e}')
    finally:
        await state.clear()


@router.message(~F.text.regexp(URL_RE))
async def ask_for_link(message: Message):
    await message.answer(
        '❌ Пожалуйста, пришлите корректную ссылку, '
        'начинающуюся с http:// или https://'
    )

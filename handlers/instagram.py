import asyncio
import os

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message, FSInputFile

from keyboards.menu import MenuCB, main_keyboard_menu
from utils.download import download_video_and_description
from utils.logger import log_user_action

router = Router()


@router.message(Command("menu"))
async def menu_handler(message: Message):
    await message.answer("Выберите действие:", reply_markup=main_keyboard_menu())

class InstagramDownload(StatesGroup):
    waiting_for_link = State()

@router.callback_query(MenuCB.filter(F.action == 'instagram'))
@router.message(F.text =='📷 Instagram')
@log_user_action('instagram')
async def handler_instagram(query: CallbackQuery, state: FSMContext):
    await query.message.answer(
        'Пожалуйста, пришлите ссылку на видео с Instagram 📷'
    )
    await state.set_state(InstagramDownload.waiting_for_link)


async def animate_loading(message: Message, stop_event: asyncio.Event):
    """Анимация загрузки с точками."""
    dots = ['', '.', '..', '...']
    while not stop_event.is_set():
        for dot in dots:
            if stop_event.is_set():
                break
            try:
                await message.edit_text(f'⏳ Загрузка{dot}')
                await asyncio.sleep(0.5)
            except Exception:
                return


@router.message(InstagramDownload.waiting_for_link)
async def handler_instagram_link(message: Message, state: FSMContext):
    url = message.text.strip()
    os.makedirs('./downloads', exist_ok=True)
    loading_message = await message.answer('⏳ Подготовка к загрузке...')
    stop_event = asyncio.Event()
    loading_task = asyncio.create_task(animate_loading(loading_message, stop_event))
    try:
        description = await download_video_and_description(url)
        files = os.listdir('./downloads')
        if not files:
            stop_event.set()
            await loading_task
            await loading_message.edit_text('❌ Не удалось найти скачанный файл.')
            await state.clear()
            return
        file_path = os.path.join('./downloads', files[0])
        video = FSInputFile(file_path)
        stop_event.set()
        await loading_task
        await loading_message.edit_text('📦 Отправляю файл...')
        await message.answer_video(video, caption=description)
        os.remove(file_path)
        await loading_message.edit_text('✅ Файл успешно отправлен!')
    except Exception as e:
        stop_event.set()
        await loading_task
        await loading_message.edit_text(f'❌ Ошибка при скачивании: {e}')
    await state.clear()

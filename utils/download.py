import asyncio

import yt_dlp
from aiogram import types


async def update_message(queue: asyncio.Queue, message: types.Message):
    while True:
        status = await queue.get()
        if status == 'done':
            await message.edit_text("✅ Загрузка завершена!")
            break
        await message.edit_text(status)


async def progress_hook(d, queue: asyncio.Queue):
    if d['status'] == 'downloading':
        percent = d['_percent_str']
        eta = d.get('eta', 'N/A')
        speed = d.get('speed', 'N/A')
        await queue.put(f"Загрузка: {percent}\nОставшееся время: {eta} сек\nСкорость: {speed}")
    elif d['status'] == 'finished':
        await queue.put(f"Загрузка завершена: {d['filename']}")
        await queue.put('done')
    elif d['status'] == 'error':
        await queue.put(f"Ошибка загрузки: {d.get('error', 'Неизвестная ошибка')}")
        await queue.put('done')


async def download_video_and_description(url):
    # queue = asyncio.Queue()
    # asyncio.create_task(update_message(queue, message))

    ydl_opts = {
        'outtmpl': './downloads/%(id)s.%(ext)s',
        'merge_output_format': 'mp4',
        'format': 'best',
        # 'progress_hooks': [lambda d: asyncio.create_task(progress_hook(d, queue))],
    }

    def sync_download():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            return info_dict.get('description', '')

    return await asyncio.to_thread(sync_download)
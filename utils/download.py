import asyncio
import os

import yt_dlp


async def download_video_and_get_description(url):
    ydl_opts = {
        'outtmpl': './downloads/%(id)s.%(ext)s',
        'merge_output_format': 'mp4',
        'format': 'best',
    }

    def sync_download():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            return (
                info_dict.get('description', ''),
                os.path.abspath(
                    os.path.join(
                        './downloads',
                        f'{info_dict.get('id', 'unknown')}.'
                        f'{info_dict.get('ext', 'mp4')}'
                    )
                )
            )

    return await asyncio.to_thread(sync_download)
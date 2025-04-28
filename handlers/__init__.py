from aiogram import Router

from .download import router as download_router

router = Router()
router.include_router(
    download_router
)

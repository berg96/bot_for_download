from aiogram import Router

from .instagram import router as instagram_router

router = Router()
router.include_router(
    instagram_router
)

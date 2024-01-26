import structlog
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from src.config import StorageType, TelegramConfig
from src.presentation.telegram.routes.handlers import router

logger = structlog.get_logger(__name__)


async def setup_dispatcher(config: TelegramConfig) -> tuple[Bot, Dispatcher]:
    storage = MemoryStorage()
    if config.storage == StorageType.redis:
        redis = Redis(**config.storage_args)
        storage = RedisStorage(redis)

    dp = Dispatcher(storage=storage)
    dp.include_router(router)

    bot = Bot(config.token)

    await bot.delete_webhook(drop_pending_updates=True)
    if await bot.set_webhook(f"{config.webhook_base}/api/{bot.token}"):
        await logger.ainfo(
            "Bot started on hook: %s", f"{config.webhook_base}/api/{bot.token}"
        )

    return bot, dp

# bot/handlers.py
import logging

from vkbottle.bot import Bot, Message

from bot.config import MAX_VIDEO_DURATION, MAX_VOICE_DURATION, WARNING_TTL
from bot.services.guards.guard_manager import GuardManager
from bot.services.guards.video_guard import VideoGuard
from bot.services.guards.voice_guard import VoiceGuard
from bot.services.message_service import VKMessageService
from bot.services.user_service import VKUserService

logger = logging.getLogger(__name__)


def register_handlers(bot: Bot) -> None:
    message_service = VKMessageService(bot.api, warning_ttl=WARNING_TTL)
    user_service = VKUserService(bot.api)

    manager = GuardManager(guards=[
        VoiceGuard(MAX_VOICE_DURATION, message_service, user_service),
        VideoGuard(MAX_VIDEO_DURATION, message_service, user_service),
    ])

    @bot.on.chat_message()
    async def handle_chat_message(message: Message) -> None:
        await manager.handle(message)
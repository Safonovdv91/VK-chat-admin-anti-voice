import logging

from vkbottle.bot import Bot, Message

from bot.config import MAX_VOICE_DURATION
from bot.services.message_service import VKMessageService
from bot.services.user_service import VKUserService
from bot.services.voice_guard import VoiceGuard

logger = logging.getLogger(__name__)


def register_handlers(bot: Bot) -> None:
    voice_guard = VoiceGuard(
        max_duration=MAX_VOICE_DURATION,
        message_service=VKMessageService(bot.api),
        user_service=VKUserService(bot.api),
    )

    @bot.on.chat_message()
    async def handle_chat_message(message: Message) -> None:
        await voice_guard.handle(message)
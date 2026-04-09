# bot/services/guards/voice_guard.py
import logging

from vkbottle.bot import Message

from bot.services.guards.base import BaseGuard

logger = logging.getLogger(__name__)


class VoiceGuard(BaseGuard):
    def __init__(self, max_duration: int, message_service, user_service) -> None:
        super().__init__(message_service, user_service)
        self._max_duration = max_duration

    def _is_long_voice(self, attachments: list) -> bool:
        return any(
            att.type.value == "audio_message"
            and att.audio_message.duration > self._max_duration
            for att in attachments
        )

    def _is_forwarded_voice(self, attachments: list) -> bool:
        return any(att.type.value == "audio_message" for att in attachments)

    def _has_violation(self, message: Message) -> tuple[bool, str]:
        if message.attachments and self._is_long_voice(message.attachments):
            return True, f"голосовые длиннее {self._max_duration}с запрещены"

        if message.fwd_messages:
            for fwd in message.fwd_messages:
                if fwd.attachments and self._is_forwarded_voice(fwd.attachments):
                    return True, "пересылка голосовых сообщений запрещена"

        return False, ""
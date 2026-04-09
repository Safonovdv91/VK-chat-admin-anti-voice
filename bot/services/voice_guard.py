# bot/services/voice_guard.py
import logging

from vkbottle.bot import Message

from bot.services.message_service import MessageServiceProtocol
from bot.services.user_service import UserServiceProtocol

logger = logging.getLogger(__name__)


class VoiceGuard:
    def __init__(
        self,
        max_duration: int,
        message_service: MessageServiceProtocol,
        user_service: UserServiceProtocol,
    ) -> None:
        self._max_duration = max_duration
        self._message_service = message_service
        self._user_service = user_service

    def _is_long_voice(self, attachments: list) -> bool:
        return any(
            att.type.value == "audio_message"
            and att.audio_message.duration > self._max_duration
            for att in attachments
        )

    def _is_forwarded_voice(self, attachments: list) -> bool:
        return any(
            att.type.value == "audio_message"
            for att in attachments
        )
    def _has_violation(self, message: Message) -> tuple[bool, str]:
        # Проверяем прямое голосовое > лимита
        if message.attachments and self._is_long_voice(message.attachments):
            return True, f"голосовые длиннее {self._max_duration}с запрещены"

        # Проверяем пересланные сообщения
        if message.fwd_messages:
            for fwd in message.fwd_messages:
                if fwd.attachments and self._is_forwarded_voice(fwd.attachments):
                    return True, "пересылка голосовых сообщений ТЕМ БОЛЕЕ запрещена"

        return False, ""
    

    async def handle(self, message: Message) -> None:
        violated, reason = self._has_violation(message)

        if not violated:
            logger.debug("Сообщение прошло проверку")
            return

        logger.warning(
            f"Нарушение ({reason}) "
            f"от user_id={message.from_id} в peer_id={message.peer_id}"
        )

        deleted = await self._message_service.delete(
            cmid=message.conversation_message_id,
            peer_id=message.peer_id,
        )
        if not deleted:
            return

        first_name = await self._user_service.get_first_name(message.from_id)
        await self._message_service.send(
            peer_id=message.peer_id,
            text=f"🚫 {first_name}, {reason}!",
        )
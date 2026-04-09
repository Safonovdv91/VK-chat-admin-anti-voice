# bot/services/guards/video_guard.py
import logging

from vkbottle.bot import Message

from bot.services.guards.base import BaseGuard

logger = logging.getLogger(__name__)


class VideoGuard(BaseGuard):
    def __init__(self, max_duration: int, message_service, user_service) -> None:
        super().__init__(message_service, user_service)
        self._max_duration = max_duration

    def _is_video_message(self, att) -> bool:
        """Кружочек может прийти как тип 'video' с подтипом video_message"""
        if att.type.value == "video_message":
            return True
        # VK иногда присылает кружочки как обычное видео с type внутри
        if att.type.value == "video" and att.video is not None:
            return getattr(att.video, "type", None) == "video_message"
        return False

    def _get_duration(self, att) -> int:
        """Получаем длительность из нужного поля в зависимости от типа"""
        if att.type.value == "video_message":
            return att.video_message.duration
        if att.type.value == "video":
            return getattr(att.video, "duration", 0)
        return 0

    def _is_long_video(self, attachments: list) -> bool:
        return any(
            self._is_video_message(att)
            and self._get_duration(att) > self._max_duration
            for att in attachments
        )

    def _is_forwarded_video(self, attachments: list) -> bool:
        return any(self._is_video_message(att) for att in attachments)

    def _has_violation(self, message: Message) -> tuple[bool, str]:
        if message.attachments and self._is_long_video(message.attachments):
            return True, f"кружочки длиннее {self._max_duration}с запрещены"

        if message.fwd_messages:
            for fwd in message.fwd_messages:
                if fwd.attachments and self._is_forwarded_video(fwd.attachments):
                    return True, "пересылка кружочков запрещена"

        return False, ""
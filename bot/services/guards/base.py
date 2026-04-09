# bot/services/guards/base.py
from abc import ABC, abstractmethod

from vkbottle.bot import Message


class BaseGuard(ABC):
    def __init__(
        self,
        message_service,
        user_service,
    ) -> None:
        self._message_service = message_service
        self._user_service = user_service

    @abstractmethod
    def _has_violation(self, message: Message) -> tuple[bool, str]:
        """Возвращает (нарушение, причина)"""
        ...

    async def handle(self, message: Message) -> bool:
        """Возвращает True если нарушение найдено и сообщение удалено"""
        violated, reason = self._has_violation(message)
        if not violated:
            return False

        deleted = await self._message_service.delete(
            cmid=message.conversation_message_id,
            peer_id=message.peer_id,
        )
        if not deleted:
            return False

        first_name = await self._user_service.get_first_name(message.from_id)
        await self._message_service.send(
            peer_id=message.peer_id,
            text=f"🚫 {first_name}, {reason}!",
        )
        return True
import logging
from typing import Protocol

import vkbottle
from vkbottle.api import API

logger = logging.getLogger(__name__)


class MessageServiceProtocol(Protocol):
    async def delete(self, cmid: int, peer_id: int) -> bool: ...
    async def send(self, peer_id: int, text: str) -> None: ...


class VKMessageService:
    def __init__(self, api: API) -> None:
        self._api = api

    async def delete(self, cmid: int, peer_id: int) -> bool:
        try:
            await self._api.messages.delete(
                cmids=[cmid],
                peer_id=peer_id,
                delete_for_all=True,
            )
            logger.info(f"Сообщение cmid={cmid} удалено из peer_id={peer_id}")
            return True
        except vkbottle.VKAPIError as e:
            logger.error(f"Не удалось удалить сообщение cmid={cmid}: {e}")
            return False

    async def send(self, peer_id: int, text: str) -> None:
        try:
            await self._api.messages.send(
                peer_id=peer_id,
                message=text,
                random_id=0,
            )
        except vkbottle.VKAPIError as e:
            logger.error(f"Не удалось отправить сообщение в peer_id={peer_id}: {e}")
# bot/services/message_service.py
import asyncio
import logging
from typing import Protocol

import vkbottle
from vkbottle.api import API

logger = logging.getLogger(__name__)


class MessageServiceProtocol(Protocol):
    async def delete(self, cmid: int, peer_id: int) -> bool: ...
    async def send(self, peer_id: int, text: str) -> None: ...


class VKMessageService:
    def __init__(self, api: API, warning_ttl: int = 5) -> None:
        self._api = api
        self._warning_ttl = warning_ttl

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

    async def _delete_after_ttl(self, cmid: int, peer_id: int) -> None:
        await asyncio.sleep(self._warning_ttl)
        logger.debug(f"TTL истёк, удаляем предупреждение cmid={cmid}")
        await self.delete(cmid=cmid, peer_id=peer_id)

    async def send(self, peer_id: int, text: str) -> None:
        try:
            # peer_ids (множественное) возвращает список объектов с conversation_message_id
            response = await self._api.request(
                "messages.send",
                {
                    "peer_ids": peer_id,
                    "message": text,
                    "random_id": 0,
                }
            )
            logger.debug(f"messages.send (peer_ids) сырой ответ: {response!r}")

            cmid = None
            items = response if isinstance(response, list) else response.get("response", [])
            if isinstance(items, list) and items:
                cmid = items[0].get("conversation_message_id")

            if not cmid:
                logger.warning(f"Не удалось извлечь cmid: {response!r}")
                return

            logger.info(f"Предупреждение отправлено в peer_id={peer_id}, cmid={cmid}")
            asyncio.create_task(self._delete_after_ttl(cmid=cmid, peer_id=peer_id))

        except vkbottle.VKAPIError as e:
            logger.error(f"Не удалось отправить сообщение в peer_id={peer_id}: {e}")
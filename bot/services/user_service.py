import logging
from typing import Protocol

import vkbottle
from vkbottle.api import API

logger = logging.getLogger(__name__)


class UserServiceProtocol(Protocol):
    async def get_first_name(self, user_id: int) -> str: ...


class VKUserService:
    def __init__(self, api: API) -> None:
        self._api = api

    async def get_first_name(self, user_id: int) -> str:
        try:
            users = await self._api.users.get(user_ids=[user_id])
            return users[0].first_name if users else "Пользователь"
        except vkbottle.VKAPIError as e:
            logger.error(f"Не удалось получить данные пользователя {user_id}: {e}")
            return "Пользователь"
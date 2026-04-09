import logging

from vkbottle.bot import Message

from bot.services.guards.base import BaseGuard

logger = logging.getLogger(__name__)


class GuardManager:
    def __init__(self, guards: list[BaseGuard]) -> None:
        self._guards = guards

    async def handle(self, message: Message) -> None:
        for guard in self._guards:
            # Если одним guard'ом нарушение уже обработано — дальше не идём
            if await guard.handle(message):
                logger.warning(
                    f"{guard.__class__.__name__} сработал "
                    f"для user_id={message.from_id}"
                )
                return
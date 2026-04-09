import logging
import os

from dotenv import load_dotenv
from vkbottle.bot import Bot

from bot.handlers import register_handlers
from bot.logger import setup_logger

load_dotenv()
setup_logger()
logger = logging.getLogger(__name__)


def create_bot() -> Bot:
    logger.info("Создаем бота")
    token = os.getenv("VK_TOKEN")
    if not token:
        raise ValueError("VK_TOKEN не найден в .env файле")
    return Bot(token=token)


if __name__ == "__main__":
    logger.info("Запуск программы")
    bot = create_bot()
    register_handlers(bot)
    logger.info("Бот успешно запущен")
    bot.run_forever()
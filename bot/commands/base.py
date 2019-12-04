import logging

from telegram.ext import CommandHandler

from bot.core import BotTelegramCore
from bot.messages import START, HELP


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)


def config_handlers(instance: BotTelegramCore):
    logger.info('Setting base commands...')

    instance.add_handler(
        CommandHandler("start",
                       lambda update, context: update.message.reply_text(START)))

    instance.add_handler(
        CommandHandler("help",
                       lambda update, context: update.message.reply_text(HELP)))

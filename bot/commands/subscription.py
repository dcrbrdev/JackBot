import logging

from telegram.ext import CommandHandler

from bot.core import BotTelegramCore


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)


def subscribe(update, context):
    pass


def subscriptions(update, context):
    pass


def unsubscribe(update, context):
    pass


def config_handlers(instance: BotTelegramCore):
    logger.info('Setting subscription commands...')

    instance.add_handler(CommandHandler("subscribe", subscribe))
    instance.add_handler(CommandHandler("subscriptions", subscriptions))
    instance.add_handler(CommandHandler("subscriptions", unsubscribe))

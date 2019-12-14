import logging

from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

from bot.core import BotTelegramCore
from bot.utils import convert_dcr


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)


def dcr(update: Update, context: CallbackContext):
    try:
        target_coin = context.args[0]
    except TypeError:
        target_coin = 'USD'

    try:
        dcr_amount = context.args[1]
    except TypeError:
        dcr_amount = 1

    target_value = convert_dcr(dcr_amount, target_coin)

    update.effective_message.reply_text(target_value)


def config_handlers(instance: BotTelegramCore):
    logger.info('Setting exchange commands...')



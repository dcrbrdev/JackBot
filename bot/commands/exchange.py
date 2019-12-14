import logging

from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

from bot.core import BotTelegramCore
from bot.utils import convert_dcr
from bot.exceptions import DcrDataAPIError, ExchangeAPIError


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

    try:
        target_value = convert_dcr(dcr_amount, target_currency)
    except ExchangeAPIError as e:
        update.effective_message.reply_text(f"{e}")
        return
    except DcrDataAPIError as e:
        update.effective_message.reply_text("Error requests data from DCRData API.\n"
                                            "Please contact my managers!")
        update.effective_message.reply_text(f"{e}")
        return

    message = f"{dcr_amount} DCR => {target_value:.2f} {target_currency}"

    update.effective_message.reply_text(message)


def config_handlers(instance: BotTelegramCore):
    logger.info('Setting exchange commands...')

    instance.add_handler(CommandHandler("dcr", dcr))

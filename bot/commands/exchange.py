import logging

from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

from bot.core import BotTelegramCore
from bot.utils import convert_dcr
from bot.exceptions import DcrDataAPIError


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)


def dcr(update: Update, context: CallbackContext):
    target_currency = None
    dcr_amount = None

    try:
        dcr_amount = float(context.args[0])
    except ValueError:
        target_currency = context.args[0].upper()
    except IndexError:
        dcr_amount = 1
        target_currency = "USD"

    try:
        dcr_amount = float(context.args[1])
    except ValueError:
        target_currency = context.args[1].upper()
    except IndexError:
        if target_currency is None:
            target_currency = "USD"
        if dcr_amount is None:
            dcr_amount = 1

    try:
        target_value = convert_dcr(dcr_amount, target_currency)
    except DcrDataAPIError as e:
        update.effective_message.reply_text("Error requests data from "
                                            "DCRData API.\n "
                                            "Please contact my managers!")
        update.effective_message.reply_text(f"{e}")
        return

    message = f"{dcr_amount} DCR => {target_value:.2f} {target_currency}"

    update.effective_message.reply_text(message)


def config_handlers(instance: BotTelegramCore):
    logger.info('Setting exchange commands...')

    instance.add_handler(CommandHandler("dcr", dcr))

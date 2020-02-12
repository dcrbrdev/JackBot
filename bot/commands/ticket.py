import logging

from mongoengine.errors import DoesNotExist
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

from bot.core import BotTelegramCore
from bot.messages import GROUP_RESTRICTED, TX_ID_ERROR
from db.observer import UserObserver
from db.ticket import Ticket


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO)

logger = logging.getLogger(__name__)


def add_ticket(update: Update, context: CallbackContext):
    chat = update.effective_chat
    message = update.effective_message

    if chat.type != "private":
        message.reply_text(GROUP_RESTRICTED)
        return

    try:
        observer = UserObserver.objects.get(chat_id=f"{chat.id}")
    except DoesNotExist:
        observer = UserObserver(f"{chat.username}",
                                f"{chat.id}").save()

    try:
        tx_id = context.args[0]
    except IndexError:
        message.reply_text(TX_ID_ERROR)
        return

    try:
        Ticket.objects.get(observer=observer, tx_id=tx_id)
        message.reply_text(f"Ticket with transaction id {tx_id}"
                           f" is already registered!", parse_mode='HTML')
        return
    except DoesNotExist:
        ticket = Ticket(observer, tx_id)

    if ticket.fetch():
        message.reply_text(f"Ticket has been saved!"
                           f"\n\n{ticket.html}", parse_mode='HTML')


def remove_ticket(update: Update, context: CallbackContext):
    chat = update.effective_chat
    message = update.effective_message

    if chat.type != "private":
        message.reply_text(GROUP_RESTRICTED)
        return

    try:
        observer = UserObserver.objects.get(chat_id=f"{chat.id}")
    except DoesNotExist:
        observer = UserObserver(f"{chat.username}",
                                f"{chat.id}").save()

    try:
        tx_id = context.args[0]
    except IndexError:
        message.reply_text(TX_ID_ERROR)
        return

    try:
        ticket = Ticket.objects.get(observer=observer, tx_id=tx_id)
    except DoesNotExist:
        message.reply_text(f"Ticket with transaction id {tx_id} doesn't exist!")
        return

    ticket.delete()
    message.reply_text(f"Ticket {tx_id} has been removed!")


def list_tickets(update: Update, context: CallbackContext):
    chat = update.effective_chat
    message = update.effective_message

    if chat.type != "private":
        message.reply_text(GROUP_RESTRICTED)
        return

    try:
        observer = UserObserver.objects.get(chat_id=f"{chat.id}")
    except DoesNotExist:
        observer = UserObserver(f"{chat.username}",
                                f"{chat.id}").save()

    tickets = Ticket.objects(observer=observer)

    if not tickets:
        message.reply_text("<b>There are no watched tickets!"
                           "</b>", parse_mode='HTML')
        return

    text = "<b>Watched tickets</b>\n\n"
    for index, ticket in enumerate(tickets):
        text += ticket.html
        text += '\n' if index != len(tickets) else ''

    message.reply_text(text, parse_mode='HTML')


def config_handlers(instance: BotTelegramCore):
    logger.info("Setting ticket commands...")

    instance.add_handler(CommandHandler("add_ticket", add_ticket))
    instance.add_handler(CommandHandler("remove_ticket", remove_ticket))
    instance.add_handler(CommandHandler("list_tickets", list_tickets))

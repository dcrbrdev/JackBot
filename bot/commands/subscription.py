import json
import logging

from mongoengine.errors import DoesNotExist
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackContext

from bot.core import BotTelegramCore
from bot.utils import build_menu
from db.subscription import Subject, Observer


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO)

logger = logging.getLogger(__name__)


def subscribe(update: Update, context: CallbackContext):
    chat = update.effective_chat

    try:
        observer = Observer.objects.get(chat_id=f"{chat.id}")
    except DoesNotExist:
        observer = Observer(chat_id=f"{chat.id}",
                            username=f"{chat.username}").save()

    subscribed_subjects = Subject.objects(observers=observer)
    avaliable_subjects = [subject for subject in Subject.objects()
                          if subject not in subscribed_subjects]

    buttons_list = [
        InlineKeyboardButton(
            subject.header,
            callback_data=json.dumps({
                    "type": "subscribe",
                    "id": f"{subject.id}"
                })
         )
        for subject in avaliable_subjects
    ]
    menu = InlineKeyboardMarkup(build_menu(buttons_list, n_cols=1))

    context.bot.send_message(chat.id,
                             "<b>Avaliable subjects</b>",
                             parse_mode='HTML', reply_markup=menu)


def unsubscribe(update: Update, context: CallbackContext):
    chat = update.effective_chat

    observer = Observer.objects.get(chat_id=f"{chat.id}")

    subscribed_subjects = Subject.objects(observers=observer)

    buttons_list = [
        InlineKeyboardButton(
            subject.header,
            callback_data=json.dumps({
                "type": "unsubscribe",
                "id": f"{subject.id}"
            })
        )
        for subject in subscribed_subjects
    ]

    menu = InlineKeyboardMarkup(build_menu(buttons_list, n_cols=1))

    context.bot.send_message(chat.id,
                             "<b>Subscribed subjects</b>",
                             parse_mode='HTML', reply_markup=menu)


def subscriptions(update: Update, context: CallbackContext):
    chat = update.effective_chat

    observer = Observer.objects.get(chat_id=f"{chat.id}")

    subscribed_subjects = Subject.objects(observers=observer)

    text = "<b>Subscribed subjects</b>\n\n"
    for index, subject in enumerate(subscribed_subjects):
        text += '-'
        text += subject.__str__()
        text += '\n' if index != len(subscribed_subjects) else ''

    context.bot.send_message(chat.id, text, parse_mode='HTML')


def config_handlers(instance: BotTelegramCore):
    logger.info("Setting subscription commands...")

    instance.add_handler(CommandHandler("subscribe", subscribe))
    instance.add_handler(CommandHandler("unsubscribe", unsubscribe))
    instance.add_handler(CommandHandler("subscriptions", subscriptions))

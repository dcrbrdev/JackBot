import json
import logging

from telegram import Update
from telegram.ext import CallbackQueryHandler, CallbackContext

from bot.core import BotTelegramCore
from db.subscription import Subject, Observer
from db.exceptions import (ObserverAlreadyRegisteredError,
                           ObserverNotRegisteredError)


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)


def handle_callback(update: Update, context: CallbackContext):
    chat = update.effective_chat

    query = update.callback_query
    data = json.loads(query.data)

    observer = Observer.objects.get(chat_id=f'{chat.id}')

    if data.get('type') in ["subscribe", "unsubscribe"]:
        subject = Subject.objects.get(id=data.get('id'))

        msg = ""
        try:
            if data.get('type') == "subscribe":
                subject.subscribe(observer)
                msg = f"Observer {observer} has been subscribed to {subject}"
            elif data.get('type') == "unsubscribe":
                subject.unsubscribe(observer)
                msg = f"Observer {observer} has been unsubscribed to {subject}"
        except (ObserverNotRegisteredError, ObserverAlreadyRegisteredError) as e:
            msg = f"{e}"

        context.bot.answer_callback_query(
            callback_query_id=query.id,
            text=msg,
            show_alert=True
        )


def config_handlers(instance: BotTelegramCore):
    logging.info('Setting callback handler...')

    instance.add_handler(
        CallbackQueryHandler(handle_callback)
    )

import logging

from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
from mongoengine.errors import DoesNotExist, MultipleObjectsReturned

from bot.core import BotTelegramCore
from bot.messages import NOW_GROUP_RESTRICTED
from db.subject import Subject
from db.observer import UserObserver
from db.update_message import UpdateMessage


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)


def now(update: Update, context: CallbackContext):
    chat = update.effective_chat
    message = update.effective_message

    if not chat.type == "private":
        available_vsps = "\n".join([subject.header for subject in Subject.objects.all()])
        message.reply_text(NOW_GROUP_RESTRICTED, parse_mode='MARKDOWN')
        message.reply_text(f"<b>Available VSP's are:</b>\n\n{available_vsps}", parse_mode='HTML')
        return

    try:
        observer = UserObserver.objects.get(chat_id=f"{chat.id}")
    except DoesNotExist:
        observer = UserObserver(f"{chat.username}",
                                f"{chat.id}").save()

    subject_names = context.args
    subjects = []
    errors = []

    if subject_names:
        for name in subject_names:
            try:
                subject = Subject.objects.get(name__icontains=name)
                subjects.append(subject)
            except DoesNotExist as e:
                errors.append(f"{name}: {e}")
            except MultipleObjectsReturned as e:
                errors.append(f"{e}\n"
                              f"The value {name} returned more than "
                              f"one subject. Please be more specific!")
    else:
        subjects = Subject.objects.all()

    update_messages = []

    for subject in subjects:
        update_messages.append(UpdateMessage.get_last_by_subject(subject))

    if errors:
        error_message = "\n".join(errors)
        message.reply_text(error_message)

    for msg in update_messages:
        observer.notify(msg)


def config_handlers(instance: BotTelegramCore):
    logger.info('Setting subject commands...')

    instance.add_handler(CommandHandler("now", now))

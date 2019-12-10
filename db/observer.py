import logging

from mongoengine import (
    Document, EmbeddedDocument,
    StringField,
    ReferenceField, EmbeddedDocumentListField)

from bot.core import BotTelegramCore


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)


class ObserverMessage(EmbeddedDocument):
    message_id = StringField(required=True)
    subject = ReferenceField('Subject', required=True)


class Observer(Document):
    username = StringField(max_length=50)
    chat_id = StringField(required=True, max_length=50, unique=True)
    messages = EmbeddedDocumentListField(ObserverMessage)

    meta = {
        'indexes': [
            {
                'fields': ['messages.subject'],
                'unique': True
            }
        ]
    }

    def __str__(self):
        return f"{self.username if self.username else ''} " \
               f"{self.chat_id}".strip()

    def notify(self, update_message):
        self._remove_last_message_from_subject(update_message.subject)
        self._send_update_message(update_message)

    def _send_update_message(self, update_message):
        telegram_message = BotTelegramCore.instance().send_message(update_message, chat_id=self.chat_id)
        self.messages.create(telegram_message.message_id, update_message.subject)

    def _remove_last_message_from_subject(self, subject):
        self.messages.get(subject=subject).delete()
        self.save()

import logging

import pendulum
from mongoengine import (
    Document,
    StringField, IntField, ListField, DateTimeField,
    ReferenceField, NULLIFY)
from mongoengine.errors import DoesNotExist
from telegram.error import BadRequest

from bot.core import BotTelegramCore


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)


class ObserverMessage(Document):
    message_id = IntField(required=True)
    subject = ReferenceField('Subject', required=True)
    observer = ReferenceField('Observer', required=True)
    datetime = DateTimeField(default=pendulum.now, required=True)

    meta = {
        'ordering': ['datetime'],
        'indexes': [
            {'fields': ['datetime'], 'expireAfterSeconds': 1*24*60*60}
        ]
    }

    def __str__(self):
        return f"{self.message_id} {self.subject}"


class Observer(Document):
    username = StringField(max_length=50)
    chat_id = StringField(required=True, max_length=50, unique=True)

    meta = {
        'allow_inheritance': True
    }

    def __str__(self):
        return f"{self.username if self.username else ''} " \
               f"{self.chat_id}".strip()

    def notify(self, update_message):
        self.reload()
        self._send_update_message(update_message)

    def _send_update_message(self, update_message):
        telegram_message = BotTelegramCore.send_message(
            f'{update_message}', chat_id=self.chat_id)
        ObserverMessage(
            telegram_message.message_id,
            update_message.subject,
            self
        ).save()

    @classmethod
    def get_official_observer(cls):
        return cls.objects.get(chat_id=BotTelegramCore.instance().chat_id)


class UserObserver(Observer):
    messages = ListField(
        ReferenceField(ObserverMessage, reverse_delete_rule=NULLIFY)
    )

    def notify(self, update_message):
        self.reload()
        self._remove_last_message_from_subject(update_message.subject)
        self._send_update_message(update_message)

    def _send_update_message(self, update_message):
        subject = update_message.subject

        official_observer = Observer.get_official_observer()
        last_official_message = ObserverMessage\
            .objects(subject=subject,
                     observer=official_observer)\
            .order_by('-datetime').first()
        telegram_message = BotTelegramCore.forward_message(
            to_chat_id=self.chat_id,
            from_chat_id=official_observer.chat_id,
            message_id=last_official_message.message_id
        )
        self._create_message(telegram_message.message_id, subject)

    def _remove_last_message_from_subject(self, subject):
        for om in self.messages:
            try:
                if om.subject == subject:
                    BotTelegramCore.delete_message(self.chat_id, om.message_id)
                    self._delete_message(om)
            except (AttributeError, BadRequest):
                self._delete_message(om)

    def _delete_message(self, om: ObserverMessage):
        self.messages.remove(om)
        if isinstance(om, ObserverMessage):
            om.delete()
        self.save()

    def _create_message(self, telegram_message_id, subject):
        om = ObserverMessage(
            telegram_message_id,
            subject,
            self
        ).save()
        self.messages.append(om)
        self.save()

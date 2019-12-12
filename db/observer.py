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
    """MongoDB Document for a observer telegram sent message

    Attributes:
        message_id (int): telegram send message id
        subject (Subject): subject reference
        observer (Observer): observer reference
        datetime: now() datetime
    """
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
    """MongoDB Document for official Telegram Channel

    Attributes:
        username (str): telegram chat username
        chat_id (str): telegram chat id

    """
    username = StringField(max_length=50)
    chat_id = StringField(required=True, max_length=50, unique=True)

    meta = {
        'allow_inheritance': True
    }

    def __str__(self):
        return f"{self.username if self.username else ''} " \
               f"{self.chat_id}".strip()

    def notify(self, update_message):
        """Notify observer of update message.

        Calls:
        >>> self._send_update_message(update_message)

        Args:
            update_message (UpdateMessage): update message to be notified

        """
        self._send_update_message(update_message)

    def _send_update_message(self, update_message):
        """Send update message to telegram chat and creates it's respective ObserverMessage

        Args:
            update_message (UpdateMessage): update message to be sent
        """
        telegram_message = BotTelegramCore.send_message(
            f'{update_message}', chat_id=self.chat_id)
        ObserverMessage(
            telegram_message.message_id,
            update_message.subject,
            self
        ).save()

    @classmethod
    def get_official_observer(cls):
        """get official observer from official chat_id

        Returns:
            Observer: official observer
        """
        return cls.objects.get(chat_id=BotTelegramCore.instance().chat_id)


class UserObserver(Observer):
    """MongoDB Document for user's observer

     Attributes:
        username (str): telegram chat username
        chat_id (str): telegram chat id
        messages (list of ObserverMessage): list of ObserverMessage's
    """
    messages = ListField(
        ReferenceField(ObserverMessage, reverse_delete_rule=NULLIFY)
    )

    def notify(self, update_message):
        """Notify observer of update message.

        Calls:
        >>> self._remove_last_message_from_subject(update_message.subject)
        >>> self._send_update_message(update_message)

        Args:
            update_message (UpdateMessage): update message to be notified

        """
        self._remove_last_message_from_subject(update_message.subject)
        self._send_update_message(update_message)

    def _send_update_message(self, update_message):
        """Forward official channel update message to telegram chat and creates it's respective ObserverMessage

        Args:
            update_message (UpdateMessage): update message to be forwarded
        """
        official_observer = Observer.get_official_observer()
        last_official_message = ObserverMessage\
            .objects(subject=update_message.subject,
                     observer=official_observer)\
            .order_by('-datetime').first()
        telegram_message = BotTelegramCore.forward_message(
            to_chat_id=self.chat_id,
            from_chat_id=official_observer.chat_id,
            message_id=last_official_message.message_id
        )
        om = ObserverMessage(
            telegram_message.message_id,
            update_message.subject,
            self
        ).save()
        self.messages.append(om)
        self.save()

    def _remove_last_message_from_subject(self, subject):
        """Delete previous forwarded official channel update message from subject on telegram chat and removes it's respective ObserverMessage

        Args:
            subject (Subject): subject to be filter messages
        """
        self.reload()
        try:
            observer_messages = filter(
                lambda x: (isinstance(x, ObserverMessage)
                           and x.subject == subject),
                self.messages
            )

            for om in observer_messages:
                BotTelegramCore.delete_message(self.chat_id, om.message_id)

            for om in self.messages:
                self.messages.remove(om)
                om.delete()

            self.save()
        except DoesNotExist:
            pass
        except BadRequest as e:
            logger.warning(f'BadRequest {e}')

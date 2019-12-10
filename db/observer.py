import logging

from mongoengine import (
    Document,
    StringField, IntField, ListField,
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

    def __str__(self):
        return f"{self.message_id} {self.subject}"


class Observer(Document):
    username = StringField(max_length=50)
    chat_id = StringField(required=True, max_length=50, unique=True)
    messages = ListField(
        ReferenceField(ObserverMessage, reverse_delete_rule=NULLIFY)
    )

    def __str__(self):
        return f"{self.username if self.username else ''} " \
               f"{self.chat_id}".strip()

    def notify(self, update_message):
        self.reload()
        self._remove_last_message_from_subject(update_message.subject)
        self._send_update_message(update_message)

    def _send_update_message(self, update_message):
        telegram_message = BotTelegramCore.send_message(
            f'{update_message}', chat_id=self.chat_id)
        om = ObserverMessage(telegram_message.message_id,
                             update_message.subject).save()
        self.messages.append(om)
        self.save()

    def _remove_last_message_from_subject(self, subject):
        self.reload()
        try:
            observer_messages = [om for om in self.messages if
                                 isinstance(om, ObserverMessage) and
                                 om.subject == subject]
            for om in observer_messages:
                BotTelegramCore.delete_message(self.chat_id, om.message_id)
                self.messages.remove(om)
                self.save()
                om.delete()
        except DoesNotExist:
            pass
        except BadRequest as e:
            logger.warning(f'BadRequest {e}')
        except Exception as e:
            logger.error(e)

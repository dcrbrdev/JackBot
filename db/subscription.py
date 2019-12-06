import logging

from mongoengine import (Document, StringField,
                         ListField, ReferenceField, CASCADE)

from bot.core import BotTelegramCore
from db.exceptions import (ObserverNotRegisteredError,
                           ObserverAlreadyRegisteredError)


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)


class Observer(Document):
    username = StringField(max_length=50)
    chat_id = StringField(required=True, max_length=50, unique=True)

    def __str__(self):
        return f"{self.username} {self.chat_id}"

    def notify(self, message):
        BotTelegramCore.instance().send_message(message, chat_id=self.chat_id)


class Subject(Document):
    emoji = StringField(required=True, max_length=2)
    name = StringField(required=True, max_length=55, unique=True)
    url = StringField(required=True, max_length=120, unique=True)

    observers = ListField(
        ReferenceField(Observer, reverse_delete_rule=CASCADE), default=[]
    )

    def __str__(self):
        return f"{self.header} {self.url}"

    @property
    def header(self):
        return f"{self.emoji} {self.name}"

    def subscribe(self, observer: Observer):
        if not isinstance(observer, Observer):
            raise TypeError(f"{observer} is not instance of {Observer}")
        if observer in self.observers:
            raise ObserverAlreadyRegisteredError(f"Observer {observer} "
                                                 f"is already registered!")
        self.observers.append(observer)
        self.save()

    def unsubscribe(self, observer: Observer):
        if not isinstance(observer, Observer):
            raise TypeError(f"{observer} is not instance of {Observer}")
        if observer not in self.observers:
            raise ObserverNotRegisteredError(f"Observer {observer} "
                                             f"is not registered!")
        self.observers.remove(observer)
        self.save()

    def notify(self, message):
        logger.info(f'Notifying observers {self.observers} for {self}')
        for observer in self.observers:
            observer.notify(message)

from mongoengine import Document, StringField, ListField, ReferenceField, CASCADE

from bot.core import BotTelegramCore
from db.exceptions import ObserverNotRegisteredError, ObserverAlreadyRegisteredError


class Observer(Document):
    username = StringField(required=True, max_length=50, unique=True)
    chat_id = StringField(required=True, max_length=50, unique=True)

    def __str__(self):
        return f"{self.username} {self.chat_id}"

    def notify(self, message):
        BotTelegramCore.instance().send_message(message, chat_id=self.chat_id, parse_mode='HTML')


class Subject(Document):
    emoji = StringField(required=True, max_length=5)
    name = StringField(required=True, max_length=55, unique_with='emoji')
    url = StringField(required=True, max_length=120, unique=True)

    observers = ListField(ReferenceField(Observer, reverse_delete_rule=CASCADE), default=[])

    def __str__(self):
        return f"{self.header} {self.url}"

    @property
    def header(self):
        return f"{self.emoji} {self.name}"

    def register(self, observer: Observer):
        if not isinstance(observer, Observer):
            raise TypeError(f"{observer} is not instance of {Observer}")
        if observer in self.observers:
            raise ObserverAlreadyRegisteredError(f"Observer {observer} is already registered!")
        self.observers.append(observer)
        self.save()

    def unregister(self, observer: Observer):
        if not isinstance(observer, Observer):
            raise TypeError(f"{observer} is not instance of {Observer}")
        if observer not in self.observers:
            raise ObserverNotRegisteredError(f"Observer {observer} is not registered!")
        self.observers.remove(observer)
        self.save()

    def notify(self, message):
        for observer in self.observers:
            observer.notify(message)

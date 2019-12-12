import logging

from mongoengine import (
    Document,
    StringField, ListField,
    ReferenceField, NULLIFY)

from db.exceptions import (ObserverNotRegisteredError,
                           ObserverAlreadyRegisteredError)
from db.observer import Observer, UserObserver


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)


class Subject(Document):
    """MongoDB Document for a split ticket VSP

    Attributes:
        emoji (str): A string emoji
        name (str): name of split ticket VSP
        uri (str): websocket URI
        observers (list of UserObserver): observers watching this subject
    """

    emoji = StringField(required=True, max_length=2)
    name = StringField(required=True, max_length=55, unique=True)
    uri = StringField(required=True, max_length=120, unique=True)

    observers = ListField(
        ReferenceField(UserObserver, reverse_delete_rule=NULLIFY), default=[]
    )

    def __str__(self):
        return f"{self.header} {self.uri}"

    @property
    def header(self):
        """str headear for subject

        Returns:
            str: emoji + name
        """
        return f"{self.emoji} {self.name}"

    def subscribe(self, observer):
        """Subscribe a Observer to this subject

        Args:
            observer (Observer): observer to subscribe
        Raises:
            ObserverAlreadyRegisteredError: if observer is already subscribed to subject
        """
        if observer in self.observers:
            raise ObserverAlreadyRegisteredError(f"Observer {observer} "
                                                 f"is already subscribed!")
        self.observers.append(observer)
        self.save()

    def unsubscribe(self, observer):
        """Unsubscribe a Observer to this subject

        Args:
            observer (Observer): observer to unsubscribe
        Raises:
            ObserverNotRegisteredError: if observer is not subscribed
        """
        if observer not in self.observers:
            raise ObserverNotRegisteredError(f"Observer {observer} "
                                             f"is not subscribed!")
        self.observers.remove(observer)
        self.save()

    def notify(self, update_message):
        """Notify official Observer and UserObserver's subscribed of some UpdateMessage

        Args:
            update_message (UpdateMessage): update message to be notified
        """
        official_observer = Observer.get_official_observer()
        logger.info(f'Notifying official observer {official_observer} '
                    f'for {self}')
        official_observer.notify(update_message)
        logger.info(f'Notifying observers {self.observers} for {self}')
        for observer in self.observers:
            observer.notify(update_message)

from json import loads

import pendulum
from mongoengine import (
    Document, EmbeddedDocument,
    IntField, StringField, DateTimeField,
    EmbeddedDocumentListField, ReferenceField)

from db.subject import Subject
from db.ticket import TicketPrice
from utils.exceptions import DuplicatedUpdateMessageError


class Amount(EmbeddedDocument):
    ATOM_DECIMALS = 100000000

    _value = IntField(required=True)

    def __str__(self):
        return f"{self.value} DCR"

    def equal(self, other):
        if not isinstance(other, Amount):
            raise TypeError(f"Other must be {Amount}")
        return self.value == other.value

    @property
    def value(self):
        return self._value/self.ATOM_DECIMALS

    @value.setter
    def value(self, value: int):
        if not isinstance(value, int):
            raise TypeError(f"{value} {type(value)} is not int")
        self._value = value


class Session(EmbeddedDocument):
    hash = StringField(required=True)
    amounts = EmbeddedDocumentListField(Amount, required=True)

    def __str__(self):
        string = f"{self.hash[:32]}:\t["
        total = 0
        for index, amount in enumerate(self.amounts):
            total += amount.value
            string += f"{amount}"
            string += ", " if index != len(self.amounts)-1 else "]"
        string += f"\nTotal: {total} DCR"
        return string

    def equal(self, other):
        if not isinstance(other, Session):
            raise TypeError(f"Other must be {Session}")

        return self.tuple == other.tuple

    @property
    def tuple(self):
        return self.hash, [amount.value for amount in self.amounts]

    @classmethod
    def from_data(cls, data):
        instance = cls(data.get('name'))
        for amount in data.get('amounts'):
            instance.amounts.append(Amount(amount))
        return instance


class UpdateMessage(Document):
    subject = ReferenceField(Subject, required=True)
    sessions = EmbeddedDocumentListField(Session)
    datetime = DateTimeField(default=pendulum.now, required=True)

    meta = {
        'ordering': ['datetime'],
        'indexes': [
            {'fields': ['datetime'], 'expireAfterSeconds': 31 * 24 * 60 * 60}
        ]
    }

    def __str__(self):
        string = f"<b>{self.subject.header}</b>\n\n"
        string += f"<i>Default session: {self.subject.default_session}</i>\n\n"
        string += f"Ticket price: {TicketPrice.get_last()}\n\n"
        for index, msg in enumerate(self.sessions):
            string += f"<code>{msg}</code>"
            string += "\n\n" if index != len(self.sessions) - 1 else ""
        return string

    def equal(self, other):
        if not isinstance(other, UpdateMessage):
            raise TypeError(f"Other must be {UpdateMessage}")
        return self.tuple == other.tuple

    @property
    def tuple(self):
        return self.subject, [session.tuple for session in self.sessions]

    @classmethod
    def get_last_by_subject(cls, subject):
        return cls.objects(subject=subject).order_by('-datetime').first()

    @classmethod
    def from_data(cls, subject, msg):
        json_data = loads(msg)
        instance = cls(subject=subject)
        for data in json_data:
            instance.sessions.append(
                Session.from_data(data)
            )

        last_update = cls.get_last_by_subject(subject)
        if last_update and instance.equal(last_update):
            raise DuplicatedUpdateMessageError(f"{instance} == {last_update}")

        instance.save()
        return instance

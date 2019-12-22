from json import loads

import pendulum
from mongoengine import (
    Document, EmbeddedDocument,
    IntField, StringField, DateTimeField,
    EmbeddedDocumentListField, ReferenceField)

from db.subject import Subject


class Amount(EmbeddedDocument):
    ATOM_DECIMALS = 100000000

    _value = IntField(required=True)

    def __str__(self):
        return f"{self.value} DCR"

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

    @classmethod
    def from_data(cls, data):
        instance = cls(data.get('name'))
        for amount in data.get('amounts'):
            instance.amounts.append(Amount(amount))
        return instance


class UpdateMessage(Document):
    subject = ReferenceField(Subject, required=True)
    sessions = EmbeddedDocumentListField(Session, required=True)
    datetime = DateTimeField(default=pendulum.now, required=True)

    def __str__(self):
        string = f"<b>{self.subject.header}</b>\n"
        string += f"<i>default session: {self.subject.default_session}</i>\n\n"
        for index, msg in enumerate(self.sessions):
            string += f"<code>{msg}</code>"
            string += "\n\n" if index != len(self.sessions) - 1 else ""
        return string

    @classmethod
    def from_data(cls, subject, msg):
        json_data = loads(msg)
        instance = cls(subject=subject)
        for data in json_data:
            instance.sessions.append(
                Session.from_data(data)
            )
        instance.save()
        return instance

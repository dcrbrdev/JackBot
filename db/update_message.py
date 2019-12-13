from json import loads

import pendulum
from mongoengine import (
    Document, EmbeddedDocument,
    IntField, StringField, DateTimeField,
    EmbeddedDocumentListField, ReferenceField)

from db.subject import Subject


class Amount(EmbeddedDocument):
    """MongoDB EmbeddedDocument for some amount value in ATOM

    Attributes:
        _value (int): atom value
    """
    ATOM_DECIMALS = 100000000

    _value = IntField(required=True)

    def __str__(self):
        return f"{self.value} DCR"

    @property
    def value(self):
        """Value get property method

        Returns:
            float: the value of amount in DCR

        Args:
            value: desired value

        Raises:
            TypeError: if value is not int
        """
        return self._value/self.ATOM_DECIMALS

    @value.setter
    def value(self, value: int):
        if not isinstance(value, int):
            raise TypeError(f"{value} {type(value)} is not int")
        self._value = value


class Session(EmbeddedDocument):
    """MongoDB EmbeddedDocument for a session data

    Attributes:
        hash (str): session id
        amounts (list of Amount): list of Amount's in session
    """
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
        """Create a session from a data

        Examples:
            >>> session = Session.from_data({'name': 'some_hash', 'amounts': [1000000000, 200000000]})

        Args:
            data: data to create a Session and it's respective Amount's

        Returns:
            Session: Session created
        """
        instance = cls(data.get('name'))
        for amount in data.get('amounts'):
            instance.amounts.append(Amount(amount))
        return instance


class UpdateMessage(Document):
    """MongoDB Document for a update message

    Attributes:
        subject (Subject): subject of this update message
        sessions (list of Session): list of sessions
        datetime: now() datetime
    """
    subject = ReferenceField(Subject, required=True)
    sessions = EmbeddedDocumentListField(Session, required=True)
    datetime = DateTimeField(default=pendulum.now, required=True)

    def __str__(self):
        string = f"<b>{self.subject.header}</b>\n\n"
        for index, msg in enumerate(self.sessions):
            string += f"<code>{msg}</code>"
            string += "\n\n" if index != len(self.sessions) - 1 else ""
        return string

    @classmethod
    def from_data(cls, subject, msg):
        """Create a update message from a data

        Examples:
            >>> subject = Subject()
            >>> update_message = UpdateMessage.from_data(subject, [{'name': 'some_hash', 'amounts': [1000000000, 200000000]}])

        Args:
            msg: msg received from websocket to create a UpdateMessage and it's respective Session's
            subject Subject: Subject for UpdateMessage

        Returns:
            UpdateMessage: UpdateMessage created
        """
        json_data = loads(msg)
        instance = cls(subject=subject)
        for data in json_data:
            instance.sessions.append(
                Session.from_data(data)
            )
        instance.save()
        return instance

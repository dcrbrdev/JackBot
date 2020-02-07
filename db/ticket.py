import logging
from threading import Lock

import pendulum
from mongoengine import (
    Document, ReferenceField,
    FloatField, DateTimeField, StringField)

from db.observer import Observer
from utils.dcrdata import request_dcr_data
from utils.exceptions import DcrDataAPIError


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)


class TicketPrice(Document):
    lock = Lock()
    endpoint = "stake/diff"

    price = FloatField(required=True)
    datetime = DateTimeField(default=pendulum.now, required=True)

    meta = {
        'ordering': ['datetime'],
        'indexes': [
            {'fields': ['datetime'], 'expireAfterSeconds': 7*24*60*60}
        ]
    }

    def __str__(self):
        return f"{self.price:.2f} DCR"

    @property
    def pendulum_datetime(self):
        return pendulum.instance(self.datetime).in_tz('America/Sao_Paulo')

    def is_past_expire(self):
        now = pendulum.now()
        last = self.pendulum_datetime
        diff = now - last
        return diff.in_seconds() >= 2*60*60

    @classmethod
    def _fetch_new_ticket_price(cls):
        price = request_dcr_data(cls.endpoint)
        price = price.get('current')
        return cls(price)

    @classmethod
    def get_last(cls):
        cls.lock.acquire()
        last_ticket_price = cls.objects.order_by('-datetime').first()

        try:
            if last_ticket_price.is_past_expire():
                last_ticket_price = cls._fetch_new_ticket_price()
        except AttributeError:
            last_ticket_price = cls._fetch_new_ticket_price()
        finally:
            last_ticket_price.save()
            if cls.lock.locked():
                cls.lock.release()

        return last_ticket_price


class Status(Document):
    name = StringField(max_length=8, unique=True)

    def __eq__(self, other):
        name = None

        if isinstance(other, Status):
            name = other.name
        elif isinstance(other, str):
            name = other
        return self.name == name

    def __str__(self):
        return self.name

    @classmethod
    def immature(cls):
        return cls.objects.get(name='immature')

    @classmethod
    def live(cls):
        return cls.objects.get(name='live')

    @classmethod
    def voted(cls):
        return cls.objects.get(name='voted')


class Ticket(Document):
    observer = ReferenceField(Observer, unique_with='tx_id')
    tx_id = StringField(max_length=64, required=True)
    _status = ReferenceField(Status)
    vote_id = StringField(max_length=64)

    def __str__(self):
        message = f"tx {self.tx_id}\n" \
                  f"status: {self.status}"
        if self.vote_id:
            message += f"\nvote: {self.vote_id}"
        return message

    @property
    def html(self):
        message = f"<b>tx</b>: {self.tx_link}\n" \
                  f"<b>status</b>: {self.status}"
        if self.vote_id:
            message += f"\n<b>vote</b>: {self.vote_link}"
        return message

    def is_same_status(self, new_status_name):
        return self.status == new_status_name

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, new_status_name):
        self._status = Status.objects.get(name=new_status_name)

    @property
    def tx_link(self):
        return f"<a href='https://dcrdata.decred.org/tx/" \
               f"{self.tx_id}'>{self.tx_id}</a>"

    @property
    def vote_link(self):
        return f"<a href='https://dcrdata.decred.org/tx/" \
               f"{self.vote_id}'>{self.vote_id}</a>"

    def notify(self):
        self.observer.send_message(self.html)

    def fetch(self):
        logger.debug(f"fetching ticket {self}")
        try:
            data = request_dcr_data(f"tx/{self.tx_id}/tinfo")
        except DcrDataAPIError as e:
            self.delete()
            self.observer.send_message(e)
            self.observer.send_message(f"Your ticket was removed!")
            return

        status = data.get('status')

        if self.is_same_status(status):
            return

        self.status = status
        if self.status == Status.voted():
            self.vote_id = data.get('vote')

        self.save()
        self.notify()

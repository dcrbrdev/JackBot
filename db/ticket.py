import logging

import pendulum
from mongoengine import (
    Document,
    FloatField, DateTimeField)

from utils.dcrdata import request_dcr_data


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)


class TicketPrice(Document):
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
        last_ticket_price = cls.objects.order_by('-datetime').first()

        try:
            if last_ticket_price.is_past_expire():
                last_ticket_price = cls._fetch_new_ticket_price()
        except AttributeError:
            last_ticket_price = cls._fetch_new_ticket_price()
        finally:
            last_ticket_price.save()

        return last_ticket_price

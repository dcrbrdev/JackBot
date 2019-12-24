from unittest import TestCase, mock

import pendulum
import pytest

from tests.fixtures import mongo  # noqa F401
from db.ticket import TicketPrice


@pytest.mark.usefixtures('mongo')
class TicketPriceTestCase(TestCase):
    def test_create(self):
        self.assertEqual(TicketPrice.objects.count(), 0)

        instance = TicketPrice(150.5).save()
        self.assertEqual(TicketPrice.objects.count(), 1)

        self.assertEqual(instance.price, 150.5)
        self.assertTrue(instance.datetime)

    def test_is_past_expire(self):
        self.assertEqual(TicketPrice.objects.count(), 0)
        TicketPrice(150.5).save()
        self.assertEqual(TicketPrice.objects.count(), 1)

        instance = TicketPrice.objects.first()

        self.assertFalse(instance.is_past_expire())

        instance.datetime = pendulum.yesterday()
        self.assertTrue(instance.is_past_expire())

    @mock.patch('db.ticket.request_dcr_data')
    def test_fetch_new_ticket_price(self, mocked_request_dcr_data):
        self.assertIsInstance(mocked_request_dcr_data, mock.MagicMock)
        mocked_request_dcr_data.return_value = mock.MagicMock(
            get=mock.MagicMock(
                return_value=150.5
            )
        )

        instance = TicketPrice._fetch_new_ticket_price()
        self.assertEqual(instance.price, 150.5)
        self.assertTrue(instance.datetime)

    @mock.patch('db.ticket.request_dcr_data')
    def test_get_last_price_exception(self, mocked_request_dcr_data):
        self.assertIsInstance(mocked_request_dcr_data, mock.MagicMock)
        mocked_request_dcr_data.return_value = mock.MagicMock(
            get=mock.MagicMock(
                return_value=150.5
            )
        )

        self.assertEqual(TicketPrice.objects.count(), 0)

        instance = TicketPrice.get_last()
        self.assertEqual(TicketPrice.objects.count(), 1)
        self.assertEqual(instance.price, 150.5)
        self.assertTrue(instance.datetime)

    def test_get_last_price_existing(self):
        TicketPrice(130).save()

        self.assertEqual(TicketPrice.objects.count(), 1)

        instance = TicketPrice.get_last()
        self.assertEqual(TicketPrice.objects.count(), 1)
        self.assertEqual(instance.price, 130)
        self.assertTrue(instance.datetime)

    @mock.patch('db.ticket.request_dcr_data')
    def test_get_last_price_existing_expired(self, mocked_request_dcr_data):
        self.assertIsInstance(mocked_request_dcr_data, mock.MagicMock)
        mocked_request_dcr_data.return_value = mock.MagicMock(
            get=mock.MagicMock(
                return_value=150.5
            )
        )

        TicketPrice(130, pendulum.yesterday()).save()
        self.assertEqual(TicketPrice.objects.count(), 1)

        instance = TicketPrice.get_last()
        self.assertEqual(TicketPrice.objects.count(), 2)
        self.assertEqual(instance.price, 150.5)
        self.assertTrue(instance.datetime)

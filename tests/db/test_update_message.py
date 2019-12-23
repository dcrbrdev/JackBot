from unittest import TestCase

import pytest

from tests.fixtures import mongo  # noqa F401
from db.update_message import UpdateMessage, Session, Amount
from db.subject import Subject
from db.exceptions import DuplicatedUpdateMessageError


DATA = '[{"name":"c17b1828e97bf66abd5329e7' \
       '3755173b43b98e18ebd4b84b19a016781d8cfa86",' \
       '"amounts":[1000000000,2000000000]}]\n'

DATA2 = '[{"name":"c17b1828e97bf66abd5329e7' \
       '3755173b43b98e18ebd4b84b19a016781d8cfa86",' \
       '"amounts":[1000000000,2000000000,500000000]}]\n'


@pytest.mark.usefixtures('mongo')
class UpdateMessageTestCase(TestCase):
    def setUp(self) -> None:
        self.subject = Subject("🇧🇷", "Decred Brasil",
                               "wss://split-ticket-svc.stake.decredbrasil"
                               ".com:8477/watchWaitingList",
                               "dcrbr1").save()

    def test_init(self):
        self.assertEqual(UpdateMessage.objects.count(), 0)

        UpdateMessage(self.subject, [Session('test', [Amount(10)])]).save()
        self.assertEqual(UpdateMessage.objects.count(), 1)

        instance = UpdateMessage.objects.first()
        self.assertEqual(instance.subject, self.subject)
        self.assertIsInstance(instance, UpdateMessage)

    def test_equal(self):
        instance = UpdateMessage(self.subject, [Session('test', [Amount(10)])])
        other = UpdateMessage(self.subject, [Session('test', [Amount(10)])])

        self.assertTrue(instance.equal(other))

    def test_equal_false(self):
        instance = UpdateMessage(self.subject, [Session('test', [Amount(10)])])
        other = UpdateMessage(self.subject, [Session('test', [Amount(11)])])

        self.assertFalse(instance.equal(other))

    def test_get_last_by_subject(self):
        UpdateMessage(self.subject, [Session('test', [Amount(10)])]).save()
        other = UpdateMessage(self.subject,
                              [Session('test', [Amount(11)])]).save()

        last = UpdateMessage.get_last_by_subject(self.subject)
        self.assertEqual(other, last)

    def test_from_sessions(self):
        UpdateMessage.from_data(self.subject, DATA)
        instance = UpdateMessage.objects.first()
        self.assertEqual(instance.subject, self.subject)
        self.assertEqual(len(instance.sessions), 1)

        session = instance.sessions[0]
        self.assertIsInstance(session, Session)
        self.assertEqual(session.hash,
                         'c17b1828e97bf66abd5329e737551'
                         '73b43b98e18ebd4b84b19a016781d8cfa86')
        self.assertEqual(len(session.amounts), 2)
        self.assertIsInstance(session.amounts[0], Amount)
        self.assertIsInstance(session.amounts[1], Amount)
        self.assertEqual(session.amounts[0].value, 10.0)
        self.assertEqual(session.amounts[1].value, 20.0)

    def test_from_sessions_duplicated(self):
        self.assertEqual(UpdateMessage.objects.count(), 0)
        UpdateMessage.from_data(self.subject, DATA)
        self.assertEqual(UpdateMessage.objects.count(), 1)
        self.assertRaises(DuplicatedUpdateMessageError,
                          UpdateMessage.from_data, self.subject, DATA)
        self.assertEqual(UpdateMessage.objects.count(), 1)

    def test_from_sessions_2(self):
        self.assertEqual(UpdateMessage.objects.count(), 0)
        UpdateMessage.from_data(self.subject, DATA)
        self.assertEqual(UpdateMessage.objects.count(), 1)
        self.assertRaises(DuplicatedUpdateMessageError,
                          UpdateMessage.from_data, self.subject, DATA)
        self.assertEqual(UpdateMessage.objects.count(), 1)
        UpdateMessage.from_data(self.subject, DATA2)
        self.assertEqual(UpdateMessage.objects.count(), 2)
        UpdateMessage.from_data(self.subject, DATA)
        self.assertEqual(UpdateMessage.objects.count(), 3)

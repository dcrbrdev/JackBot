from unittest import TestCase

import pytest

from tests.fixtures import mongo  # noqa F401
from db.message import UpdateMessage, Session, Amount
from db.subject import Subject


DATA = '[{"name":"c17b1828e97bf66abd5329e7' \
       '3755173b43b98e18ebd4b84b19a016781d8cfa86",' \
       '"amounts":[1000000000,2000000000]}]\n'


@pytest.mark.usefixtures('mongo')
class UpdateMessageTestCase(TestCase):
    def setUp(self) -> None:
        self.subject = Subject("🇧🇷", "Decred Brasil",
                               "wss://split-ticket-svc.stake.decredbrasil"
                               ".com:8477/watchWaitingList").save()

    def test_init(self):
        UpdateMessage(self.subject, [Session('test', [Amount(10)])]).save()
        instance = UpdateMessage.objects.first()
        self.assertEqual(instance.subject, self.subject)
        self.assertIsInstance(instance, UpdateMessage)

    def test_fromsessions(self):
        data = DATA
        UpdateMessage.from_data(self.subject, data)
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

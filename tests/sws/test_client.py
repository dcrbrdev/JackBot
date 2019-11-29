from unittest import TestCase

import pytest
from websocket import WebSocketApp

from tests.fixtures import mongo  # noqa F401
from db.subscription import Subject
from sws.client import SessionWebSocket
from sws.exceptions import SessionWebSocketNotFoundError


@pytest.mark.usefixtures('mongo')
class SessionWebSocketTestCase(TestCase):
    def tearDown(self):
        SessionWebSocket.sessions = {}

    def test_create(self):
        subject = Subject(
            emoji="🇧🇷", name="Decred Brasil",
            url="wss://split-ticket-svc.stake.decredbrasil.com:8477/watchWaitingList").save()
        sws = SessionWebSocket(subject)

        self.assertEqual(len(SessionWebSocket.sessions), 1)

        self.assertEqual(sws.subject, subject)
        self.assertIsNone(sws.ws)
        self.assertFalse(sws.ignore_next_update)

        self.assertEqual(sws.url, subject.url)
        self.assertEqual(sws.name, subject.name)
        self.assertEqual(sws.header, subject.header)
        self.assertEqual(sws.__str__(), subject.__str__())

    def test_set_ws(self):
        subject = Subject(
            emoji="🇧🇷", name="Decred Brasil",
            url="wss://split-ticket-svc.stake.decredbrasil.com:8477/watchWaitingList").save()
        sws = SessionWebSocket(subject)

        self.assertIsNone(sws.ws)
        sws.set_ws()

        self.assertIsInstance(sws.ws, WebSocketApp)
        self.assertEqual(sws.ws.url, subject.url)

    def test_get_sws(self):
        subject = Subject(
            emoji="🇧🇷", name="Decred Brasil",
            url="wss://split-ticket-svc.stake.decredbrasil.com:8477/watchWaitingList").save()
        SessionWebSocket(subject)

        self.assertEqual(len(SessionWebSocket.sessions), 1)

        sws = SessionWebSocket.get_sws("wss://split-ticket-svc.stake.decredbrasil.com:8477/watchWaitingList")
        self.assertIsInstance(sws, SessionWebSocket)

        self.assertRaises(SessionWebSocketNotFoundError, SessionWebSocket.get_sws, "url_teste")

    def test_create_all(self):
        Subject(
            emoji="🇧🇷", name="Decred Brasil",
            url="wss://split-ticket-svc.stake.decredbrasil.com:8477/watchWaitingList").save()
        Subject(
            emoji="🇺🇸", name="Decred Voting",
            url="wss://matcher.decredvoting.com:8477/watchWaitingList").save()

        self.assertEqual(len(SessionWebSocket.sessions), 0)

        SessionWebSocket.create_all()

        self.assertEqual(len(SessionWebSocket.sessions), 2)

        sws = SessionWebSocket.get_sws("wss://split-ticket-svc.stake.decredbrasil.com:8477/watchWaitingList")
        self.assertIsNone(sws.ws)
        self.assertFalse(sws.ignore_next_update)

        self.assertEqual(sws.url, "wss://split-ticket-svc.stake.decredbrasil.com:8477/watchWaitingList")
        self.assertEqual(sws.name, "Decred Brasil")
        self.assertEqual(sws.header, "🇧🇷 Decred Brasil")

        sws = SessionWebSocket.get_sws("wss://matcher.decredvoting.com:8477/watchWaitingList")
        self.assertIsNone(sws.ws)
        self.assertFalse(sws.ignore_next_update)

        self.assertEqual(sws.url, "wss://matcher.decredvoting.com:8477/watchWaitingList")
        self.assertEqual(sws.name, "Decred Voting")
        self.assertEqual(sws.header, "🇺🇸 Decred Voting")

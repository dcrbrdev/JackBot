from unittest import TestCase

import pytest
from websocket import WebSocketApp

from tests.fixtures import mongo  # noqa F401
from db.subject import Subject
from sws.client import SessionWebSocket
from sws.exceptions import SessionWebSocketNotFoundError


@pytest.mark.usefixtures('mongo')
class SessionWebSocketTestCase(TestCase):
    def setUp(self) -> None:
        self.brasil = Subject("🇧🇷", "Decred Brasil",
                              "wss://split-ticket-svc.stake.decredbrasil"
                              ".com:8477/watchWaitingList").save()
        self.voting = Subject("🇺🇸", "Decred Voting",
                              "wss://matcher.decredvoting.com:8477/"
                              "watchWaitingList").save()

    def tearDown(self):
        SessionWebSocket.sessions = {}

    def test_create(self):
        sws = SessionWebSocket(self.brasil)

        self.assertEqual(len(SessionWebSocket.sessions), 1)

        self.assertEqual(sws.subject, self.brasil)
        self.assertIsNone(sws.ws)
        self.assertFalse(sws.ignore_next_update)

        self.assertEqual(sws.url, self.brasil.url)
        self.assertEqual(sws.name, self.brasil.name)
        self.assertEqual(sws.header, self.brasil.header)
        self.assertEqual(sws.__str__(), self.brasil.__str__())

    def test_set_ws(self):
        sws = SessionWebSocket(self.brasil)

        self.assertIsNone(sws.ws)
        sws.set_ws()

        self.assertIsInstance(sws.ws, WebSocketApp)
        self.assertEqual(sws.ws.url, self.brasil.url)

    def test_get_sws(self):
        SessionWebSocket(self.brasil)

        self.assertEqual(len(SessionWebSocket.sessions), 1)

        sws = SessionWebSocket.get_sws("wss://split-ticket-svc.stake."
                                       "decredbrasil.com:8477/watchWaitingList")
        self.assertIsInstance(sws, SessionWebSocket)

        self.assertRaises(SessionWebSocketNotFoundError,
                          SessionWebSocket.get_sws, "url_teste")

    def test_create_all(self):
        self.assertEqual(len(SessionWebSocket.sessions), 0)

        SessionWebSocket.create_all()

        self.assertEqual(len(SessionWebSocket.sessions), 2)

        sws = SessionWebSocket.get_sws("wss://split-ticket-svc.stake."
                                       "decredbrasil.com:8477/watchWaitingList")
        self.assertIsNone(sws.ws)
        self.assertFalse(sws.ignore_next_update)

        self.assertEqual(sws.url, "wss://split-ticket-svc.stake.decredbrasil"
                                  ".com:8477/watchWaitingList")
        self.assertEqual(sws.name, "Decred Brasil")
        self.assertEqual(sws.header, "🇧🇷 Decred Brasil")

        sws = SessionWebSocket.get_sws("wss://matcher.decredvoting"
                                       ".com:8477/watchWaitingList")
        self.assertIsNone(sws.ws)
        self.assertFalse(sws.ignore_next_update)

        self.assertEqual(sws.url, "wss://matcher.decredvoting.com:"
                                  "8477/watchWaitingList")
        self.assertEqual(sws.name, "Decred Voting")
        self.assertEqual(sws.header, "🇺🇸 Decred Voting")
